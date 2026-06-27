import httpx
import pytest
import respx

from opnsense_mcp.client import OPNsenseClient
from opnsense_mcp.config import Config
from opnsense_mcp.errors import OPNsenseAPIError, ToolError

BASE = "https://fake.opnsense.example"


class TestClientGet:
    async def test_returns_parsed_dict(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(200, json={"uptime": "1d"})
        )
        async with OPNsenseClient(test_config) as client:
            result = await client.get("core/dashboard/get")
        assert result == {"uptime": "1d"}

    async def test_sends_basic_auth(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        route = respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(200, json={})
        )
        async with OPNsenseClient(test_config) as client:
            await client.get("core/dashboard/get")
        auth = route.calls[0].request.headers.get("authorization", "")
        assert auth.startswith("Basic ")

    async def test_raises_api_error_on_401(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(401, json={"message": "Unauthorized"})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.get("core/dashboard/get")
        assert exc_info.value.status_code == 401

    async def test_raises_api_error_on_403(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/firmware/status/check").mock(
            return_value=httpx.Response(403, json={"message": "Forbidden"})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.get("firmware/status/check")
        assert exc_info.value.status_code == 403

    async def test_raises_api_error_on_404(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/nonexistent").mock(
            return_value=httpx.Response(404, json={})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.get("nonexistent")
        assert exc_info.value.status_code == 404

    async def test_raises_api_error_on_500(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(500, json={"message": "Internal Server Error"})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.get("core/dashboard/get")
        assert exc_info.value.status_code == 500

    async def test_api_error_carries_path_and_method(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(401, json={})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.get("core/dashboard/get")
        err = exc_info.value
        assert "core/dashboard/get" in err.path
        assert err.method == "GET"

    async def test_connect_timeout_raises_tool_error(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        def _timeout(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectTimeout("timed out", request=request)

        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(side_effect=_timeout)
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.get("core/dashboard/get")
        msg = str(exc_info.value).lower()
        assert "connect" in msg or "timeout" in msg

    async def test_read_timeout_raises_tool_error(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        def _timeout(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timed out", request=request)

        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(side_effect=_timeout)
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.get("core/dashboard/get")
        msg = str(exc_info.value).lower()
        assert "read" in msg or "timeout" in msg

    async def test_logs_successful_request(
        self,
        test_config: Config,
        respx_mock: respx.MockRouter,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(200, json={})
        )
        async with OPNsenseClient(test_config) as client:
            await client.get("core/dashboard/get")
        err = capsys.readouterr().err
        assert "GET" in err
        assert "core/dashboard/get" in err
        assert "200" in err
        assert "success" in err

    async def test_logs_failed_request(
        self,
        test_config: Config,
        respx_mock: respx.MockRouter,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/dashboard/get").mock(
            return_value=httpx.Response(401, json={})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError):
                await client.get("core/dashboard/get")
        err = capsys.readouterr().err
        assert "401" in err
        assert "error" in err


class TestClientGetText:
    async def test_returns_raw_string(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        xml_body = '<?xml version="1.0"?><opnsense><version>24.7</version></opnsense>'
        respx_mock.get(f"{BASE}/api/core/backup/download/this").mock(
            return_value=httpx.Response(200, text=xml_body)
        )
        async with OPNsenseClient(test_config) as client:
            result = await client.get_text("core/backup/download/this")
        assert result == xml_body
        assert isinstance(result, str)

    async def test_does_not_parse_as_json(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        xml_body = "<root><item>not json</item></root>"
        respx_mock.get(f"{BASE}/api/core/backup/download/this").mock(
            return_value=httpx.Response(200, text=xml_body)
        )
        async with OPNsenseClient(test_config) as client:
            result = await client.get_text("core/backup/download/this")
        assert result == xml_body

    async def test_raises_api_error_on_non_2xx(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/backup/download/this").mock(
            return_value=httpx.Response(403, json={"message": "Forbidden"})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.get_text("core/backup/download/this")
        assert exc_info.value.status_code == 403

    async def test_logs_request(
        self,
        test_config: Config,
        respx_mock: respx.MockRouter,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        respx_mock.get(f"{BASE}/api/core/backup/download/this").mock(
            return_value=httpx.Response(200, text="<xml/>")
        )
        async with OPNsenseClient(test_config) as client:
            await client.get_text("core/backup/download/this")
        err = capsys.readouterr().err
        assert "GET" in err
        assert "core/backup/download/this" in err
        assert "success" in err


class TestClientPost:
    async def test_returns_parsed_dict(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.post(f"{BASE}/api/firewall/filter/search_rule").mock(
            return_value=httpx.Response(200, json={"rows": [], "total": 0})
        )
        async with OPNsenseClient(test_config) as client:
            result = await client.post(
                "firewall/filter/search_rule", {"current": 1, "rowCount": -1}
            )
        assert result == {"rows": [], "total": 0}

    async def test_sends_json_body(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        route = respx_mock.post(f"{BASE}/api/firewall/filter/add_rule").mock(
            return_value=httpx.Response(
                200, json={"result": "saved", "uuid": "abc-123"}
            )
        )
        async with OPNsenseClient(test_config) as client:
            await client.post("firewall/filter/add_rule", {"rule": {"action": "pass"}})
        body = route.calls[0].request.content
        assert b"action" in body

    async def test_raises_api_error_on_non_2xx(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.post(f"{BASE}/api/firewall/filter/add_rule").mock(
            return_value=httpx.Response(400, json={"message": "Validation error"})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.post("firewall/filter/add_rule", {})
        assert exc_info.value.status_code == 400

    async def test_api_error_carries_method(
        self, test_config: Config, respx_mock: respx.MockRouter
    ) -> None:
        respx_mock.post(f"{BASE}/api/firewall/filter/add_rule").mock(
            return_value=httpx.Response(500, json={})
        )
        async with OPNsenseClient(test_config) as client:
            with pytest.raises(OPNsenseAPIError) as exc_info:
                await client.post("firewall/filter/add_rule", {})
        assert exc_info.value.method == "POST"

    async def test_logs_request(
        self,
        test_config: Config,
        respx_mock: respx.MockRouter,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        respx_mock.post(f"{BASE}/api/firewall/filter/search_rule").mock(
            return_value=httpx.Response(200, json={})
        )
        async with OPNsenseClient(test_config) as client:
            await client.post("firewall/filter/search_rule", {})
        err = capsys.readouterr().err
        assert "POST" in err
        assert "firewall/filter/search_rule" in err
        assert "success" in err
