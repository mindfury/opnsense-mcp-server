from opnsense_mcp.errors import OPNsenseAPIError, ToolError


class TestOPNsenseAPIError:
    def test_construction(self) -> None:
        err = OPNsenseAPIError(
            status_code=401,
            body={"message": "Unauthorized"},
            path="core/dashboard/get",
            method="GET",
        )
        assert err.status_code == 401
        assert err.body == {"message": "Unauthorized"}
        assert err.path == "core/dashboard/get"
        assert err.method == "GET"

    def test_is_exception(self) -> None:
        err = OPNsenseAPIError(
            status_code=500, body={}, path="core/dashboard/get", method="GET"
        )
        assert isinstance(err, Exception)

    def test_str_includes_status_code(self) -> None:
        err = OPNsenseAPIError(
            status_code=404,
            body={},
            path="firmware/status/check",
            method="GET",
        )
        assert "404" in str(err)

    def test_str_includes_path(self) -> None:
        err = OPNsenseAPIError(
            status_code=404,
            body={},
            path="firmware/status/check",
            method="GET",
        )
        assert "firmware/status/check" in str(err)

    def test_can_be_raised_and_caught(self) -> None:
        import pytest

        with pytest.raises(OPNsenseAPIError) as exc_info:
            raise OPNsenseAPIError(
                status_code=503,
                body={"error": "unavailable"},
                path="test",
                method="GET",
            )
        assert exc_info.value.status_code == 503


class TestToolError:
    def test_is_exception(self) -> None:
        err = ToolError("connection timed out")
        assert isinstance(err, Exception)

    def test_str_returns_message(self) -> None:
        err = ToolError("connect timeout exceeded for core/dashboard/get")
        assert "connect timeout" in str(err).lower()

    def test_from_api_error_contains_status_code(self) -> None:
        api_err = OPNsenseAPIError(
            status_code=403,
            body={"message": "Forbidden"},
            path="firewall/filter/add_rule",
            method="POST",
        )
        msg = ToolError.from_api_error(api_err)
        assert "403" in str(msg)

    def test_from_api_error_contains_path(self) -> None:
        api_err = OPNsenseAPIError(
            status_code=403,
            body={"message": "Forbidden"},
            path="firewall/filter/add_rule",
            method="POST",
        )
        msg = ToolError.from_api_error(api_err)
        assert "firewall/filter/add_rule" in str(msg)

    def test_from_api_error_contains_body(self) -> None:
        api_err = OPNsenseAPIError(
            status_code=400,
            body={"message": "Validation failed"},
            path="routes/routes/addroute",
            method="POST",
        )
        msg = ToolError.from_api_error(api_err)
        assert "Validation failed" in str(msg)

    def test_from_api_error_returns_tool_error(self) -> None:
        api_err = OPNsenseAPIError(status_code=500, body={}, path="test", method="GET")
        result = ToolError.from_api_error(api_err)
        assert isinstance(result, ToolError)
