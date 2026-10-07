# Before the workshop: set this up in advance

**Supercharging Your Pentesting With AI**

Please do this **before** the session starts. There is one multi-gigabyte download here and
thirty of us pulling it at once over the same connection will not work. Fifteen minutes of
prep tonight buys you the whole day tomorrow.

If you only do one thing, do **step 2**. It is the only large download and the one that takes
longest.

There is no Docker in this list and Windows users do not need WSL. Four steps, one of them
slow, the rest instant.

---

## 1. Claude Code

You will get a seat invitation by email. Accept it, then:

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

First run opens a browser to sign in. Confirm you get a version number and a prompt that
answers you.

**Size:** small. **Time:** 2 minutes.

---

## 2. Ollama and a local model

Install Ollama from **ollama.com** (normal Mac/Windows installer).

**First, check how much memory your machine has.** Apple menu, About This Mac. It changes
which model you pull.

### If you have 24 GB or more

```bash
ollama pull qwen3.5:9b
printf 'FROM qwen3.5:9b\nPARAMETER num_ctx 32768\n' > Modelfile
ollama create qwen3.5:9b-32k -f Modelfile
```

### If you have 16 GB, use the smaller model

```bash
ollama pull qwen3.5:4b
printf 'FROM qwen3.5:4b\nPARAMETER num_ctx 32768\n' > Modelfile
ollama create qwen3.5:4b-32k -f Modelfile
```

The 9b model holds 6.6 GB of memory while it is loaded. Add your browser, your editor and the
call you are watching this on, and a 16 GB machine starts swapping. It does not crash, it just
gets slow at the exact moment you need it. The 4b model is 3.4 GB and leaves room. It is a
weaker model and on 16 GB that is the right trade.

Either way, line 1 is the slow part. Lines 2 and 3 take about five seconds and download
nothing.

**Why lines 2 and 3 exist:** Ollama defaults every model to a 4,096 token context window,
which is too small to hold tool definitions plus a working conversation. At 4,096 the tool
schemas get truncated out of the prompt and the model stops emitting valid tool calls, which
looks like the model being stupid rather than the window being short. Those two lines make a
copy of the model with a 32,768 token window. Use the `-32k` tag you just created from then
on, not the plain one.

Setting `OLLAMA_CONTEXT_LENGTH` as an environment variable does not work on macOS, because the
Ollama app starts its own server process that does not inherit it. The derived tag works on
every platform, which is why we do it this way.

Check it worked:

```bash
ollama list
```

You should see your `-32k` tag.

**Size:** 6.6 GB for 9b, 3.4 GB for 4b. **Time:** 15 to 40 minutes. **Start this first.**

**Hardware:** 16 GB of unified memory is the practical floor, using the 4b model. 8 GB will
not work well even with 4b. Intel Macs have no GPU path for this and will be too slow to sit
inside an agent loop.

**If your machine cannot run a local model**, come anyway. You will follow the configuration
with me and point at a hosted endpoint instead. Tell me at the start so I know.

Model page: https://ollama.com/library/qwen3.5

---

## 3. Python 3

The harness we run in the second half is a single Python file using nothing outside the
standard library. No pip install, no virtualenv, no packages.

```bash
python3 --version
```

Anything 3.9 or newer is fine. macOS and most Linux distributions already have it. On Windows,
install it from python.org and tick "Add python.exe to PATH" during setup.

**Size:** none, or 30 MB on Windows. **Time:** 1 minute.

---

## 4. Command line tools

Most of you will have these. Check and fill gaps:

```bash
curl --version
jq --version
git --version
feroxbuster --version
```

If `jq` is missing: `brew install jq` on macOS, `apt install jq` on Debian or Ubuntu,
`winget install jqlang.jq` on Windows.

**`feroxbuster` is the one you probably do not have.** It is the content discovery tool we use for
recon, and the preconfigured project expects it:

```bash
brew install feroxbuster          # macOS
apt install feroxbuster           # Debian, Ubuntu
```

On Windows, download the release binary from github.com/epi052/feroxbuster and put it on your
PATH. **Size:** about 15 MB. **Time:** 2 minutes.

---

## Checklist

Run these four and you are ready:

```bash
claude --version
ollama list            # should show your -32k tag
python3 --version
jq --version
feroxbuster --version
```

---

## What you do NOT need to do

- **No Docker.** Nothing in this course runs in a container.
- **No WSL on Windows.** Every command in this course runs in PowerShell or your normal
  terminal.
- **No repository to clone.** We build every configuration file together, live, on screen.
  You will write them yourself rather than copying mine.
- **No harness to download.** You get one Python file from me at the start of exercise 5. We
  read it together before we run it, which is the point of that exercise.
- **No lab setup.** You claim your lab environment at the start of the session and it
  provisions while we talk.

---

## If something will not install

Post it in the workshop chat before the day if you can, or at the very start of the session. A
TryHackMe team member is monitoring chat throughout and we will work through it while the
class continues.

Nothing in exercises 1 through 4 needs Ollama or the local model, so a failed install there
does not cost you the morning. That is the first two thirds of the day.

---

# Using the harness

You get one Python file, `agent.py`. Nothing to install: it uses only the Python
standard library and talks to the Ollama you set up in step 2.

Set your model tag once per terminal. Use the tag **you** created in step 2:

```bash
export AGENT_MODEL=qwen3.5:9b-32k      # or qwen3.5:4b-32k on a 16 GB machine
```

Run it from whatever folder you want the output in. It writes `findings.jsonl` and
`notes.md` into the **current directory**, not next to the script.

## Source mode — reading code, no target needed

```bash
MODE=source AGENT_REPO=/path/to/the/source \
  python3 agent.py "Find endpoints with a missing authorization check"
```

Point `AGENT_REPO` at the **root** of the source, not a subfolder. Given a subfolder it
will burn its turn budget hunting for files it is not allowed to reach.

## Web mode — testing a running application

```bash
export AGENT_TARGET=https://your-lab-address
MODE=web python3 agent.py "Test /orders/{id} for broken object level authorization"
```

It will only talk to the host in `AGENT_TARGET`. That is enforced in the file, and
nothing it does at runtime can widen it.

## Both at once — source and the running app together

```bash
MODE=both AGENT_REPO=/path/to/the/source AGENT_TARGET=https://your-lab-address \
  python3 agent.py "Read the source to find endpoints with no authorization check, then prove it against the running application"
```

## What you will see

Numbered tool calls, one per line, then a stop. Three things are normal and worth
watching for, because they are the harness doing its job:

- **`no such tool 'fetch'`** — the model invented a tool it does not have and was refused.
- **`REJECTED: no such request id`** — it tried to cite evidence it never collected. In
  source mode findings are cited with `file_path`, not request ids.
- **`turn cap reached, stopping.`** — it hit a stopping rule rather than running forever.

Then read `findings.jsonl`. A local 9B model is not going to hand you a finished report;
the point is watching where it goes wrong and why the limits exist.

## If it does nothing

```bash
ollama list                 # your -32k tag must be here
curl http://localhost:11434/v1/models
```

If the second command fails, Ollama is not running. Open the Ollama app.
