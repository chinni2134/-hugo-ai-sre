import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Boxes,
  Brain,
  CheckCircle2,
  GitBranch,
  LayoutDashboard,
  Network,
  ShieldCheck,
  Terminal,
  Zap,
} from "lucide-react";

const API = "http://localhost:8000/api/v1";

const navItems = [
  { label: "Command Center", icon: LayoutDashboard },
  { label: "Infrastructure", icon: Boxes },
  { label: "Topology", icon: Network },
  { label: "Incidents", icon: AlertTriangle },
  { label: "AI Intelligence", icon: Brain },
  { label: "Operations", icon: Zap },
];

function App() {
  const [state, setState] = useState(null);
  const [error, setError] = useState("");
  const [investigating, setInvestigating] = useState(false);
  const [remediation, setRemediation] = useState(null);
  const [approving, setApproving] = useState(false);
  const [approvalMessage, setApprovalMessage] = useState("");

  async function loadState() {
    try {
      const response = await fetch(`${API}/digital-twin/state`);

      if (!response.ok) {
        throw new Error(`HUGO API returned ${response.status}`);
      }

      const data = await response.json();

      setState(data);
      setError("");
    } catch (err) {
      setError(err.message);
    }
  }

  async function investigateIncident() {
    if (!primaryIncident) {
      return;
    }

    setInvestigating(true);
    setApprovalMessage("");

    try {
      const response = await fetch(
        `${API}/incidents/${primaryIncident.id}/remediation`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(`Remediation API returned ${response.status}`);
      }

      const data = await response.json();

      setRemediation(data);
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setInvestigating(false);
    }
  }

  async function approveRemediation() {
    if (!remediation?.action_id) {
      return;
    }

    setApproving(true);
    setApprovalMessage("");

    try {
      const response = await fetch(
        `${API}/remediation/${remediation.action_id}/approve`,
        {
          method: "PATCH",
        }
      );

      if (!response.ok) {
        throw new Error(`Approval API returned ${response.status}`);
      }

      const data = await response.json();

      setRemediation((previous) => ({
        ...previous,
        ...data,
        status: data.status || "approved",
      }));

      setApprovalMessage(
        "Remediation proposal approved. Execution remains governed by HUGO's protected operation layer."
      );

      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setApproving(false);
    }
  }

  useEffect(() => {
    loadState();

    const interval = setInterval(loadState, 5000);

    return () => clearInterval(interval);
  }, []);

  const services = state?.services ?? [];
  const incidents = state?.incidents ?? [];
  const telemetry = state?.telemetry ?? [];
  const topology = state?.topology ?? [];

  const openIncidents = incidents.filter(
    (incident) =>
      String(incident.status).toLowerCase() === "open"
  );

  const highIncidents = openIncidents.filter((incident) =>
    ["high", "critical"].includes(
      String(incident.severity).toLowerCase()
    )
  );

  const healthyServices = services.filter((service) => {
    const records = telemetry.filter(
      (record) => record.entity_id === service.entity_id
    );

    if (!records.length) {
      return false;
    }

    const latest = records[0];

    return (
      String(latest.status).toLowerCase() === "running" &&
      Number(latest.cpu_percent ?? 0) < 80 &&
      Number(latest.memory_percent ?? 0) < 85
    );
  });

  const systemState =
    highIncidents.length > 0
      ? "Attention required"
      : "All systems operational";

  const primaryIncident =
    highIncidents[0] || openIncidents[0] || null;

  const systemNames = useMemo(() => {
    const names = new Set();

    services.forEach((service) => {
      if (service.service_name) {
        names.add(service.service_name);
      }
    });

    return Array.from(names);
  }, [services]);

  const latestIncidentEntity =
    primaryIncident?.entity_id || "unknown";

  const remediationStatus =
    String(remediation?.status || "proposed").toLowerCase();

  return (
    <div className="app">

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-mark">H</div>

          <div>
            <h1>HUGO</h1>
            <span>Infrastructure Intelligence</span>
          </div>
        </div>

        <nav>
          {navItems.map(({ label, icon: Icon }, index) => (
            <button
              className={`nav-item ${index === 0 ? "active" : ""
                }`}
              key={label}
            >
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">

          <div className="mcp-status">
            <ShieldCheck size={18} />

            <div>
              <strong>MCP Operational</strong>
              <span>11 tools available</span>
            </div>
          </div>

        </div>
      </aside>


      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="main">

        {/* TOP BAR */}

        <header className="topbar">

          <div>
            <p className="eyebrow">
              HUGO AI / COMMAND CENTER
            </p>

            <h2>Infrastructure Overview</h2>
          </div>

          <div
            className={`system-state ${highIncidents.length ? "attention" : ""
              }`}
          >
            <span className="pulse" />

            {systemState}
          </div>

        </header>


        {/* API ERROR */}

        {error && (
          <div className="incident-card">

            <div className="severity">
              API ERROR
            </div>

            <h4>
              Unable to reach HUGO
            </h4>

            <p>{error}</p>

          </div>
        )}


        {/* HERO */}

        <section className="hero">

          <div>

            <p className="eyebrow">
              AUTONOMOUS OPERATIONS
            </p>

            <h3>
              Observe. Understand. Act.
            </h3>

            <p>
              HUGO continuously builds an understanding
              of your infrastructure, dependencies,
              telemetry and operational state.
            </p>

          </div>

          <div className="hero-icon">
            <Brain size={42} />
          </div>

        </section>


        {/* METRICS */}

        <section className="metrics">

          <Metric
            icon={<Activity />}
            label="Systems"
            value={
              systemNames.length || services.length
            }
            detail="Live services"
          />

          <Metric
            icon={<Network />}
            label="Dependencies"
            value={topology.length}
            detail="Topology relationships"
          />

          <Metric
            icon={<AlertTriangle />}
            label="Incidents"
            value={openIncidents.length}
            detail={
              openIncidents.length
                ? "Open"
                : "Clear"
            }
            warning={openIncidents.length > 0}
          />

          <Metric
            icon={<GitBranch />}
            label="MCP Tools"
            value="11"
            detail="Operational"
          />

        </section>


        {/* INFRASTRUCTURE + INCIDENT */}

        <section className="content-grid">

          {/* LIVE INFRASTRUCTURE */}

          <div className="panel">

            <div className="panel-header">

              <div>
                <p className="eyebrow">
                  LIVE INFRASTRUCTURE
                </p>

                <h3>
                  System Inventory
                </h3>
              </div>

              <Boxes size={20} />

            </div>


            <div className="system-list">

              {services.map((service) => {

                const record = telemetry.find(
                  (item) =>
                    item.entity_id ===
                    service.entity_id
                );

                const cpu = Number(
                  record?.cpu_percent ?? 0
                );

                const memory = Number(
                  record?.memory_percent ?? 0
                );

                const critical =
                  cpu >= 80 ||
                  memory >= 85 ||
                  String(
                    record?.status
                  ).toLowerCase() !==
                  "running";

                return (
                  <div
                    className="system-row"
                    key={`${service.entity_id}-${service.service_name}`}
                  >

                    <div className="system-info">

                      <div
                        className={`system-dot ${critical
                          ? "critical-dot"
                          : ""
                          }`}
                      />

                      <div>

                        <strong>
                          {service.service_name}
                        </strong>

                        <span>
                          {service.protocol
                            ? `${service.protocol} / ${service.port}`
                            : "Infrastructure service"}
                        </span>

                      </div>

                    </div>


                    <div>

                      <span
                        className={
                          critical
                            ? "critical"
                            : "healthy"
                        }
                      >
                        {critical
                          ? "Attention"
                          : "Healthy"}
                      </span>

                      <small className="telemetry-value">
                        CPU {cpu.toFixed(1)}%
                        {" · "}
                        MEM {memory.toFixed(1)}%
                      </small>

                    </div>

                  </div>
                );
              })}

            </div>

          </div>


          {/* INCIDENT INTELLIGENCE */}

          <div className="panel incident-panel">

            <div className="panel-header">

              <div>
                <p className="eyebrow">
                  INCIDENT INTELLIGENCE
                </p>

                <h3>
                  Active Incident
                </h3>
              </div>

              <AlertTriangle size={20} />

            </div>


            {primaryIncident ? (

              <div className="incident-card">

                <div className="severity">
                  {String(
                    primaryIncident.severity
                  ).toUpperCase()}
                </div>

                <h4>
                  {primaryIncident.title}
                </h4>

                <p>
                  {primaryIncident.description ||
                    "HUGO detected an infrastructure incident requiring investigation."}
                </p>

                <div className="incident-meta">

                  <span>
                    Entity:{" "}
                    <strong>
                      {primaryIncident.entity_id}
                    </strong>
                  </span>

                  <span>
                    Status:{" "}
                    <strong>
                      {primaryIncident.status}
                    </strong>
                  </span>

                </div>


                {/* TEST INCIDENT NOTICE */}

                {String(
                  primaryIncident.entity_id
                ).startsWith("docker:test") && (
                    <p
                      style={{
                        marginTop: "10px",
                        color: "#7f8d9d",
                        fontSize: "9px",
                      }}
                    >
                      Simulation incident — generated
                      through HUGO's test incident
                      endpoint for controlled demonstration.
                    </p>
                  )}


                <div className="incident-actions">

                  <button
                    className="primary-btn"
                    onClick={investigateIncident}
                    disabled={investigating}
                  >

                    <Brain size={16} />

                    {investigating
                      ? "HUGO Investigating..."
                      : "Investigate with HUGO"}

                  </button>


                  {remediation && (
                    <button
                      className="secondary-btn"
                      onClick={() =>
                        document
                          .querySelector(
                            ".ai-intelligence"
                          )
                          ?.scrollIntoView({
                            behavior: "smooth",
                          })
                      }
                    >
                      <Terminal size={16} />
                      View analysis
                    </button>
                  )}

                </div>

              </div>

            ) : (

              <div className="incident-card">

                <div className="severity healthy-severity">
                  HEALTHY
                </div>

                <h4>
                  No open incidents
                </h4>

                <p>
                  HUGO currently has no open SRE
                  incidents requiring intervention.
                </p>

              </div>

            )}

          </div>

        </section>


        {/* =====================================================
            AI INTELLIGENCE
        ====================================================== */}

        {remediation && primaryIncident && (

          <section className="ai-intelligence">

            <div className="ai-intelligence-header">

              <div className="ai-intelligence-title">

                <div className="ai-intelligence-icon">
                  <Brain size={18} />
                </div>

                <div>

                  <p className="eyebrow">
                    HUGO AI / INCIDENT INTELLIGENCE
                  </p>

                  <h3>
                    Operational Investigation
                  </h3>

                  <p>
                    Evidence-driven incident analysis
                    from HUGO infrastructure state.
                  </p>

                </div>

              </div>


              <span className="ai-status">
                LIVE ANALYSIS
              </span>

            </div>


            {/* AI REASONING PIPELINE */}

            <div className="ai-flow">

              <IntelligenceStep
                number="01"
                title="OBSERVATION"
                text={
                  primaryIncident.title
                }
                active
              />

              <IntelligenceStep
                number="02"
                title="CORRELATION"
                text="Telemetry + topology + service state"
                active
              />

              <IntelligenceStep
                number="03"
                title="IMPACT"
                text={`Affected entity: ${latestIncidentEntity}`}
                active
              />

              <IntelligenceStep
                number="04"
                title="ANALYSIS"
                text="HUGO evaluates the incident evidence and determines the next diagnostic action."
                active
              />

              <IntelligenceStep
                number="05"
                title="RECOMMENDATION"
                text={
                  remediation.description ||
                  remediation.action_type
                }
                active
              />

              <IntelligenceStep
                number="06"
                title="HUMAN APPROVAL"
                text={
                  remediationStatus === "approved"
                    ? "Approved by operator."
                    : "Explicit approval required."
                }
                active
              />

            </div>


            {/* ANALYSIS CARDS */}

            <div className="ai-analysis-grid">

              <div className="ai-analysis-card">

                <span className="label">
                  OBSERVATION
                </span>

                <strong>
                  {primaryIncident.title}
                </strong>

                <p>
                  HUGO detected an active{" "}
                  {String(
                    primaryIncident.severity
                  ).toLowerCase()}{" "}
                  severity incident.
                </p>

              </div>


              <div className="ai-analysis-card">

                <span className="label">
                  CORRELATION
                </span>

                <strong>
                  Multi-source evidence
                </strong>

                <p>
                  HUGO correlates telemetry,
                  topology relationships and
                  infrastructure service state.
                </p>

              </div>


              <div className="ai-analysis-card">

                <span className="label">
                  IMPACT
                </span>

                <strong>
                  {latestIncidentEntity}
                </strong>

                <p>
                  Current incident scope is limited
                  to the entity reported by the
                  incident engine.
                </p>

              </div>


              <div className="ai-analysis-card">

                <span className="label">
                  HUGO ANALYSIS
                </span>

                <strong>
                  Diagnostic investigation required
                </strong>

                <p>
                  HUGO has generated a remediation
                  proposal rather than directly
                  changing infrastructure.
                </p>

              </div>


              {/* RECOMMENDATION */}

              <div className="ai-analysis-card recommendation full">

                <span className="label">
                  RECOMMENDED ACTION
                </span>

                <div className="recommendation-action">

                  <div>

                    <strong>
                      {remediation.action_type}
                    </strong>

                    <p>
                      {remediation.description}
                    </p>

                  </div>

                  <span className="proposed-badge">
                    {String(
                      remediation.status ||
                      "PROPOSED"
                    ).toUpperCase()}
                  </span>

                </div>


                {/* APPROVAL */}

                <div className="ai-approval">

                  {remediationStatus ===
                    "approved" ? (

                    <button
                      className="ai-approve"
                      disabled
                    >
                      <CheckCircle2
                        size={14}
                      />
                      Approved
                    </button>

                  ) : (

                    <button
                      className="ai-approve"
                      onClick={
                        approveRemediation
                      }
                      disabled={approving}
                    >

                      <ShieldCheck
                        size={14}
                      />

                      {approving
                        ? "Approving..."
                        : "Approve Remediation"}

                    </button>

                  )}

                  <button
                    className="ai-dismiss"
                    onClick={() =>
                      setRemediation(null)
                    }
                  >
                    Dismiss
                  </button>

                </div>

              </div>

            </div>


            {/* APPROVAL MESSAGE */}

            {approvalMessage && (

              <div
                style={{
                  marginTop: "12px",
                  padding: "10px 12px",
                  border:
                    "1px solid #304153",
                  borderRadius: "7px",
                  color: "#91aa9c",
                  background: "#0a1017",
                  fontSize: "9px",
                }}
              >

                <CheckCircle2
                  size={13}
                  style={{
                    verticalAlign: "middle",
                    marginRight: "6px",
                  }}
                />

                {approvalMessage}

              </div>

            )}

          </section>

        )}
        {/* =====================================================
    MCP OPERATIONS
====================================================== */}

        {remediation && (
          <section className="mcp-operations">

            <div className="mcp-operations-header">

              <div>
                <p className="eyebrow">
                  HUGO MCP / CONTROLLED OPERATIONS
                </p>

                <h3>
                  Governed Infrastructure Operation
                </h3>

                <p>
                  HUGO routes approved infrastructure
                  actions through its native MCP execution layer.
                </p>
              </div>

              <div className="mcp-live-badge">
                <span className="live-dot" />
                MCP ONLINE
              </div>

            </div>


            <div className="operation-grid">

              <div className="operation-card">

                <span className="operation-label">
                  INCIDENT
                </span>

                <strong>
                  {primaryIncident?.title || "Active Incident"}
                </strong>

                <small>
                  {primaryIncident?.entity_id || "Unknown entity"}
                </small>

              </div>


              <div className="operation-card">

                <span className="operation-label">
                  PROPOSED ACTION
                </span>

                <strong>
                  {remediation.action_type}
                </strong>

                <small>
                  {remediation.description}
                </small>

              </div>


              <div className="operation-card">

                <span className="operation-label">
                  AUTHORIZATION
                </span>

                <strong>
                  {remediationStatus === "approved"
                    ? "HUMAN APPROVED"
                    : "AWAITING APPROVAL"}
                </strong>

                <small>
                  Protected operation mode
                </small>

              </div>


              <div className="operation-card">

                <span className="operation-label">
                  EXECUTION MODE
                </span>

                <strong>
                  MCP / GOVERNED
                </strong>

                <small>
                  Authorization required before execution
                </small>

              </div>

            </div>


            <div className="operation-pipeline">

              <OperationStage
                number="01"
                title="PROPOSED"
                active
                complete
              />

              <OperationConnector />

              <OperationStage
                number="02"
                title="HUMAN APPROVAL"
                active={remediationStatus === "approved"}
                complete={remediationStatus === "approved"}
              />

              <OperationConnector />

              <OperationStage
                number="03"
                title="MCP AUTHORIZATION"
                active={remediationStatus === "approved"}
              />

              <OperationConnector />

              <OperationStage
                number="04"
                title="EXECUTION"
              />

              <OperationConnector />

              <OperationStage
                number="05"
                title="VERIFICATION"
              />

            </div>


            <div className="operation-footer">

              <ShieldCheck size={18} />

              <div>
                <strong>
                  Protected execution boundary
                </strong>

                <span>
                  Infrastructure-changing operations remain
                  explicitly governed by HUGO authorization.
                </span>
              </div>

              <span className="operation-mode">
                APPROVED MODE
              </span>

            </div>

          </section>
        )}

        {/* =====================================================
    HUGO VERIFICATION
====================================================== */}

        {remediation && (
          <section className="verification-panel">

            <div className="verification-header">

              <div>
                <p className="eyebrow">
                  HUGO / POST-OPERATION VERIFICATION
                </p>

                <h3>
                  Infrastructure State Verification
                </h3>

                <p>
                  HUGO verifies infrastructure state after a
                  governed operation before closing the loop.
                </p>
              </div>

              <div className="verification-badge">
                <ShieldCheck size={15} />
                CONTROLLED
              </div>

            </div>


            <div className="verification-grid">

              <VerificationItem
                label="TARGET"
                value={primaryIncident?.entity_id || "Unknown"}
              />

              <VerificationItem
                label="ACTION"
                value={remediation.action_type}
              />

              <VerificationItem
                label="AUTHORIZATION"
                value={
                  remediationStatus === "approved"
                    ? "APPROVED"
                    : "PENDING"
                }
                success={remediationStatus === "approved"}
              />

              <VerificationItem
                label="CURRENT STATE"
                value={
                  state?.state?.toUpperCase() || "LIVE"
                }
                success
              />

            </div>


            <div className="verification-chain">

              <VerificationStage
                title="Operation governed"
                status="Human approval boundary"
                complete={remediationStatus === "approved"}
              />

              <div className="verification-arrow">→</div>

              <VerificationStage
                title="Infrastructure observed"
                status={`${services.length} live services`}
                complete
              />

              <div className="verification-arrow">→</div>

              <VerificationStage
                title="Telemetry available"
                status={`${telemetry.length} telemetry records`}
                complete
              />

              <div className="verification-arrow">→</div>

              <VerificationStage
                title="Verification"
                status={
                  remediationStatus === "approved"
                    ? "Ready for execution verification"
                    : "Awaiting approved operation"
                }
                complete={false}
              />

            </div>


            <div className="verification-note">

              <Activity size={16} />

              <span>
                HUGO continuously compares observed infrastructure
                state against the expected operational state.
              </span>

            </div>

          </section>
        )}
        {/* =====================================================
            HUMAN CONTROL BANNER
        ====================================================== */}

        <section className="bottom-banner">

          <div>

            <ShieldCheck size={20} />

            <div>

              <strong>
                Human-controlled operations
              </strong>

              <span>
                Infrastructure-changing actions
                require explicit approval.
              </span>

            </div>

          </div>

          <span className="mode">
            PROTECTED MODE
          </span>

        </section>


        {/* LIVE FOOTER */}

        <div className="live-footer">

          <span className="live-dot" />

          HUGO DIGITAL TWIN STATE:{" "}
          {state?.state?.toUpperCase() ||
            "CONNECTING"}

          <span>•</span>

          {healthyServices.length}/
          {services.length || 0}
          {" "}services healthy

          <span>•</span>

          Auto-refresh: 5s

        </div>

      </main>

    </div>
  );
}


/* =========================================================
   METRIC COMPONENT
========================================================= */

function Metric({
  icon,
  label,
  value,
  detail,
  warning,
}) {
  return (
    <div className="metric">

      <div className="metric-icon">
        {icon}
      </div>

      <div>

        <span>{label}</span>

        <strong>{value}</strong>

        <small
          className={
            warning
              ? "warning-text"
              : ""
          }
        >
          {detail}
        </small>

      </div>

    </div>
  );
}


/* =========================================================
   AI INTELLIGENCE STEP
========================================================= */

function IntelligenceStep({
  number,
  title,
  text,
  active,
}) {
  return (
    <div
      className={`ai-flow-step ${active ? "active" : ""
        }`}
    >

      <strong>
        {number} · {title}
      </strong>

      <span>
        {text}
      </span>

    </div>
  );
}


export default App;
function OperationStage({
  number,
  title,
  active = false,
  complete = false,
}) {
  return (
    <div
      className={`operation-stage ${active ? "active" : ""
        } ${complete ? "complete" : ""}`}
    >
      <span className="operation-number">
        {complete ? "✓" : number}
      </span>

      <strong>
        {title}
      </strong>
    </div>
  );
}


function OperationConnector() {
  return (
    <div className="operation-connector">
      →
    </div>
  );
}

function VerificationItem({
  label,
  value,
  success = false,
}) {
  return (
    <div className="verification-item">

      <span>
        {label}
      </span>

      <strong
        className={success ? "verification-success" : ""}
      >
        {value}
      </strong>

    </div>
  );
}


function VerificationStage({
  title,
  status,
  complete = false,
}) {
  return (
    <div
      className={`verification-stage ${complete ? "complete" : ""
        }`}
    >

      <div className="verification-stage-dot">
        {complete ? "✓" : "•"}
      </div>

      <div>

        <strong>
          {title}
        </strong>

        <span>
          {status}
        </span>

      </div>

    </div>
  );
}