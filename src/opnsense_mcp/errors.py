from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OPNsenseAPIError(Exception):
    status_code: int
    body: dict[str, Any]
    path: str
    method: str

    def __str__(self) -> str:
        return f"OPNsense {self.method} {self.path} → {self.status_code}: {self.body}"


class ToolError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

    @classmethod
    def from_api_error(cls, err: OPNsenseAPIError) -> ToolError:
        return cls(
            f"OPNsense API error {err.status_code} on"
            f" {err.method} {err.path}: {err.body}"
        )
