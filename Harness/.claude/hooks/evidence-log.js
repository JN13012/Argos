#!/usr/bin/env node
"use strict";
/*
 * PostToolUse hook. This is the evidence backend that replaces Burp's proxy
 * history in the workshop's original design: it, not the model, assigns the
 * id and it, not the model, decides what the recorded body actually is. A
 * subagent can only cite an id that exists in evidence.jsonl, and Review
 * checks that at the end -- so a fabricated request id has nothing behind
 * it, same guarantee the course profile got from Burp, done natively.
 *
 * Fires after every Bash call and every browser call that can reach the
 * target (navigate, javascript_tool, computer, read_page, get_page_text) and
 * after WebFetch. Appends one line of JSON per call to
 * engagements/<active>/evidence/evidence.jsonl. Never blocks the run --
 * a logging failure is surfaced on stderr, not treated as a stop condition.
 */
const fs = require("fs");
const path = require("path");

function readStdin() {
  try { return fs.readFileSync(0, "utf8"); } catch (e) { return ""; }
}

let input;
try { input = JSON.parse(readStdin() || "{}"); } catch (e) { process.exit(0); }

const toolName = input.tool_name || "";
const toolInput = input.tool_input || {};
const toolResponse = input.tool_response !== undefined ? input.tool_response : input.tool_output;

const LOGGED = /^Bash$|Claude_Browser__(navigate|javascript_tool|computer|read_page|get_page_text)$|^WebFetch$/;
if (!LOGGED.test(toolName)) process.exit(0);

const ROOT = process.cwd();
let currentEngagement;
try {
  currentEngagement = fs.readFileSync(path.join(ROOT, "CURRENT_ENGAGEMENT.md"), "utf8").trim();
} catch (e) {
  process.exit(0); // no active engagement -- nothing to log evidence against
}

const evidenceDir = path.join(ROOT, "engagements", currentEngagement, "evidence");
try { fs.mkdirSync(evidenceDir, { recursive: true }); } catch (e) {}

const evidencePath = path.join(evidenceDir, "evidence.jsonl");
const counterPath = path.join(evidenceDir, ".evidence_seq");

let seq = 0;
try { seq = parseInt(fs.readFileSync(counterPath, "utf8"), 10) || 0; } catch (e) {}
seq += 1;
try { fs.writeFileSync(counterPath, String(seq)); } catch (e) {}

const id = "ev_" + String(seq).padStart(6, "0");
const record = {
  id,
  ts: new Date().toISOString(),
  tool: toolName,
  input: toolInput,
  response: toolResponse,
};

try {
  fs.appendFileSync(evidencePath, JSON.stringify(record) + "\n");
} catch (e) {
  process.stderr.write("evidence-log: failed to write " + evidencePath + ": " + e.message + "\n");
}

process.exit(0);
