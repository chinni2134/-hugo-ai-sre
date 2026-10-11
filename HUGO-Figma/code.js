async function main() {
  await figma.loadFontAsync({ family: "Inter", style: "Regular" });
  await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });

  const C = {
    background: { r: 7 / 255, g: 10 / 255, b: 15 / 255 },
    surface: { r: 13 / 255, g: 19 / 255, b: 27 / 255 },
    elevated: { r: 18 / 255, g: 26 / 255, b: 36 / 255 },
    border: { r: 36 / 255, g: 49 / 255, b: 64 / 255 },
    text: { r: 232 / 255, g: 238 / 255, b: 245 / 255 },
    secondary: { r: 132 / 255, g: 147 / 255, b: 165 / 255 },
    accent: { r: 143 / 255, g: 169 / 255, b: 194 / 255 }
  };

  function solid(color, opacity = 1) {
    return [{
      type: "SOLID",
      color,
      opacity
    }];
  }

  function rect(name, x, y, width, height, color, radius = 0) {
    const node = figma.createRectangle();

    node.name = name;
    node.x = x;
    node.y = y;
    node.resize(width, height);
    node.fills = solid(color);

    if (radius > 0) {
      node.cornerRadius = radius;
    }

    return node;
  }

  function text(
    name,
    value,
    x,
    y,
    size,
    color,
    weight = "Regular"
  ) {
    const node = figma.createText();

    node.name = name;
    node.fontName = {
      family: "Inter",
      style: weight
    };

    node.characters = value;
    node.fontSize = size;
    node.fills = solid(color);
    node.x = x;
    node.y = y;

    return node;
  }

  // ==================================================
  // MAIN FRAME
  // ==================================================

  const frame = figma.createFrame();

  frame.name = "HUGO Command Center";
  frame.resize(1440, 900);
  frame.x = 0;
  frame.y = 0;
  frame.fills = solid(C.background);

  // ==================================================
  // SIDEBAR
  // ==================================================

  const sidebar = rect(
    "HUGO Navigation",
    0,
    0,
    250,
    900,
    C.surface
  );

  // Sidebar divider
  rect(
    "Sidebar Divider",
    249,
    0,
    1,
    900,
    C.border
  );

  // Logo
  const logo = text(
    "HUGO Logo",
    "HUGO",
    32,
    30,
    30,
    C.text,
    "Semi Bold"
  );

  logo.letterSpacing = {
    unit: "PERCENT",
    value: 3
  };

  text(
    "HUGO Subtitle",
    "INFRASTRUCTURE INTELLIGENCE",
    34,
    70,
    9,
    C.secondary,
    "Semi Bold"
  );

  // ==================================================
  // NAVIGATION GROUPS
  // ==================================================

  text(
    "Command Group",
    "COMMAND",
    32,
    130,
    9,
    C.secondary,
    "Semi Bold"
  );

  // Active navigation item
  rect(
    "Active Navigation",
    20,
    155,
    210,
    42,
    C.elevated,
    8
  );

  rect(
    "Active Navigation Indicator",
    20,
    155,
    3,
    42,
    C.accent,
    2
  );

  text(
    "Command Center",
    "Command Center",
    48,
    168,
    13,
    C.text,
    "Semi Bold"
  );

  text(
    "Infrastructure",
    "Infrastructure",
    48,
    214,
    13,
    C.secondary
  );

  text(
    "Topology",
    "Topology",
    48,
    258,
    13,
    C.secondary
  );

  text(
    "Intelligence Group",
    "INTELLIGENCE",
    32,
    320,
    9,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Incidents",
    "Incidents",
    48,
    350,
    13,
    C.secondary
  );

  text(
    "AI Intelligence",
    "AI Intelligence",
    48,
    394,
    13,
    C.secondary
  );

  text(
    "Operations Group",
    "OPERATIONS",
    32,
    455,
    9,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Operations",
    "Operations",
    48,
    485,
    13,
    C.secondary
  );

  text(
    "Digital Twin",
    "Digital Twin",
    48,
    529,
    13,
    C.secondary
  );

  // Sidebar bottom status
  rect(
    "System Status Card",
    20,
    790,
    210,
    75,
    C.elevated,
    10
  );

  text(
    "System Status Label",
    "SYSTEM STATUS",
    35,
    807,
    8,
    C.secondary,
    "Semi Bold"
  );

  text(
    "System Status",
    "OPERATIONAL",
    35,
    828,
    11,
    C.text,
    "Semi Bold"
  );

  // ==================================================
  // TOP COMMAND BAR
  // ==================================================

  rect(
    "Top Command Bar",
    280,
    25,
    1130,
    58,
    C.surface,
    12
  );

  text(
    "Command Label",
    "COMMAND CENTER",
    305,
    46,
    10,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Environment",
    "DEVELOPMENT",
    510,
    46,
    10,
    C.secondary,
    "Semi Bold"
  );

  text(
    "MCP Status",
    "MCP CONNECTED",
    680,
    46,
    10,
    C.text,
    "Semi Bold"
  );

  text(
    "Human Control",
    "HUMAN CONTROL ENABLED",
    1150,
    46,
    10,
    C.accent,
    "Semi Bold"
  );

  // ==================================================
  // PAGE HEADER
  // ==================================================

  text(
    "Page Title",
    "Infrastructure Command Center",
    280,
    115,
    26,
    C.text,
    "Semi Bold"
  );

  text(
    "Page Description",
    "Observe infrastructure state, reason about incidents, and control operations.",
    282,
    153,
    12,
    C.secondary
  );

  // ==================================================
  // OVERVIEW METRICS
  // ==================================================

  const metrics = [
    ["ACTIVE SYSTEMS", "5"],
    ["SERVICES", "5"],
    ["OPEN INCIDENTS", "1"],
    ["HEALTH", "98%"]
  ];

  metrics.forEach((metric, index) => {
    const x = 280 + index * 285;

    rect(
      `Metric Card ${index + 1}`,
      x,
      190,
      265,
      105,
      C.surface,
      12
    );

    text(
      `Metric Label ${index + 1}`,
      metric[0],
      x + 18,
      210,
      9,
      C.secondary,
      "Semi Bold"
    );

    text(
      `Metric Value ${index + 1}`,
      metric[1],
      x + 18,
      240,
      26,
      C.text,
      "Semi Bold"
    );
  });

  // ==================================================
  // INFRASTRUCTURE TOPOLOGY
  // ==================================================

  rect(
    "Topology Panel",
    280,
    325,
    720,
    330,
    C.surface,
    12
  );

  text(
    "Topology Title",
    "INFRASTRUCTURE TOPOLOGY",
    305,
    350,
    10,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Topology Description",
    "Live dependency and connectivity view",
    305,
    373,
    11,
    C.secondary
  );

  const nodes = [
    ["PostgreSQL", 350, 430],
    ["Neo4j", 575, 430],
    ["Redis", 800, 430],
    ["Prometheus", 460, 535],
    ["Elasticsearch", 685, 535]
  ];

  nodes.forEach((node, index) => {
    rect(
      `Infrastructure Node ${index + 1}`,
      node[1],
      node[2],
      145,
      58,
      C.elevated,
      10
    );

    text(
      `Infrastructure Node Label ${index + 1}`,
      node[0],
      node[1] + 16,
      node[2] + 21,
      11,
      C.text,
      "Semi Bold"
    );
  });

  // ==================================================
  // INCIDENT INTELLIGENCE
  // ==================================================

  rect(
    "Incident Panel",
    1025,
    325,
    385,
    330,
    C.surface,
    12
  );

  text(
    "Incident Panel Title",
    "INCIDENT INTELLIGENCE",
    1050,
    350,
    10,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Incident Severity",
    "HIGH",
    1050,
    395,
    20,
    C.text,
    "Semi Bold"
  );

  text(
    "Incident Name",
    "High CPU utilization",
    1050,
    430,
    13,
    C.text,
    "Semi Bold"
  );

  text(
    "Incident Description",
    "Synthetic incident detected on infrastructure.",
    1050,
    458,
    11,
    C.secondary
  );

  text(
    "Reasoning Label",
    "HUGO REASONING",
    1050,
    505,
    9,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Reasoning",
    "Correlating telemetry with",
    1050,
    535,
    12,
    C.text
  );

  text(
    "Reasoning 2",
    "service dependencies and topology.",
    1050,
    558,
    12,
    C.text
  );

  // ==================================================
  // CONTROLLED OPERATIONS
  // ==================================================

  rect(
    "Operations Panel",
    280,
    680,
    1130,
    155,
    C.surface,
    12
  );

  text(
    "Operations Title",
    "CONTROLLED OPERATIONS",
    305,
    705,
    10,
    C.secondary,
    "Semi Bold"
  );

  text(
    "Operations Description",
    "Proposed infrastructure actions remain under explicit human control.",
    305,
    735,
    12,
    C.text
  );

  rect(
    "Review Action",
    305,
    770,
    190,
    42,
    C.elevated,
    8
  );

  text(
    "Review Action Text",
    "REVIEW ACTION",
    335,
    785,
    10,
    C.text,
    "Semi Bold"
  );

  text(
    "Execution Mode",
    "PROTECTED MODE",
    1180,
    785,
    9,
    C.secondary,
    "Semi Bold"
  );

  // ==================================================
  // FOOTER
  // ==================================================

  text(
    "HUGO Operating Loop",
    "OBSERVE  •  UNDERSTAND  •  CORRELATE  •  REASON  •  ACT  •  VERIFY",
    280,
    855,
    9,
    C.secondary
  );

  // ==================================================
  // FINALIZE
  // ==================================================

  figma.currentPage.selection = [frame];
  figma.viewport.scrollAndZoomIntoView([frame]);

  figma.notify("HUGO Command Center updated.");
  figma.closePlugin();
}

main();
