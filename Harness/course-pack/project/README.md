# Supercharging Your Pentesting With AI, takeaway repo

Everything you built during the workshop, plus the reference material that did not
fit on a slide. Clone this at the start of the day.

```
claude-profile/        A Claude Code profile configured for web pentesting
  CLAUDE.md            Engagement rules. Shapes behaviour, enforces nothing.
  scope.md             The scope document the hook reads
  .claude/
    settings.json      Permissions, allow and deny, and the hook registration
    hooks/             scope-check.sh, the one place the model cannot argue with
    skills/recon/      A worked security skill
    agents/            bola-hunter.md, a per class subagent
harness/
  agent.py             The 120 line local harness, all seven components labelled
  system_prompt.md     Its methodology document
prompts/
  finding.schema.json  The shared output schema every subagent emits
evals/
  cases.yaml           A minimal eval set, including a negative case
LINKS.md               Tools named in passing, and the fixes for known traps
```

## Running the harness

```bash
export AGENT_BASE_URL=http://localhost:11434/v1   # Ollama, vLLM or LM Studio
export AGENT_MODEL=qwen3:32b
export AGENT_TARGET=http://localhost:8080
export TOKEN_ALICE=... TOKEN_BOB=...
cd harness && python3 agent.py "Map the API and test for broken object level authorization."
```

Read it before you run it. It is deliberately short enough to read in one sitting,
and the seven harness components are labelled in the header comment.

## Using the profile

Copy `claude-profile/` over your engagement directory, fill in `scope.md`, then set
`ENGAGEMENT_HOST` so the hook knows what is in scope:

```bash
export ENGAGEMENT_HOST=localhost:8080
```

Prove the hook works before you trust it. Ask the agent to fetch something out of
scope and watch it get blocked.
