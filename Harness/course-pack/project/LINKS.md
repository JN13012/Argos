# Reference

Things named in passing during the workshop, plus fixes for the traps.

## Traps with fixes

**Ollama picks its context window from detected VRAM.** The default is often far
smaller than the model supports, and your agent will silently truncate.
Set it explicitly: `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`, or `num_ctx` in
the Modelfile. Check what you actually got before blaming the model.

**Skill listings are not free.** Every skill name and description sits in context
on every turn under a budget. Past it, listings truncate and a skill silently stops
triggering. If a skill stops firing, check the listing before you debug the skill.

**Subagents are skipped silently** when the file has no name, a name containing a
colon or leading dash, or no description. Confirm it loaded before debugging its prompt.

**Quantisation kills tool calling before it kills prose.** 8 bit is close to free.
The jump to 4 bit is where structured tool calls start failing.

## Harnesses
Claude Code, OpenAI Codex CLI, Gemini CLI, Cursor, Aider, OpenHands, Cline, Windsurf.

## Security platforms and open source
XBOW, Horizon3 NodeZero, RunSybil, Mindfort, Terra. Open: Strix, PentestGPT, CAI.

## Frameworks
Claude Agent SDK, LangGraph, AutoGen, CrewAI, OpenAI Agents SDK, smolagents.

## Browser
Playwright MCP, Chrome DevTools MCP, Claude in Chrome, Browser Use, Stagehand.

## MCP servers
Burp (first party, works on Community), Caido community servers and Drift,
AWS managed MCP plus the awslabs collection, Azure MCP Server, Google Cloud,
ProjectDiscovery, Semgrep (in the main binary), Metasploit from Rapid7.
No first party server exists for Nmap or Shodan.

## Evals
claude plugin eval, promptfoo, Braintrust, Inspect (UK AISI), DeepEval, OpenAI Evals.

## Serving local models
Ollama, vLLM, LM Studio, llama.cpp.

## Cloud assessment
ScoutSuite (read only, safest first tool), Prowler, CloudFox, Pacu.

## Benchmarks worth bookmarking
aisi.gov.uk, cybergym.io, cvebench.com.
