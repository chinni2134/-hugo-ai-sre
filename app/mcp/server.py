# pyrefly: ignore [missing-import]
from mcp.server.mcpserver import MCPServer

from app.database.postgres import SessionLocal
from app.models.system import SystemEntity


mcp = MCPServer(
    name="HUGO MCP Server",
    title="HUGO AI Infrastructure Intelligence",
    description=(
        "HUGO's native MCP server for infrastructure "
        "intelligence, observability, incidents, and operations."
    ),
    version="0.1.0",
)


@mcp.tool()
async def get_topology() -> list[dict]:
    """Return the infrastructure topology stored in HUGO's Neo4j graph."""

    from app.database.neo4j import neo4j_connection

    query = """
    MATCH (source:SystemEntity)-[r]->(target:SystemEntity)
    RETURN
        source.entity_id AS source,
        source.name AS source_name,
        type(r) AS relationship_type,
        target.entity_id AS target,
        target.name AS target_name,
        properties(r) AS properties
    ORDER BY source.name, target.name
    """

    with neo4j_connection.driver.session() as session:
        result = session.run(query)

        return [dict(record) for record in result]


@mcp.tool()
async def hugo_health() -> dict:
    """Return the health status of the HUGO platform."""

    return {
        "platform": "HUGO AI",
        "status": "healthy",
        "phase": 2,
        "mcp": "operational",
    }


@mcp.tool()
async def get_systems() -> list[dict]:
    """Return all infrastructure systems discovered by HUGO."""

    db = SessionLocal()

    try:
        systems = (
            db.query(SystemEntity)
            .order_by(SystemEntity.id)
            .all()
        )

        return [
            {
                "entity_id": system.entity_id,
                "name": system.name,
                "entity_type": system.entity_type,
                "environment": system.environment,
            }
            for system in systems
        ]

    finally:
        db.close()





@mcp.tool()
async def get_services() -> list[dict]:
    """Return services discovered by HUGO across the infrastructure."""

    from app.services.docker_services import DockerServiceDiscovery

    services = DockerServiceDiscovery().discover_services()

    return services


@mcp.tool()
async def get_incidents() -> list[dict]:
    """Return incidents currently known to HUGO."""

    from app.models.incident import Incident
    from app.database.postgres import SessionLocal

    db = SessionLocal()

    try:
        incidents = (
            db.query(Incident)
            .order_by(Incident.created_at.desc())
            .all()
        )

        return [
            {
                "id": incident.id,
                "entity_id": incident.entity_id,
                "severity": incident.severity,
                "title": incident.title,
                "description": incident.description,
                "status": incident.status,
                "created_at": incident.created_at.isoformat(),
            }
            for incident in incidents
        ]

    finally:
        db.close()


@mcp.tool()
async def get_telemetry(entity_id: str | None = None) -> list[dict]:
    """Return recent telemetry collected by HUGO."""

    from app.models.telemetry import TelemetryRecord
    from app.database.postgres import SessionLocal

    db = SessionLocal()

    try:
        query = db.query(TelemetryRecord)

        if entity_id:
            query = query.filter(
                TelemetryRecord.entity_id == entity_id
            )

        records = (
            query
            .order_by(TelemetryRecord.collected_at.desc())
            .limit(100)
            .all()
        )

        return [
            {
                "id": record.id,
                "entity_id": record.entity_id,
                "status": record.status,
                "cpu_percent": record.cpu_percent,
                "memory_percent": record.memory_percent,
                "collected_at": record.collected_at.isoformat(),
            }
            for record in records
        ]

    finally:
        db.close()


@mcp.tool()
async def get_dependencies() -> list[dict]:
    """Return infrastructure dependencies inferred by HUGO."""

    from app.database.neo4j import neo4j_connection

    query = """
    MATCH (source:SystemEntity)-[r:DEPENDS_ON]->(target:SystemEntity)
    RETURN
        source.entity_id AS source,
        source.name AS source_name,
        target.entity_id AS target,
        target.name AS target_name,
        r.relationship AS relationship,
        r.confidence AS confidence,
        r.evidence AS evidence
    ORDER BY source.name, target.name
    """

    with neo4j_connection.driver.session() as session:
        result = session.run(query)

        return [dict(record) for record in result]


@mcp.tool()
async def test_connectivity() -> list[dict]:
    """Return the latest connectivity observations known to HUGO."""

    from app.database.neo4j import neo4j_connection

    query = """
    MATCH (source:SystemEntity)-[r:OBSERVED_CONNECTIVITY]->(target:SystemEntity)
    RETURN
        source.entity_id AS source,
        source.name AS source_name,
        target.entity_id AS target,
        target.name AS target_name,
        r.port AS port,
        r.protocol AS protocol,
        r.confidence AS confidence
    ORDER BY source.name, target.name
    """

    with neo4j_connection.driver.session() as session:
        result = session.run(query)

        return [dict(record) for record in result]


@mcp.tool()
async def get_remediation_actions(
    incident_id: int | None = None,
) -> list[dict]:
    """Return remediation actions managed by HUGO."""

    from app.models.action import RemediationAction
    from app.database.postgres import SessionLocal

    db = SessionLocal()

    try:
        query = db.query(RemediationAction)

        if incident_id is not None:
            query = query.filter(
                RemediationAction.incident_id == incident_id
            )

        actions = (
            query
            .order_by(RemediationAction.created_at.desc())
            .all()
        )

        return [
            {
                "id": action.id,
                "incident_id": action.incident_id,
                "action_type": action.action_type,
                "description": action.description,
                "status": action.status,
                "created_at": action.created_at.isoformat(),
            }
            for action in actions
        ]

    finally:
        db.close()

from app.mcp.security.policy import MCPPolicy, ActionMode
from app.database.postgres import SessionLocal
from app.models.audit import AuditLog


def authorize_mcp_tool(tool_name: str, mode: ActionMode = ActionMode.READ_ONLY) -> dict:
    """
    Central authorization boundary for all HUGO MCP operations.
    """
    required_mode = MCPPolicy.mode_for_tool(tool_name)

    if not MCPPolicy.is_allowed(tool_name, mode):
        raise PermissionError(
            f"MCP tool '{tool_name}' requires '{required_mode.value}' mode."
        )

    return {
        "tool": tool_name,
        "requested_mode": mode.value,
        "required_mode": required_mode.value,
        "authorized": True,
    }


@mcp.tool()
async def check_mcp_authorization(
    tool_name: str,
    mode: str = "read_only",
) -> dict:
    """
    Check whether a requested HUGO MCP operation is authorized.
    """
    try:
        action_mode = ActionMode(mode)
    except ValueError:
        return {
            "authorized": False,
            "error": f"Invalid action mode: {mode}",
            "valid_modes": [m.value for m in ActionMode],
        }

    try:
        return authorize_mcp_tool(tool_name, action_mode)
    except PermissionError as exc:
        return {
            "tool": tool_name,
            "authorized": False,
            "error": str(exc),
        }


@mcp.tool()
async def restart_service(
    service_name: str,
    approved: bool = False,
) -> dict:
    """
    Controlled service restart operation.

    HUGO never executes infrastructure changes unless explicit
    approval is provided.
    """
    if not approved:
        return {
            "tool": "restart_service",
            "service": service_name,
            "mode": ActionMode.PROPOSE.value,
            "status": "approval_required",
            "message": (
                "Restart operation proposed but not executed. "
                "Explicit approval is required."
            ),
        }

    authorize_mcp_tool("restart_service", ActionMode.APPROVED)

    from app.mcp.execution.service_executor import service_executor

    try:
        result = service_executor.restart_container(service_name)

        db = SessionLocal()
        try:
            audit = AuditLog(
                tool_name="restart_service",
                action="restart_container",
                target=service_name,
                mode=ActionMode.APPROVED.value,
                status="executed",
                details=str(result),
            )
            db.add(audit)
            db.commit()
        finally:
            db.close()

        return {
            "tool": "restart_service",
            "service": service_name,
            "mode": ActionMode.APPROVED.value,
            "status": "executed",
            "execution": result,
            "audit_logged": True,
        }

    except Exception as exc:
        return {
            "tool": "restart_service",
            "service": service_name,
            "mode": ActionMode.APPROVED.value,
            "status": "failed",
            "error": str(exc),
        }

if __name__ == "__main__":
    mcp.run()
