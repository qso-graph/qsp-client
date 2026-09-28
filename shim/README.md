# qsp-mcp → qsp-client

**qsp-mcp has been renamed [qsp-client](https://pypi.org/project/qsp-client/).** In the MCP world, `-mcp`
names mark servers, and this is a client.

This package has no code of its own: installing or upgrading `qsp-mcp` installs `qsp-client`. Your config
and the `qsp-mcp` command keep working. New installs:

```bash
pip install qsp-client
```

[github.com/qso-graph/qsp-client](https://github.com/qso-graph/qsp-client)
