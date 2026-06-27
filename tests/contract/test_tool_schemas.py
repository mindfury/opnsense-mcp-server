"""Contract tests: verify each firewall MCP tool has the correct name,
non-empty description, and input schema required fields per contracts/firewall.md."""
from unittest.mock import AsyncMock

import pytest

from mcp.server.fastmcp import FastMCP

from opnsense_mcp.client import OPNsenseClient
from opnsense_mcp.tools import firewall


@pytest.fixture
def firewall_mcp(mock_client: AsyncMock) -> FastMCP:
    mcp = FastMCP("test-firewall")
    firewall.register_tools(mcp, mock_client)
    return mcp


def _tool(mcp: FastMCP, name: str):  # type: ignore[no-untyped-def]
    tools = mcp._tool_manager._tools
    assert name in tools, f"Tool '{name}' not registered"
    return tools[name]


class TestFirewallRuleSchemas:
    def test_rule_list_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_list")
        assert t.name == "firewall_rule_list"
        assert t.description

    def test_rule_list_no_required_params(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_list")
        required = t.parameters.get("required", [])
        assert required == []

    def test_rule_get_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_get")
        assert t.name == "firewall_rule_get"
        assert t.description

    def test_rule_get_requires_uuid(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_get")
        assert "uuid" in t.parameters.get("required", [])

    def test_rule_add_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_add")
        assert t.name == "firewall_rule_add"
        assert t.description

    def test_rule_add_requires_rule(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_add")
        assert "rule" in t.parameters.get("required", [])

    def test_rule_update_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_update")
        assert t.name == "firewall_rule_update"
        assert t.description

    def test_rule_update_requires_uuid_and_rule(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_update")
        required = t.parameters.get("required", [])
        assert "uuid" in required
        assert "rule" in required

    def test_rule_delete_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_delete")
        assert t.name == "firewall_rule_delete"
        assert t.description

    def test_rule_delete_requires_uuid(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_delete")
        assert "uuid" in t.parameters.get("required", [])

    def test_rule_apply_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_apply")
        assert t.name == "firewall_rule_apply"
        assert t.description

    def test_rule_apply_no_required_params(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_rule_apply")
        assert t.parameters.get("required", []) == []


class TestFirewallAliasSchemas:
    def test_alias_list_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_list")
        assert t.name == "firewall_alias_list"
        assert t.description

    def test_alias_get_uuid_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_get_uuid")
        assert t.name == "firewall_alias_get_uuid"
        assert t.description

    def test_alias_get_uuid_requires_name(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_get_uuid")
        assert "name" in t.parameters.get("required", [])

    def test_alias_add_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_add")
        assert t.name == "firewall_alias_add"
        assert t.description

    def test_alias_add_requires_alias(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_add")
        assert "alias" in t.parameters.get("required", [])

    def test_alias_update_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_update")
        assert t.name == "firewall_alias_update"
        assert t.description

    def test_alias_update_requires_uuid_and_alias(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_update")
        required = t.parameters.get("required", [])
        assert "uuid" in required
        assert "alias" in required

    def test_alias_delete_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_delete")
        assert t.name == "firewall_alias_delete"
        assert t.description

    def test_alias_delete_requires_uuid(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_delete")
        assert "uuid" in t.parameters.get("required", [])

    def test_alias_apply_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_alias_apply")
        assert t.name == "firewall_alias_apply"
        assert t.description


class TestFirewallNatSchemas:
    def test_nat_list_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_list")
        assert t.name == "firewall_nat_list"
        assert t.description

    def test_nat_list_no_required_params(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_list")
        assert t.parameters.get("required", []) == []

    def test_nat_add_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_add")
        assert t.name == "firewall_nat_add"
        assert t.description

    def test_nat_add_requires_rule(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_add")
        assert "rule" in t.parameters.get("required", [])

    def test_nat_update_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_update")
        assert t.name == "firewall_nat_update"
        assert t.description

    def test_nat_update_requires_uuid_and_rule(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_update")
        required = t.parameters.get("required", [])
        assert "uuid" in required
        assert "rule" in required

    def test_nat_delete_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_delete")
        assert t.name == "firewall_nat_delete"
        assert t.description

    def test_nat_delete_requires_uuid(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_delete")
        assert "uuid" in t.parameters.get("required", [])

    def test_nat_apply_registered(self, firewall_mcp: FastMCP) -> None:
        t = _tool(firewall_mcp, "firewall_nat_apply")
        assert t.name == "firewall_nat_apply"
        assert t.description
