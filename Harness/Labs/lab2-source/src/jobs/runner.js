/*
 * The batch runner.
 *
 * Scheduled jobs are small Node scripts in this directory. Operations can add
 * a job, point it at one of those tasks, and give it per job settings; the
 * runner starts the task as its own process so a job that falls over cannot
 * take the platform with it, and captures whatever it writes so there is
 * something to look at afterwards.
 *
 * The task is never passed through a shell. It is looked up against the tasks
 * that actually exist on disk and started with execFile, so nothing a job
 * carries can be interpreted as a command.
 */

const { execFile } = require("child_process");
const fs = require("fs");
const path = require("path");
const { q, one } = require("../db");

const TASK_DIR = __dirname;
const RUN_TIMEOUT_MS = 20000;
const MAX_OUTPUT = 64 * 1024;

/* Only files that are here, and only ones meant to be run on their own. */
function availableTasks() {
  return fs
    .readdirSync(TASK_DIR)
    .filter((f) => f.endsWith(".js") && f !== "runner.js")
    .map((f) => f.replace(/\.js$/, ""));
}

/*
 * Settings a job carries are checked before the task is started. A value may
 * only hold characters that cannot be used to break out of an argument, so a
 * job cannot smuggle a second command into the one we are running.
 */
const SAFE_VALUE = /^[A-Za-z0-9 _\-.,:/=+]{0,512}$/;

function environmentFor(job) {
  const env = {
    PATH: process.env.PATH,
    HOME: process.env.HOME,
    NODE_ENV: process.env.NODE_ENV || "production",
    DB_HOST: process.env.DB_HOST,
    DB_PORT: process.env.DB_PORT,
    DB_USER: process.env.DB_USER,
    DB_PASSWORD: process.env.DB_PASSWORD,
    DB_NAME: process.env.DB_NAME,
    JOB_NAME: job.name,
  };

  for (const [name, value] of Object.entries(job.env || {})) {
    if (typeof value !== "string") continue;
    if (!SAFE_VALUE.test(value)) continue;
    env[name] = value;
  }
  return env;
}

async function runJob(jobId, startedBy) {
  const job = await one("SELECT * FROM scheduled_jobs WHERE id = $1", [jobId]);
  if (!job) throw new Error("no such job");
  if (!job.enabled) throw new Error("job is disabled");

  if (!availableTasks().includes(job.task)) {
    throw new Error("unknown task");
  }
  const taskPath = path.join(TASK_DIR, `${job.task}.js`);

  const run = await one(
    "INSERT INTO job_runs (job_id, started_by) VALUES ($1,$2) RETURNING id",
    [jobId, startedBy || null]);

  return new Promise((resolve) => {
    execFile(
      process.execPath,
      [taskPath],
      { env: environmentFor(job), timeout: RUN_TIMEOUT_MS, maxBuffer: MAX_OUTPUT },
      async (err, stdout, stderr) => {
        const output = `${stdout || ""}${stderr || ""}`.slice(0, MAX_OUTPUT);
        const code = err && typeof err.code === "number" ? err.code : err ? 1 : 0;
        await q(
          "UPDATE job_runs SET finished_at = NOW(), exit_code = $1, output = $2 WHERE id = $3",
          [code, output, run.id]);
        resolve({ run_id: run.id, exit_code: code, output });
      }
    );
  });
}

module.exports = { runJob, availableTasks };
