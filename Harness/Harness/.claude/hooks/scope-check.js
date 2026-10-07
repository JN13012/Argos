#!/usr/bin/env node
"use strict";
/*
 * PreToolUse hook. Reads the tool call as JSON on stdin. Exit 0 allows, exit 2
 * blocks and hands stderr back to the model as the reason.
 *
 * Node instead of bash so this runs the same way on Windows, macOS and Linux
 * without WSL or git-bash on PATH -- Node is already guaranteed present,
 * because Claude Code itself needs it.
 *
 * What this checks: every URL/hostname it can find in a Bash command, a
 * browser navigate() call, a browser javascript_tool() script body, or a
 * WebFetch call, against engagements/<active>/scope.json's allowed_hosts.
 *
 * What this cannot guarantee: a javascript_tool script that builds a URL at
 * runtime from a variable, a redirect chain, or string concatenation will not
 * show up as a literal http(s):// substring here. This is a strong net
 * against the obvious and accidental cases -- typos, wrong subdomain,
 * copy-paste mistakes -- not a sandbox. Treat a pass from this hook as
 * necessary, not sufficient.
 */
const fs = require("fs");
const path = require("path");

function readStdin() {
  try { return fs.readFileSync(0, "utf8"); } catch (e) { return ""; }
}

function block(reason) {
  process.stderr.write("BLOCKED BY SCOPE: " + reason + "\n");
  process.exit(2);
}

function allow() {
  process.exit(0);
}

let input;
try {
  input = JSON.parse(readStdin() || "{}");
} catch (e) {
  block("could not parse hook input: " + e.message);
}

const toolName = input.tool_name || "";
const toolInput = input.tool_input || {};
const ROOT = process.cwd();

let currentEngagement;
try {
  currentEngagement = fs.readFileSync(path.join(ROOT, "CURRENT_ENGAGEMENT.md"), "utf8").trim();
} catch (e) {
  block('CURRENT_ENGAGEMENT.md missing or unreadable at "' + ROOT + '" -- cannot determine the active engagement, so no active testing.');
}

const scopePath = path.join(ROOT, "engagements", currentEngagement, "scope.json");
let scope;
try {
  scope = JSON.parse(fs.readFileSync(scopePath, "utf8"));
} catch (e) {
  block('scope.json missing or invalid for engagement "' + currentEngagement + '" (' + scopePath + '). Active testing requires a confirmed, machine-readable scope file.');
}

if (scope.confirmed !== true) {
  block('scope.json for "' + currentEngagement + '" is not confirmed:true. Widening or activating scope is a human decision made before a run, not during one.');
}

const allowedHosts = new Set(
  [].concat(scope.allowed_hosts || [], scope.callback_hosts || []).map((h) => String(h).toLowerCase())
);

function hostAllowed(host) {
  if (!host) return false;
  return allowedHosts.has(String(host).toLowerCase().split(":")[0]);
}

function extractHostsFromText(text) {
  const hosts = [];
  const re = /https?:\/\/([a-zA-Z0-9.\-]+)(?::\d+)?/g;
  let m;
  while ((m = re.exec(text)) !== null) hosts.push(m[1]);
  return hosts;
}

const isNav = /Claude_Browser__navigate$/.test(toolName);
const isJs = /Claude_Browser__javascript_tool$/.test(toolName);
const isFetch = /^WebFetch$/.test(toolName);
const isBash = toolName === "Bash";

let candidateText = "";
if (isBash) candidateText = toolInput.command || "";
else if (isNav) candidateText = toolInput.url || "";
else if (isJs) candidateText = toolInput.text || "";
else if (isFetch) candidateText = toolInput.url || "";
else allow(); // not a network-capable tool this hook governs

let hosts = extractHostsFromText(candidateText);

// navigate() accepts a bare host with no scheme ("example.com/path") too.
if (isNav && hosts.length === 0 && toolInput.url) {
  const raw = String(toolInput.url).trim();
  if (raw !== "back" && raw !== "forward") {
    const bare = raw.replace(/^\/\//, "").split("/")[0].split(":")[0];
    if (bare) hosts.push(bare);
  }
}

if (hosts.length === 0) allow(); // nothing to check (e.g. navigate("back"))

const offenders = hosts.filter((h) => !hostAllowed(h));
if (offenders.length > 0) {
  block(
    'host(s) not in scope for engagement "' + currentEngagement + '": ' + offenders.join(", ") +
    ". Allowed: " + Array.from(allowedHosts).join(", ") +
    ". This is a BLOCKED result: stop, do not retry with different wording."
  );
}

allow();
