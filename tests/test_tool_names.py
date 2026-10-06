"""Colliding tool names are namespaced, and every name is valid for OpenAI and Gemini (#8)."""

from __future__ import annotations

import asyncio
import re
from types import SimpleNamespace

from qsp_client.relay import QSPRelay
from qsp_client.schema import namespaced_name

VALID = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,63}$")


def tool(name: str) -> SimpleNamespace:
    return SimpleNamespace(name=name, description=f"{name} tool", inputSchema={"type": "object"})


class FakeSession:
    def __init__(self, names: list[str]) -> None:
        self.names = names

    async def list_tools(self):
        return SimpleNamespace(tools=[tool(n) for n in self.names])


def discover(servers: dict[str, list[str]]) -> QSPRelay:
    relay = QSPRelay.__new__(QSPRelay)
    relay._servers = {
        name: SimpleNamespace(name=name, session=FakeSession(tools), tools=[], available=True)
        for name, tools in servers.items()
    }
    relay._tool_server_map = {}
    asyncio.run(relay._discover_tools())
    return relay


def names(relay: QSPRelay) -> list[str]:
    return [t["function"]["name"] for t in relay._openai_tools]


def test_shared_name_is_namespaced_unique_names_are_not():
    relay = discover({"solar": ["get_version_info", "solar_wind"], "wspr": ["get_version_info", "wspr_spots"]})
    assert sorted(names(relay)) == ["solar__get_version_info", "solar_wind", "wspr__get_version_info", "wspr_spots"]
    assert relay._original_tool_name["wspr__get_version_info"] == "get_version_info"
    assert relay._tool_server_map["wspr__get_version_info"] == "wspr"


def test_every_name_is_unique_and_valid_for_openai_and_gemini():
    relay = discover({
        "my solar": ["get_version_info"],
        "9975.wspr": ["get_version_info"],
        "a.b": ["get_version_info"],
        "a_b": ["get_version_info"],
        "x" * 80: ["get_version_info"],
    })
    got = names(relay)
    assert len(got) == len(set(got)) == 5
    assert all(VALID.match(n) for n in got), got


def test_namespaced_name_rules():
    assert namespaced_name("solar", "get_version_info") == "solar__get_version_info"
    assert namespaced_name("9975.wspr", "t") == "_9975_wspr__t"
    long = namespaced_name("s" * 100, "get_version_info")
    assert len(long) == 64 and long.endswith("__get_version_info")
