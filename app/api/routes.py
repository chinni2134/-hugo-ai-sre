# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.database.postgres import get_db
from app.schemas.system import (
    DependencyCreate,
    SystemEntityCreate,
)
from app.services.dependency import DependencyService
from app.services.discovery import DiscoveryService
from app.services.topology import TopologyService
from app.services.docker_topology import docker_topology
from app.services.docker_services import docker_services
from app.services.service_topology import ServiceTopologyService
from app.services.dependency_inference import DependencyInferenceService
from app.services.connectivity import ConnectivityService
from app.services.connectivity_inference import connectivity_inference
from app.services.confidence_engine import ConfidenceEngine
from app.services.telemetry import telemetry_collector
from app.services.telemetry_query import TelemetryQueryService
from app.services.anomaly_detection import AnomalyDetectionService
from app.services.incident_detection import IncidentDetectionService
from app.services.incident_query import IncidentQueryService
from app.models.incident import Incident
from app.models.action import RemediationAction
from app.services.remediation import RemediationService
from app.services.knowledge import KnowledgeService
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentResponse,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["HUGO System"],
)


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "HUGO",
    }


@router.post("/entities")
def create_entity(
    entity: SystemEntityCreate,
    db: Session = Depends(get_db),
):
    return DiscoveryService.register_entity(
        db,
        entity,
    )


@router.get("/entities")
def get_entities(
    db: Session = Depends(get_db),
):
    return DiscoveryService.get_entities(db)


@router.post("/dependencies")
def create_dependency(
    dependency: DependencyCreate,
):
    result = DependencyService.create_dependency(
        source_id=dependency.source_id,
        target_id=dependency.target_id,
        relationship=dependency.relationship,
    )

    return {
        "source": result["source"],
        "target": result["target"],
        "relationship": result["relationship"],
    }

@router.post("/topology/sync")
def sync_topology(
    db: Session = Depends(get_db),
):
    return TopologyService.sync_entities(db)


@router.post("/topology/docker-networks")
def discover_docker_networks():

    return docker_topology.sync_network_dependencies()


@router.get("/services")
def discover_services():

    return docker_services.discover_services()


@router.post("/topology/services")
def sync_service_topology():

    return ServiceTopologyService.sync_services()


@router.post("/intelligence/dependencies")
def infer_dependencies():

    return DependencyInferenceService.infer_and_store()


@router.get("/intelligence/connectivity")
def test_connectivity(
    host: str,
    port: int,
):
    return ConnectivityService.test(host, port)


@router.post("/intelligence/connectivity/scan")
def scan_connectivity():

    return connectivity_inference.test_and_store()


@router.post("/intelligence/confidence")
def calculate_confidence():

    return ConfidenceEngine.calculate()


@router.post("/telemetry/collect")
def collect_telemetry(
    db: Session = Depends(get_db),
):

    return telemetry_collector.collect(db)


@router.get("/telemetry/{entity_id:path}")
def get_telemetry(
    entity_id: str,
    db: Session = Depends(get_db),
):

    return TelemetryQueryService.latest(
        db,
        entity_id,
    )


@router.get("/intelligence/anomalies/{entity_id:path}")
def detect_anomalies(
    entity_id: str,
    db: Session = Depends(get_db),
):

    return AnomalyDetectionService.analyze(
        db,
        entity_id,
    )


@router.post("/incidents/detect")
def detect_incidents(
    db: Session = Depends(get_db),
):

    return IncidentDetectionService.detect(db)


@router.get("/incidents")
def list_incidents(
    status: str | None = None,
    db: Session = Depends(get_db),
):

    return IncidentQueryService.list_incidents(
        db,
        status,
    )


@router.get("/incidents/{incident_id}")
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):

    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return {
            "error": "Incident not found"
        }

    return {
        "id": incident.id,
        "entity_id": incident.entity_id,
        "severity": incident.severity,
        "title": incident.title,
        "description": incident.description,
        "status": incident.status,
        "created_at": incident.created_at,
    }


@router.patch("/incidents/{incident_id}/status")
def update_incident_status(
    incident_id: int,
    status: str,
    db: Session = Depends(get_db),
):

    if status not in {"open", "acknowledged", "resolved"}:
        return {
            "error": "Invalid status"
        }

    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        return {
            "error": "Incident not found"
        }

    incident.status = status

    db.commit()
    db.refresh(incident)

    return {
        "id": incident.id,
        "status": incident.status,
    }


@router.post("/incidents/{incident_id}/remediation")
def recommend_remediation(
    incident_id: int,
    db: Session = Depends(get_db),
):

    return RemediationService.recommend(
        db,
        incident_id,
    )


@router.post("/incidents/test")
def create_test_incident(
    db: Session = Depends(get_db),
):

    incident = Incident(
        entity_id="docker:test",
        severity="high",
        title="High CPU utilization",
        description="Synthetic incident for testing HUGO remediation.",
        status="open",
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return {
        "id": incident.id,
        "entity_id": incident.entity_id,
        "severity": incident.severity,
        "title": incident.title,
        "status": incident.status,
    }


@router.patch("/remediation/{action_id}/approve")
def approve_remediation(
    action_id: int,
    db: Session = Depends(get_db),
):

    action = (
        db.query(RemediationAction)
        .filter(RemediationAction.id == action_id)
        .first()
    )

    if not action:
        return {
            "error": "Remediation action not found"
        }

    if action.status != "proposed":
        return {
            "error": "Only proposed actions can be approved"
        }

    action.status = "approved"

    db.commit()
    db.refresh(action)

    return {
        "action_id": action.id,
        "status": action.status,
    }
@router.get("/digital-twin/state")
def get_digital_twin_state(
    db: Session = Depends(get_db),
):
    """
    Read-only SRE state for HUGO's Digital Twin.

    This endpoint exposes infrastructure state for visualization.
    It does not perform infrastructure actions.
    """

    # Systems
    systems = DiscoveryService.get_entities(db)

    # Services
    services = docker_services.discover_services()

    # Recent telemetry
    from app.models.telemetry import TelemetryRecord

    telemetry_records = (
        db.query(TelemetryRecord)
        .order_by(TelemetryRecord.collected_at.desc())
        .limit(100)
        .all()
    )

    telemetry = [
        {
            "entity_id": record.entity_id,
            "status": record.status,
            "cpu_percent": record.cpu_percent,
            "memory_percent": record.memory_percent,
            "collected_at": record.collected_at.isoformat(),
        }
        for record in telemetry_records
    ]

    # Incidents
    incidents = IncidentQueryService.list_incidents(
        db,
        None,
    )

    # Topology
    from app.database.neo4j import neo4j_connection

    topology_query = """
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
        result = session.run(topology_query)
        topology = [dict(record) for record in result]

    return {
        "platform": "HUGO AI",
        "domain": "SRE",
        "state": "live",
        "systems": systems,
        "services": services,
        "telemetry": telemetry,
        "incidents": incidents,
        "topology": topology,
    }

@router.post(
    "/knowledge",
    response_model=KnowledgeDocumentResponse,
)
def create_knowledge_document(
    document: KnowledgeDocumentCreate,
    db: Session = Depends(get_db),
):
    return KnowledgeService.create_document(
        db=db,
        title=document.title,
        source=document.source,
        document_type=document.document_type,
        content=document.content,
        environment=document.environment,
    )


@router.get(
    "/knowledge",
    response_model=list[KnowledgeDocumentResponse],
)
def get_knowledge_documents(
    db: Session = Depends(get_db),
):
    return KnowledgeService.get_documents(db)


@router.get("/knowledge/search")
def search_knowledge(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db),
):
    from app.services.rag import RAGService

    return RAGService.build_context(
        db=db,
        query=query,
        top_k=top_k,
    )@router.get(
    "/knowledge/{document_id}",
    response_model=KnowledgeDocumentResponse,
)
def get_knowledge_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    document = KnowledgeService.get_document(
        db,
        document_id,
    )

    if not document:
        return {
            "error": "Knowledge document not found"
        }

    return document



