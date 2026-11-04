"""Builds n8n/prospecting-skills.json. Run: python3 n8n/build_workflow.py

The skill loop of this repo in n8n: an Evaboot export in, three published SKILL.md files loaded from GitHub at
their pinned commits and used as the instructions of three Claude steps (qualify, rank by buying signal, write
the first LinkedIn message), a CSV out. Nothing is sent.
"""
import json
import uuid
from pathlib import Path

EVABOOT_MCP = "https://mcp.evaboot.com/mcp"
EVABOOT_CRED = {"httpBearerAuth": {"id": "", "name": "Evaboot MCP (Bearer)"}}
ANTHROPIC_CRED = {"anthropicApi": {"id": "", "name": "Anthropic"}}
MODEL = "claude-sonnet-5-5"

RAW = "https://raw.githubusercontent.com"
SKILLS = {
    "qualify": f"{RAW}/evaboot-labs/evaboot-plugin/37bb0d5944ab744235a67e62213eb2b70ccc5604/skills/qualify-leads/SKILL.md",
    "signals": f"{RAW}/prosyo-ai/gtm-skill/db157476d0eaf40683d3a0c1e906702900206182/skills/buying-signal-scoring/SKILL.md",
    "weights": f"{RAW}/prosyo-ai/gtm-skill/db157476d0eaf40683d3a0c1e906702900206182/skills/buying-signal-scoring/references/signal-weights.md",
    "writer": f"{RAW}/evaboot-labs/evaboot-plugin/37bb0d5944ab744235a67e62213eb2b70ccc5604/skills/write-outreach-messages/SKILL.md",
}

nodes, connections = [], {}


def node(name, type_, version, params, pos, creds=None, **extra):
    n = {"parameters": params, "id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/" + name)), "name": name, "type": type_,
         "typeVersion": version, "position": pos, **extra}
    if creds:
        n["credentials"] = creds
    nodes.append(n)


def link(a, b, kind="main", out=0):
    connections.setdefault(a, {}).setdefault(kind, [])
    while len(connections[a][kind]) <= out:
        connections[a][kind].append([])
    connections[a][kind][out].append({"node": b, "type": kind, "index": 0})


def agent(name, text, system, schema, pos):
    """One skill step: an AI Agent node whose system message is the skill file, with a structured output."""
    node(name, "@n8n/n8n-nodes-langchain.agent", 2.2, {
        "promptType": "define", "text": text, "hasOutputParser": True,
        "options": {"systemMessage": system, "maxIterations": 4},
    }, pos, retryOnFail=True, maxTries=2, waitBetweenTries=3000)
    node(f"Claude ({name.lower()})", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.3, {
        "model": {"__rl": True, "mode": "list", "value": MODEL, "cachedResultName": MODEL},
        "options": {"maxTokensToSample": 8000},
    }, [pos[0] - 80, pos[1] + 220], ANTHROPIC_CRED)
    node(f"{name} output", "@n8n/n8n-nodes-langchain.outputParserStructured", 1.3, {
        "schemaType": "manual", "inputSchema": json.dumps(schema, indent=2)}, [pos[0] + 60, pos[1] + 220])
    link(f"Claude ({name.lower()})", name, "ai_languageModel")
    link(f"{name} output", name, "ai_outputParser")


def load(name, url_key, pos):
    node(name, "n8n-nodes-base.httpRequest", 4.2, {
        "url": "={{ $('Your settings').first().json." + url_key + " }}",
        "options": {"response": {"response": {"responseFormat": "text", "outputPropertyName": "skill"}}},
    }, pos, executeOnce=True)


S = "$('Your settings').first().json"
SKILL = lambda n: "$('" + n + "').first().json.skill"

LEADS_JS = r"""
// One compact row per lead: who, where, the company and the Sales Navigator signal columns. A blank cell stays blank.
const all = $('Get export').first().json.structuredContent?.result?.prospects || [];
const cols = ['Full Name', 'Current Job', 'Location', 'Company Name', 'Company Industry', 'Company Employee Range',
  'Company Employee Exact Count', 'Company Location', 'Sales Team Size', 'Business Development Size', 'Email Status',
  'Matches Filters', 'Years in Position', 'Months in Position', 'Has New Position', 'Profile Recently Hired (90 Days)',
  'Profile Recently Promoted (90 Days)', 'Profile Recent Posts (30 Days)', 'Profile Follows Your Company',
  'Profile Viewed Your Profile (90 Days)', 'Profile Mentioned In News (30 Days)', 'Profile Mutual Connections',
  'Profile Past Colleague', 'Profile Past Customer', 'Profile Shared Groups', 'Profile Shared Education',
  'Profile TeamLink Connections', 'Profile Executive TeamLink', 'Company Employee Growth 6 Months (%)',
  'Company Employee Growth 1 Year (%)'];
const leads = all.map((p, i) => {
  const row = { lead_id: `lead-${String(i + 1).padStart(2, '0')}`, Email: p['Email'] || '' };
  for (const c of cols) row[c] = p[c] ?? '';
  row['Company Description'] = String(p['Company Description'] || '').slice(0, 400);
  return row;
});
return [{ json: { leads } }];
"""

IN_JS = r"""
// Keep the leads the qualify skill labelled In, joined by lead_id.
const leads = $('Leads').first().json.leads;
const labels = $json.output.results;
const keep = new Set(labels.filter(r => r.label === 'In').map(r => r.lead_id));
return [{ json: { leads: leads.filter(l => keep.has(l.lead_id)), labels } }];
"""

ROWS_JS = r"""
// One CSV row per lead: the qualify label, the rank and the first message (or the refusal).
const leads = $('Leads').first().json.leads;
const out = (node, key) => { try { return $(node).first().json.output[key] || []; } catch (e) { return []; } };
const labels = out('Qualify', 'results');
const ranked = out('Rank', 'ranked');
const msgs = $json.output?.messages || [];
return leads.map(l => {
  const q = labels.find(r => r.lead_id === l.lead_id) || {};
  const r = ranked.find(x => x.lead_id === l.lead_id) || {};
  const m = msgs.find(x => x.lead_id === l.lead_id) || {};
  return { json: {
    name: l['Full Name'], title: l['Current Job'], company: l['Company Name'], email: l.Email,
    email_status: l['Email Status'], label: q.label || '', why: q.heading || '', rank: r.rank ?? '',
    score: r.score ?? '', signals: r.signals || '', play: r.play || '', opener: r.opener || '', message: m.message || '',
    refused: m.refused ? (m.reason || 'yes') : '',
  } };
});
"""

PREFIX = ("=You run the published agent skill below, exactly as written. You have no tools: every file the skill "
          "says to read is pasted after the skill. Return only the structured output.\n\n")

QUALIFY_SYSTEM = PREFIX + "# Skill: qualify-leads\n\n{{ " + SKILL("Load qualify-leads") + " }}\n\n# ~/.evaboot/EVABOOT-ICP.md\n\n{{ " + S + ".icp }}"
RANK_SYSTEM = (PREFIX + "# Skill: buying-signal-scoring\n\n{{ " + SKILL("Load buying-signal-scoring") + " }}\n\n"
               "# references/signal-weights.md\n\n{{ " + SKILL("Load signal weights") + " }}\n\n"
               "# The ICP\n\n{{ " + S + ".icp }}\n\n# The offer\n\n{{ " + S + ".value_prop }}\n\n"
               "# The signals\n\nThe signals are the Sales Navigator columns of each lead row. A blank cell is unknown, "
               "never a signal. Today is {{ $now.toISODate() }}. All leads given were labelled In (fit tier 1).")
WRITE_SYSTEM = PREFIX + "# Skill: write-outreach-messages\n\n{{ " + SKILL("Load write-outreach-messages") + " }}\n\n# ~/.evaboot/EVABOOT-VALUE-PROP.md\n\n{{ " + S + ".value_prop }}"

node("Run the skills", "n8n-nodes-base.manualTrigger", 1, {}, [0, 0])
node("Your settings", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/export_id")), "name": "export_id", "type": "string", "value": "PASTE_YOUR_EVABOOT_EXPORT_ID"},
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/icp")), "name": "icp", "type": "string",
     "value": "PASTE YOUR ICP: the 7 questions of define-icp-and-value-prop with your answers (see docs/n8n.md)."},
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/value_prop")), "name": "value_prop", "type": "string",
     "value": "PASTE YOUR VALUE PROP: the 9 questions of define-icp-and-value-prop with your answers."},
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/qualify_skill_url")), "name": "qualify_skill_url", "type": "string", "value": SKILLS["qualify"]},
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/signals_skill_url")), "name": "signals_skill_url", "type": "string", "value": SKILLS["signals"]},
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/weights_url")), "name": "weights_url", "type": "string", "value": SKILLS["weights"]},
    {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "prospecting-skills/setting/writer_skill_url")), "name": "writer_skill_url", "type": "string", "value": SKILLS["writer"]},
]}, "options": {}}, [220, 0])
node("Get export", "@n8n/n8n-nodes-langchain.mcpClient", 1.1, {
    "endpointUrl": EVABOOT_MCP, "authentication": "bearerAuth",
    "tool": {"__rl": True, "mode": "list", "value": "get_export", "cachedResultName": "get_export"},
    "inputMode": "json", "jsonInput": "={{ JSON.stringify({ extraction_id: " + S + ".export_id }) }}",
    "options": {"timeout": 120000},
}, [440, 0], EVABOOT_CRED)
load("Load qualify-leads", "qualify_skill_url", [660, 0])
load("Load buying-signal-scoring", "signals_skill_url", [880, 0])
load("Load signal weights", "weights_url", [1100, 0])
load("Load write-outreach-messages", "writer_skill_url", [1320, 0])
node("Leads", "n8n-nodes-base.code", 2, {"jsCode": LEADS_JS}, [1540, 0])

agent("Qualify", "={{ JSON.stringify($json.leads) }}", QUALIFY_SYSTEM, {
    "type": "object", "required": ["results"], "properties": {"results": {"type": "array", "items": {
        "type": "object", "required": ["lead_id", "label", "heading"], "properties": {
            "lead_id": {"type": "string"}, "label": {"type": "string", "enum": ["In", "Out", "Can't tell"]},
            "heading": {"type": "string"}}}}}}, [220, 420])
node("In leads", "n8n-nodes-base.code", 2, {"jsCode": IN_JS}, [500, 420])
agent("Rank", "={{ JSON.stringify($json.leads) }}", RANK_SYSTEM, {
    "type": "object", "required": ["ranked"], "properties": {"ranked": {"type": "array", "items": {
        "type": "object", "required": ["lead_id", "rank", "score", "signals", "play", "opener"], "properties": {
            "lead_id": {"type": "string"}, "rank": {"type": "number"}, "score": {"type": "number"},
            "signals": {"type": "string"}, "play": {"type": "string"}, "opener": {"type": "string"}}}}}}, [780, 420])
agent("Write", "={{ JSON.stringify({ leads: $('In leads').first().json.leads, ranked: $json.output.ranked }) }}",
      WRITE_SYSTEM, {
          "type": "object", "required": ["messages"], "properties": {"messages": {"type": "array", "items": {
              "type": "object", "required": ["lead_id", "refused", "message", "reason"], "properties": {
                  "lead_id": {"type": "string"}, "refused": {"type": "boolean"}, "message": {"type": "string"},
                  "reason": {"type": "string"}}}}}}, [1120, 420])
node("Result rows", "n8n-nodes-base.code", 2, {"jsCode": ROWS_JS}, [1400, 420])
node("Results CSV", "n8n-nodes-base.convertToFile", 1.1, {
    "operation": "csv", "options": {"fileName": "prospecting-skills.csv"}}, [1620, 420])

for a, b in [("Run the skills", "Your settings"), ("Your settings", "Get export"),
             ("Get export", "Load qualify-leads"), ("Load qualify-leads", "Load buying-signal-scoring"),
             ("Load buying-signal-scoring", "Load signal weights"), ("Load signal weights", "Load write-outreach-messages"),
             ("Load write-outreach-messages", "Leads"), ("Leads", "Qualify"), ("Qualify", "In leads"),
             ("In leads", "Rank"), ("Rank", "Write"), ("Write", "Result rows"), ("Result rows", "Results CSV")]:
    link(a, b)

workflow = {"name": "Prospecting skills (Evaboot + Claude skills)", "nodes": nodes, "connections": connections,
            "settings": {"executionOrder": "v1"}, "pinData": {}}
out = Path(__file__).with_name("prospecting-skills.json")
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(out, len(nodes), "nodes")
