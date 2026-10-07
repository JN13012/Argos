# The engagement profile

Copy this directory over your engagement working directory, fill in `scope.md`, export
`ENGAGEMENT_HOST`, then prove the hook blocks an out of scope request before you trust
any of it.

```
CLAUDE.md                     Engagement rules. Shapes behaviour, enforces nothing.
scope.md                      The scope document the hook reads. The agent cannot write to it.
.claude/
  settings.json               Allow and deny rules, defaultMode, hook registration
  rules/
    evidence.md               Path scoped: loads when a findings file is read
    class-prompts.md          Path scoped: loads when a per class prompt is read
  hooks/scope-check.sh        The one layer that is not a request to the model
  skills/recon/SKILL.md       The worked security skill
  agents/
    bola-hunter.md            One subagent per class. Each one is a thin loader:
    bfla-hunter.md            identity, scope, identities held, then a pointer to
    injection-hunter.md       prompts/classes/<slug>.md and the shared schema.
    ssrf-hunter.md
```

Set the engagement host before you start, because the hook defaults to `localhost:8080`
and a wrong default is a hook that blocks everything or nothing:

```bash
export ENGAGEMENT_HOST=localhost:8080
```

## Why the deny list looks like this

JSON has no comments, so the reasoning for `.claude/settings.json` lives here. Read this
section next to that file. Five things are going on.

### 1. `Read(**/credentials*)` was never a secrets rule

It reads like one and it is not. It matches a file whose basename starts with the word
`credentials` and nothing else. Every one of these got straight past it:

| What it is | Why the old rule missed it |
|---|---|
| `playwright/.auth/user.json` | A saved browser session. The word `credentials` appears nowhere in the path. |
| `~/.aws/credentials` | Outside the project, and the old rule was never anchored anywhere that reached it. |
| `.env.local` | `.env` was denied by exact name. `.env.local`, `.env.test` and `app.env` were not. |
| A token store | `~/.claude/.credentials.json`, `.netrc`, `.git-credentials`, `.npmrc`, a `*.token` file. Leading dots and different words. |

The replacement names the shapes rather than a single word: `.env` and every suffix of
it, `.auth/`, the cloud provider config directories, the SSH directory and private key
filenames, and the specific token stores by name. It is longer on purpose. A secrets
deny list is an inventory, and an inventory you can read is the only kind that stays
correct.

`Read(//proc/**)` is in there for a published reason. In June 2026 Microsoft Threat
Intelligence showed the Bash tool being protected by environment scrubbing while the Read
tool was not, so an injected instruction to read `/proc/self/environ` handed over
`ANTHROPIC_API_KEY`. The environment is a file on Linux, so it belongs in a file deny list.

### 2. An allowed interpreter is an allowed everything

This profile allows `Bash(curl:*)` and denies `WebFetch`. That pairing looks like an
egress policy and it is not. The deny stops one tool. It holds only because no
interpreter is allowed, and the moment somebody adds `Bash(python3:*)` for a quick
one liner, two things break at once:

- Egress is back. `python3 -c "import urllib.request; ..."` reaches anything routable,
  and no rule named `WebFetch` has any bearing on it.
- The scope hook goes blind. `scope-check.sh` greps the command text for a URL. A URL
  built at runtime from a variable is not in the command text, so there is nothing to
  grep and the hook exits 0.

That is why the deny list names `python`, `python3`, `node`, `ruby`, `perl`, `php`, `sh`,
`bash`, `zsh`, `xargs` and `env`. `env` and `xargs` are there because both launch another
program with a fresh argument vector, which is the same hole wearing a different name.
`wget`, `nc`, `ncat`, `socat` and `ssh` are there because each is its own egress path.

### 3. The agent must not be able to edit its own enforcement

`defaultMode` is `acceptEdits`, which is the right call for a lab: the recon skill writes
`surface.json` and the subagents write findings, and nobody wants to click yes for twenty
minutes. But `acceptEdits` auto approves every write, including a write to `scope.md`.

So `scope.md`, `CLAUDE.md` and the whole of `.claude/` are denied to `Edit` and `Write`.
Scope is decided before the run starts and there is no runtime path to widen it. A hook
that reads a scope file the agent can rewrite is not enforcement, it is a suggestion with
extra steps.

### 4. The order the rules are evaluated in

A PreToolUse hook exiting 2 stops the call before any permission rule is evaluated. Then
deny, then ask, then allow. First match wins and specificity never changes that order, so
an allow rule can never carve an exception out of a deny. This is why the interpreter
denies above are safe to write broadly: nothing in the allow list can reopen them.

Only exit code 2 blocks. Exit 1 is a non blocking error and the tool still runs, which is
why `scope-check.sh` exits 2 rather than 1 when `jq` is missing. A policy hook that fails
open is not a policy.

### 5. What this list does not do, said plainly

Bash rules match the command text the model writes. They are a guardrail, not a boundary.
Put `Bash(curl:*)` in deny and a request still goes out through `/usr/bin/curl`, because
that is a different command string. The list raises the cost of routing around scope and
it makes the intent of the profile legible to a reviewer. It does not contain a
determined process.

Two consequences worth holding on to:

- The boundary is the hook plus whatever network control sits under the machine, and the
  hook is only as good as what it can parse.
- `Read` denies do not cover `Bash`. Nothing here stops `cat ~/.aws/credentials`. That
  file is only safe because `cat` is not in the allow list and an unallowed Bash call
  stops for a prompt, which is a workable control while you are watching a lab and not
  one in an unattended run.

`WebSearch` is allowed on purpose, for CVE and version lookups mid engagement. It brings
untrusted page text into context, so treat everything it returns as data and never as an
instruction.
