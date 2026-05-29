from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    MODIFY = "MODIFY"


@dataclass
class Decision:
    decision: GateDecision
    reason: str
    action_id: str
    modified_command: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        result = {
            "decision": self.decision.value,
            "reason": self.reason,
            "action_id": self.action_id,
        }
        if self.modified_command is not None:
            result["modified_command"] = self.modified_command
        return result
