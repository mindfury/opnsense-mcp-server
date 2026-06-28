from unittest.mock import AsyncMock

import pytest

from opnsense_mcp.errors import OPNsenseAPIError, ToolError
from opnsense_mcp.tools.ids import _ids_ruleset_list


class TestIdsRulesetList:
    async def test_calls_correct_endpoint(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"total": 0, "rowCount": 0, "rows": []}
        await _ids_ruleset_list(mock_client)
        mock_client.get.assert_called_once_with("ids/settings/listRulesets")

    async def test_returns_rows(self, mock_client: AsyncMock) -> None:
        rows = [{"filename": "emerging-scan.rules", "enabled": "1"}]
        mock_client.get.return_value = {"total": 1, "rowCount": 1, "rows": rows}
        result = await _ids_ruleset_list(mock_client)
        assert result["rows"] == rows

    async def test_returns_total(self, mock_client: AsyncMock) -> None:
        mock_client.get.return_value = {"total": 68, "rowCount": 68, "rows": []}
        result = await _ids_ruleset_list(mock_client)
        assert result["total"] == 68

    async def test_api_error_surfaced_as_tool_error(
        self, mock_client: AsyncMock
    ) -> None:
        mock_client.get.side_effect = OPNsenseAPIError(
            status_code=500,
            body={},
            path="ids/settings/listRulesets",
            method="GET",
        )
        with pytest.raises(ToolError) as exc_info:
            await _ids_ruleset_list(mock_client)
        assert "500" in str(exc_info.value)
