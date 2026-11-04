# Run it in n8n

[`n8n/prospecting-skills.json`](../n8n/prospecting-skills.json) runs three of the skills on an Evaboot export without an AI Agent. Each skill's `SKILL.md` is downloaded from GitHub at its pinned commit and becomes the instructions of one Claude step, so the workflow follows the same rules as Claude Code.

## What runs

1. **Your settings** (Set): the id of an Evaboot export, your ICP and value prop as text, and the four file URLs.
2. **Get export** (Evaboot MCP): the leads of that export, with their Sales Navigator signal columns.
3. **Load ...** (HTTP Request, once each): `qualify-leads`, `buying-signal-scoring`, its `signal-weights.md`, and `write-outreach-messages`.
4. **Leads** (Code): one compact row per lead.
5. **Qualify** (AI Agent): In, Out or Can't tell per lead, with the ICP heading that decided it.
6. **In leads** (Code): keeps the leads labelled In.
7. **Rank** (AI Agent): a score, the signals, a play and an opener per In lead.
8. **Write** (AI Agent): one LinkedIn message under 300 characters per In lead, or a refusal when no real hook exists.
9. **Result rows** and **Results CSV**: one row per lead, every lead included, with its label, rank and message.

## Set it up

1. **Run an export** in Evaboot (the Chrome extension, the dashboard or the Evaboot MCP), capped at the number of leads you want. Copy its id from the export page URL or from the MCP's answer.
2. **Import** the JSON: *Workflows > Import from file*.
3. **Add two credentials:**
   - **Bearer Auth** named `Evaboot MCP (Bearer)`: your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/). Select it on **Get export**.
   - **Anthropic**: select it on the three Claude nodes.
4. **Fill in Your settings:** the export id, then your ICP and value prop. Write each as the questions of [`define-icp-and-value-prop`](../skills/define-icp-and-value-prop/SKILL.md) as headings, with your answer under each. Write `unknown` when you have no answer: the skills skip it.
5. **Test:** click *Execute workflow*, then open **Results CSV** and download the file.

## Good to know

- Rerunning on the same export costs no Evaboot credits: only the Claude calls are paid. Our 10-lead run took 76 seconds.
- A value prop with `unknown` under "What can we show to back that up?" makes Write refuse every lead.
- An ICP answer the export cannot show (for example "they copy leads by hand") turns every lead into Can't tell. Write answers a column can prove, such as a sales team size above 0.
- To use another skill, paste its raw GitHub URL into the matching setting. Pin it to a commit, not `main`, so it cannot change under you.
- Nothing is sent. You load the CSV into your outreach tool after you read it.

Back to the [README](../README.md).
