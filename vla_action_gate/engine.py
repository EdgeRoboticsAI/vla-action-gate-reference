from copy import deepcopy

from .models import Decision, GateDecision


def validate_action(command: dict, context: dict) -> Decision:
    """
    Validate a proposed VLA robot action command against robot state,
    environment context, and policy constraints.

    This is a reference implementation only. It is not safety-certified and
    is not a production actuator-enforcement system.
    """
    action_id = command.get("action_id", "unknown-action")
    action_type = command.get("action_type")

    robot_state = context.get("robot_state", {})
    environment = context.get("environment", {})
    policy = context.get("policy", {})

    if robot_state.get("emergency_stop", False):
        return Decision(
            GateDecision.DENY,
            "emergency stop is active",
            action_id,
        )

    denied_actions = policy.get("denied_actions", [])
    if action_type in denied_actions:
        return Decision(
            GateDecision.DENY,
            f"action type {action_type} is denied",
            action_id,
        )

    allowed_actions = policy.get("allowed_actions", [])
    if allowed_actions and action_type not in allowed_actions:
        return Decision(
            GateDecision.DENY,
            f"action type {action_type} is not allowed",
            action_id,
        )

    battery = robot_state.get("battery_percent")
    min_battery = policy.get("min_battery_percent")
    if battery is not None and min_battery is not None and battery < min_battery:
        return Decision(
            GateDecision.DENY,
            "battery below required threshold",
            action_id,
        )

    human_distance = environment.get("human_distance_m")
    min_human_distance = policy.get("min_human_distance_m")
    if (
        human_distance is not None
        and min_human_distance is not None
        and human_distance < min_human_distance
    ):
        return Decision(
            GateDecision.DENY,
            "human proximity below required threshold",
            action_id,
        )

    limits = command.get("limits", {})
    modified_command = deepcopy(command)
    modified = False

    for field, policy_field in [
        ("max_velocity_mps", "max_velocity_mps"),
        ("max_force_n", "max_force_n"),
        ("max_torque_nm", "max_torque_nm"),
    ]:
        proposed_value = limits.get(field)
        policy_value = policy.get(policy_field)

        if proposed_value is not None and policy_value is not None:
            if proposed_value > policy_value:
                modified_command.setdefault("limits", {})[field] = policy_value
                modified = True

    if modified:
        return Decision(
            GateDecision.MODIFY,
            "command limits reduced to policy maximums",
            action_id,
            modified_command=modified_command,
        )

    return Decision(
        GateDecision.ALLOW,
        "command satisfies reference policy",
        action_id,
    )
