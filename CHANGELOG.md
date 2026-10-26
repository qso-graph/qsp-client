# Changelog

All notable changes to `qsp-client` (formerly `qsp-mcp`) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Python 3.11 is the minimum.** 3.10 reached end of life in October 2026
  ([PEP 619](https://peps.python.org/pep-0619/)), so it gets no further security
  releases on any platform. On Windows it was worse than unsupported: `uv`'s 3.10
  is built against OpenSSL 1.1.1w, end of life since September 2023, so HTTPS
  from this server ran over an unmaintained TLS library. `certifi` does not help
  with that — it supplies the root store, not the implementation.

  3.10 support was already nominal. This package has linted with
  `ruff target-version = "py311"` and type-checked with `mypy python_version =
  "3.11"` for some time, so nothing ever verified the 3.10 claim.

  `uv.lock` is regenerated and the diff is large, but **nothing is upgraded** —
  it is the 3.10 resolution branch disappearing. Packages that carried two pins,
  one per Python branch, now carry the single 3.11+ pin they already resolved to.
  An install on 3.11 or later is unchanged.

## [0.4.1] — 2026-10-26

### Security

- `certifi` in `uv.lock` moved from 2026.7.22 to 2026.10.23, clearing a CRITICAL
  advisory (GHSA-6q48-6c7w-9gw2). Nobody installing from PyPI was exposed:
  `certifi` arrives transitively through `httpx` with an open range and `uv.lock`
  is not in the wheel, so a fresh install always resolved a current `certifi`.
  What was exposed is anything running from this repository with
  `uv sync --frozen`, which includes this repository's own CI.
- `opentelemetry-api` moved from 1.45.0 to 1.45.1, clearing CVE-2026-114603.
  Found by the new audit job below, not by Dependabot, which had not reported it:
  `pip-audit` reads the lockfile against an advisory database, and that is a
  different question from the one Dependabot's alert list answers.

### Changed

- **A release is now a deliberate act, not a side effect of merging.**
  `publish.yml` fires on `workflow_dispatch` with the version typed in, and
  merging into `main` publishes nothing. This was the last repository still on
  the `develop` → `main` → publish-on-merge flow that the 22 MCP servers left on
  2026-10-25; its `develop` was five commits *behind* `main`, so that branch had
  already stopped being where work landed. `develop` is gone.
- CI audits the locked dependencies, per pull request and weekly. Its absence is
  why the `certifi` advisory above sat unnoticed: nothing read `uv.lock` against
  an advisory database. The weekly run matters because an advisory is published
  against a lockfile that has not changed, and no push or pull request fires then.
- The one-off `deprecate-qsp-mcp` job is removed. The MCP Registry already
  reports `io.github.qso-graph/qsp-mcp` 0.1.1 as `status=deprecated`, so it is
  spent.

## [0.4.0] — 2026-10-12

- **ADIF tools moved here from `adif-mcp`**, which is now only the MCP server and ADIF's published
  resources. `qsp-adif-convert` converts an ADIF (`.adi`) log to JSON or NDJSON (it was
  `adif-mcp convert`); `qsp_client.adif.reader` reads `.adi` text and `qsp_client.adif.models`
  holds the QSO and entity models. They came with their tests. Nothing in the relay uses them.
- **`qsp-adif-convert` never drops a record silently** (#24). A record it cannot convert used to
  vanish unless `--errors` was given, and the run still exited 0, so a log with no station
  callsign converted to `[]` and looked like success. It now always reports how many records
  failed and why on stderr, says to use `--station-call` when that is the reason, and exits 1.

## [0.3.5] — 2026-10-11

- **ruff and mypy run in CI** (qso-graph-devel#66), as a job the `ci-all-green` gate requires. This
  repo sat outside that rollout; it is in the MCP ecosystem and answers to the same rules as the
  servers. Settings follow `adif-mcp`, as everywhere else, and both run once rather than per Python
  version: they read the source, and neither answer changes with the interpreter.
- `_discover_tools` builds rows of `(server, namespaced name, tool)`, which is what
  `mcp_to_openai_tools(namespace=True)` documents and reads, but the list was annotated as holding
  two-tuples. Nothing produced or consumed that shape; the annotation was simply wrong.
- `BridgeConfig` was imported into `relay.py` and never used, and two functions promised a `dict`
  and a `str` while returning whatever the JSON body held.
- `E501` is deferred rather than adopted (qso-graph-devel#70): what it reports in these repos are
  widths, not defects.

## [0.3.4] — 2026-10-11

- **The published contact is `maintainers@qso-graph.io`** (qso-graph-devel#69). The `authors` field
  carried a personal address, and that field is what PyPI shows on the package page. The project
  has had outside contributions; a project address is the fitting route for them.

## [0.3.3] — 2026-10-07

- Licence: GPL-3.0-or-later, as the LICENSE file already said. The package metadata and README said MIT; released versions up to 0.3.2 keep the MIT terms they were published with.

## [0.3.2] — 2026-10-06

- PyPI: the Documentation link goes to this package's own page, https://qso-graph.io/servers/qsp-client/ (qso-graph/.github#15).
- CI: the release flow (qso-graph/.github TEMPLATES.md). Work lands on `develop`; a release is a
  PR from `develop` into `main`, and merging it publishes to PyPI and the MCP Registry, verifies both
  and tags the release. CI runs on `develop` too, and PRs into `main` must come from `develop` or a
  `security/` branch.

## [0.3.1] — 2026-10-06

### Fixed

- **Tool names are always valid function names** (#8). When servers share a tool name (every
  qso-graph server has `get_version_info`), the copies are namespaced as `server__tool`, which
  0.3.0 already did. The server part comes from your config, though, so a name like `my solar` or
  `9975.wspr` could produce a function name that OpenAI or Gemini rejects, and so could a tool's
  own name (`get version`, `solar.wind`), which comes from a third-party server. **Every** exposed
  name is now cleaned to `[A-Za-z0-9_-]`, starts with a letter or underscore, fits in 64
  characters, and stays unique even when two names clean to the same text; each still calls its
  server under its original name. Tests cover the namespacing, shared and unshared names, and the
  64-character limit with suffixes.

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
