# Agent instructions

This repo is a curated set of open-source prospecting skills from Evaboot, Anthropic and Prosyo, copied unchanged at pinned commits (`SKILLS.md`), plus one skill that runs them as a loop on real leads: define the ICP, export Sales Navigator leads with the Evaboot MCP, qualify them, rank them by buying signal and draft the first touch. Each step writes a file in `runs/`. Nothing is sent.

1. Follow the skill in `skills/prospecting-skills/SKILL.md` step by step. It calls the other skills in `skills/` by name.
2. If the Evaboot MCP is not connected, follow `docs/connect-your-agent.md`.
3. If the user asks what a skill does or where it comes from, answer from `SKILLS.md`, and read the skill's own `SKILL.md` before you run it.
4. If the user wants n8n instead of an AI Agent, follow `docs/n8n.md` with them one step at a time.
5. To update a third-party skill, follow "Pinned commits" in `SKILLS.md`; never edit a copied skill in place.

Confirm with the user before every call that spends credits (1 Evaboot credit per exported lead), and never export more leads than they approved. Never send a message or an email, and never add a lead to a sequence or a CRM, without an explicit yes. Never ask for or handle another tool's API key: the user writes keys into `.env`. Never commit `.env` or `runs/`: they hold secrets and real people's data.
