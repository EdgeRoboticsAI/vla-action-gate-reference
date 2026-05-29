import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vla_action_gate import validate_action


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    examples_dir = Path(__file__).resolve().parent
    command = load_json(examples_dir / "command_allow.json")
    context = load_json(examples_dir / "context_safe.json")

    decision = validate_action(command, context)
    print(json.dumps(decision.to_dict(), indent=2))


if __name__ == "__main__":
    main()
