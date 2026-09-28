<!-- mcp-name: io.github.qso-graph/qsp-client -->
# qsp-client

[![PyPI](https://img.shields.io/pypi/v/qsp-client?label=PyPI&color=blue)](https://pypi.org/project/qsp-client/)
[![MCP Registry](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fregistry.modelcontextprotocol.io%2Fv0%2Fservers%3Fsearch%3Dio.github.qso-graph%2Fqsp-client%26version%3Dlatest&query=%24.servers%5B0%5D.server.version&label=MCP%20Registry&color=blue)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.qso-graph/qsp-client&version=latest)

**QSP** — relay MCP tools to any OpenAI-compatible local LLM endpoint.

Named after the Q-signal **QSP** ("Will you relay?"), qsp-client relays tool calls between a local LLM and [MCP](https://modelcontextprotocol.io/) servers. It is an MCP **client**: any model with function calling gains access to the [qso-graph](https://qso-graph.io) servers' tools, from local weights, not from cloud.

**Formerly `qsp-mcp`.** See [Moving from qsp-mcp](#moving-from-qsp-mcp).

## Install

```bash
pip install qsp-client
```

## Quick Start

```bash
# Interactive mode
qsp-client --config ~/.config/qsp-client/config.json

# Single query
qsp-client --query "What bands are open from DN13 to JN48 right now?"

# Direct endpoint (no config file needed if no MCP servers configured)
qsp-client --endpoint http://localhost:8000/v1/chat/completions --api-key sk-xxx
```

## Configuration

The config format is **Claude Desktop compatible** — copy your existing `mcpServers` block directly:

```json
{
  "mcpServers": {
    "ionis": {
      "command": "ionis-mcp",
      "env": { "IONIS_DATA_DIR": "/path/to/datasets/v1.0" }
    },
    "solar": {
      "command": "solar-mcp"
    },
    "wspr": {
      "command": "wspr-mcp"
    }
  },
  "bridge": {
    "endpoint": "http://localhost:8000/v1/chat/completions",
    "model": "AstroSage-70B",
    "temperature": 0.3,
    "system_prompt": "You are an expert ham radio operator and RF engineer.",
    "max_tool_calls_per_turn": 5,
    "profiles": {
      "contest": {
        "servers": ["n1mm", "ionis", "solar", "wspr"],
        "temperature": 0.2,
        "system_prompt": "You are a contest advisor. Be concise."
      },
      "propagation": {
        "servers": ["ionis", "solar", "wspr"],
        "temperature": 0.3
      },
      "full": {
        "servers": "*",
        "temperature": 0.3
      }
    },
    "server_timeouts": {
      "ionis": 1,
      "solar": 8,
      "qrz": 5
    }
  }
}
```

The `mcpServers` block uses the exact same format as Claude Desktop. The `bridge` section is qsp-client specific (ignored by Claude Desktop).

## CLI Options

```
qsp-client [OPTIONS]

Options:
  -c, --config PATH       Config file path (default: ~/.config/qsp-client/config.json)
  -e, --endpoint URL      LLM endpoint URL (overrides config)
  -k, --api-key KEY       API key for the LLM endpoint
  -m, --model NAME        Model name (overrides config)
  -p, --profile NAME      Tool profile (contest, dx, propagation, full)
  -q, --query TEXT        Single query mode — ask one question and exit
  --enable-writes         Enable write-capable tools (disabled by default)
  --list-tools            List available tools and exit
  --version               Show version
```

## Interactive Commands

| Command | Action |
|---------|--------|
| `/tools` | List available tools |
| `/help` | Show help |
| `quit` | Exit (also: `exit`, `q`, `73`) |

## Design

qsp-client is a **strict, stateless pipe** between an LLM and MCP tools:

- No caching, no shared state, no health polling
- All state lives in MCP servers
- All inference optimization lives in the inference server (prefix caching, KV-cache)
- qsp-client just connects the two sides

Works with any OpenAI-compatible endpoint: [llama.cpp](https://github.com/ggml-org/llama.cpp), [Ollama](https://ollama.ai), [vLLM](https://github.com/vllm-project/vllm), [SGLang](https://github.com/sgl-project/sglang).

## Security

- Write-capable tools disabled by default (`--enable-writes` opt-in)
- Credentials stay inside MCP servers (OS keyring) — never exposed to qsp-client or the LLM
- No subprocess, no shell execution, no eval
- All external connections HTTPS only (LAN endpoints exempted)

## Moving from qsp-mcp

qsp-client is qsp-mcp, renamed: in the MCP world, `-mcp` names mark servers, and this is a client.

- Install the new name: `pip uninstall qsp-mcp && pip install qsp-client`.
- Your config keeps working: `~/.config/qsp-mcp/config.json` and `~/.qsp-mcp.json` are still read, after the new
  `~/.config/qsp-client/config.json` and `~/.qsp-client.json`.
- The `qsp-mcp` command still works, and says it has moved. Use `qsp-client`.

## License

MIT — see [LICENSE](LICENSE).

## Part of the qso-graph ecosystem

[qso-graph.io](https://qso-graph.io) — MCP servers for amateur radio.
