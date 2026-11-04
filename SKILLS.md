# The skill set

Six open-source skills from three publishers, plus the Evaboot MCP tools, chosen for one prospecting loop: define who you sell to, get real leads, qualify them, rank them by buying signal, write the first touch. Each is pinned to the commit we tested, because a skill runs with your agent's permissions: read it before you install it.

| Step | Skill | Publisher | License | What it does |
|---|---|---|---|---|
| 1. ICP | `define-icp-and-value-prop` | [Evaboot](https://github.com/evaboot-labs/evaboot-plugin) | MIT | Asks 16 questions, one at a time, and writes `~/.evaboot/EVABOOT-ICP.md` and `EVABOOT-VALUE-PROP.md` |
| 2. Leads | Evaboot MCP tools | [Evaboot](https://github.com/evaboot-labs/evaboot-plugin) | MIT | Builds a Sales Navigator search from one sentence and exports the leads with verified emails (1 credit per lead) |
| 3. Qualify | `qualify-leads` | [Evaboot](https://github.com/evaboot-labs/evaboot-plugin) | MIT | One label per lead against the ICP file: In, Out or Can't tell, with the heading that decided it |
| 4. Rank | `buying-signal-scoring` | [Prosyo](https://github.com/prosyo-ai/gtm-skill) | MIT | Weights each signal by strength and freshness, stacks them per account, and gives a play and an opener |
| 5. Write | `write-outreach-messages` | [Evaboot](https://github.com/evaboot-labs/evaboot-plugin) | MIT | A LinkedIn message under 300 characters, opened on a real Sales Navigator signal, or a refusal when there is none |
| 5. Write | `draft-outreach` | [Anthropic](https://github.com/anthropics/knowledge-work-plugins/tree/main/sales) | Apache-2.0 | A cold email or sequence grounded in your CRM, email and web research, created as a draft |
| Extra | `account-research` | [Anthropic](https://github.com/anthropics/knowledge-work-plugins/tree/main/sales) | Apache-2.0 | A brief on one company or contact: overview, recent news, priorities and fit |

## Pinned commits

| Repo | Commit |
|---|---|
| evaboot-labs/evaboot-plugin | `37bb0d5944ab744235a67e62213eb2b70ccc5604` |
| prosyo-ai/gtm-skill | `db157476d0eaf40683d3a0c1e906702900206182` |
| anthropics/knowledge-work-plugins | `2574e29377c7173d0cecffef29a6ecbd7f8ccb5d` |

The six skill folders are copied unchanged into `skills/`, so one plugin install brings them all. To update one, change its commit here and in `scripts/vendor-skills.sh`, run the script, then read the diff before you commit. Licenses: [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

Back to the [README](README.md).
