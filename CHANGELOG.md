# Changelog

All notable changes to `qsp-client` (formerly `qsp-mcp`) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-09-28

### Changed

- **Renamed from qsp-mcp to qsp-client.** In the MCP world, `-mcp` names mark servers, and this is a
  client. The PyPI package, the Python module (`qsp_client`), the command, the repository and the MCP
  Registry entry (`io.github.qso-graph/qsp-client`) all use the new name.
- Config is read from `~/.config/qsp-client/config.json` or `~/.qsp-client.json`, then from the old
  `~/.config/qsp-mcp/config.json` or `~/.qsp-mcp.json`, so existing setups keep working.
- The `qsp-mcp` command still works, and says it has moved.
- The old `qsp-mcp` Registry entry is marked deprecated, pointing to the new one. qsp-mcp on PyPI
  stays at 0.2.2.

### Added (CI hygiene)

- **MCP Registry sync** — `publish.yml` publishes to the [Official MCP Registry](https://registry.modelcontextprotocol.io)
  after each PyPI publish, using GitHub OIDC for auth. Triggered on
  `v*` tag push; no manual steps. The Registry job waits until PyPI
  serves the version, and retries. Pattern documented in
  [qso-graph/.github/TEMPLATES.md](https://github.com/qso-graph/.github/blob/main/TEMPLATES.md).
- **Registry version badge** in README.
- **Release gates** — the tag must match `pyproject.toml`, and a
  `verify` job fails the release unless PyPI and the MCP Registry
  both serve the new version.
- **CI** on pull requests (Python 3.10–3.13).

## [0.2.2] and earlier

Released as qsp-mcp; see the git history.
