from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from opnsense_mcp.client import OPNsenseClient
from opnsense_mcp.errors import OPNsenseAPIError, ToolError


async def _ids_ruleset_list(client: OPNsenseClient) -> dict[str, Any]:
    try:
        return await client.get("ids/settings/listRulesets")
    except OPNsenseAPIError as exc:
        raise ToolError.from_api_error(exc) from exc


def register_tools(mcp: FastMCP, client: OPNsenseClient) -> None:
    @mcp.tool()
    async def ids_ruleset_list() -> dict[str, Any]:
        """List all available IDS/IPS rulesets and their enabled/disabled status."""
        return await _ids_ruleset_list(client)
