"""MCP tool schema → OpenAI tools format translator.

Converts MCP tool definitions into the OpenAI `tools` array format
(not legacy `functions` format) for consumption by any OpenAI-compatible
LLM endpoint.
"""

from __future__ import annotations

import re
from typing import Any


# Function names every target accepts: OpenAI allows [A-Za-z0-9_-]{1,64}; Gemini
# also wants a letter or underscore first. Server names come from the user's
# config, so they are made to fit rather than trusted.
NAME_MAX = 64
_UNSAFE = re.compile(r"[^A-Za-z0-9_-]")


def safe_name(name: str, fallback: str = "tool") -> str:
    """One function name, valid for OpenAI and Gemini: characters outside
    ``[A-Za-z0-9_-]`` become ``_``, it starts with a letter or underscore, and it
    is at most 64 characters. Tool names come from third-party MCP servers, so
    they are cleaned like server names, never trusted."""
    out = _UNSAFE.sub("_", name) or fallback
    if not (out[0].isalpha() or out[0] == "_"):
        out = "_" + out
    return out[:NAME_MAX]


def namespaced_name(server: str, tool: str) -> str:
    """``{server}__{tool}``, valid as a function name for OpenAI and Gemini, cut
    to 64 characters keeping the tool part whole, so two servers' copies of one
    tool stay distinguishable."""
    srv, name = safe_name(server, "server"), _UNSAFE.sub("_", tool) or "tool"
    room = NAME_MAX - len(name) - 2
    if room < 1:
        return (srv[:1] + "__" + name)[:NAME_MAX]
    return f"{srv[:room]}__{name}"


def unique_name(name: str, taken: set[str] | dict[str, str]) -> str:
    """``name``, or ``name_2``, ``name_3``… if it is taken; never over 64 characters."""
    out, n = name, 2
    while out in taken:
        suffix = f"_{n}"
        out = name[: NAME_MAX - len(suffix)] + suffix
        n += 1
    return out


def mcp_to_openai_tools(
    mcp_tools: list[Any],
    *,
    namespace: bool = False,
) -> list[dict[str, Any]]:
    """Convert MCP tool definitions to OpenAI tools array format.

    Args:
        mcp_tools: Either a flat list of MCP tool objects, or (when
            ``namespace=True``) a list of ``(server_name, ns_name, tool)``
            tuples produced by the relay's ``_discover_tools``.
        namespace: If True, expect ``(server, ns_name, tool)`` tuples and
            prepend ``[server]`` to descriptions for LLM disambiguation.

    MCP tool format:
        name: str
        description: str
        inputSchema: dict (JSON Schema)

    OpenAI tools format:
        type: "function"
        function:
            name: str
            description: str
            parameters: dict (JSON Schema)
    """
    openai_tools = []
    for entry in mcp_tools:
        if namespace:
            server, ns_name, tool = entry
        else:
            server = None
            ns_name = None
            tool = entry

        bare_name = tool.name if hasattr(tool, "name") else tool.get("name", "")
        final_name = ns_name if ns_name is not None else bare_name

        description = (
            tool.description
            if hasattr(tool, "description")
            else tool.get("description", "")
        )
        input_schema = (
            tool.inputSchema
            if hasattr(tool, "inputSchema")
            else tool.get("inputSchema", {})
        )

        # Prepend server tag so the LLM can disambiguate colliding names
        if server and ns_name != bare_name:
            description = f"[{server}] {description}"

        # Clean the schema — remove keys that OpenAI doesn't expect
        parameters = _clean_schema(input_schema)

        openai_tools.append(
            {
                "type": "function",
                "function": {
                    "name": final_name,
                    "description": description or "",
                    "parameters": parameters,
                },
            }
        )

    return openai_tools


def _clean_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Clean JSON Schema for OpenAI compatibility.

    Removes fields that OpenAI's API doesn't accept and ensures
    required fields are present.
    """
    if not schema:
        return {"type": "object", "properties": {}}

    cleaned: dict[str, Any] = {}

    # Core schema fields
    cleaned["type"] = schema.get("type", "object")

    if "properties" in schema:
        cleaned["properties"] = {}
        for prop_name, prop_schema in schema["properties"].items():
            cleaned["properties"][prop_name] = _clean_property(prop_schema)

    if "required" in schema:
        cleaned["required"] = schema["required"]

    return cleaned


def _clean_property(prop: dict[str, Any]) -> dict[str, Any]:
    """Clean a single property schema.

    Drops ``default: null`` entries and ensures every property has a ``type``
    so that llama.cpp's JSON‑schema converter doesn't choke on bare
    ``{"default": null}`` objects.
    """
    cleaned: dict[str, Any] = {}

    for key in ("type", "description", "enum", "default", "items"):
        if key in prop:
            # llama.cpp rejects {"default": null} — omit it
            if key == "default" and prop[key] is None:
                continue
            cleaned[key] = prop[key]

    # Guarantee a type — llama.cpp requires it
    if "type" not in cleaned:
        cleaned["type"] = "string"

    return cleaned


def filter_tools_by_profile(
    tools: list[dict[str, Any]],
    tool_server_map: dict[str, str],
    allowed_servers: list[str] | str,
) -> list[dict[str, Any]]:
    """Filter OpenAI tools list to only include tools from allowed servers.

    Args:
        tools: OpenAI-format tools list.
        tool_server_map: Maps tool name → server name.
        allowed_servers: List of server names, or "*" for all.

    Returns:
        Filtered tools list.
    """
    if allowed_servers == "*":
        return tools

    return [
        tool
        for tool in tools
        if tool_server_map.get(tool["function"]["name"]) in allowed_servers
    ]


def filter_write_tools(
    tools: list[dict[str, Any]],
    enable_writes: bool,
) -> list[dict[str, Any]]:
    """Remove write-capable tools unless explicitly enabled.

    Write tools are identified by common naming patterns.
    """
    if enable_writes:
        return tools

    write_patterns = (
        "upload", "send", "post", "delete", "create", "update",
        "write", "modify", "remove", "set_",
    )

    return [
        tool
        for tool in tools
        if not any(
            tool["function"]["name"].lower().startswith(p)
            or f"_{p}" in tool["function"]["name"].lower()
            for p in write_patterns
        )
    ]
