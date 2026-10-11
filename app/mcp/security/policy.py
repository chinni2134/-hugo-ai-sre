from enum import Enum


class ActionMode(str, Enum):
    READ_ONLY = "read_only"
    PROPOSE = "propose"
    APPROVED = "approved"
    EXECUTE = "execute"


class MCPPolicy:
    """
    Central policy boundary for HUGO MCP operations.
    """

    READ_ONLY_TOOLS = {
        "hugo_health",
        "get_systems",
        "get_services",
        "get_topology",
        "get_incidents",
        "get_telemetry",
        "get_dependencies",
        "test_connectivity",
        "get_remediation_actions",
    }

    PROTECTED_TOOLS = {
        "execute_remediation",
        "restart_service",
        "stop_service",
        "start_service",
        "scale_service",
    }

    @classmethod
    def mode_for_tool(cls, tool_name: str) -> ActionMode:
        if tool_name in cls.READ_ONLY_TOOLS:
            return ActionMode.READ_ONLY

        if tool_name in cls.PROTECTED_TOOLS:
            return ActionMode.EXECUTE

        return ActionMode.PROPOSE

    @classmethod
    def is_allowed(cls, tool_name: str, mode: ActionMode) -> bool:
        required_mode = cls.mode_for_tool(tool_name)

        if required_mode == ActionMode.READ_ONLY:
            return True

        return mode in {
            ActionMode.APPROVED,
            ActionMode.EXECUTE,
        }
