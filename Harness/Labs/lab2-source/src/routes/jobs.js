/*
 * Scheduled job administration.
 *
 * Operations own the batch schedule. Jobs name a task that ships with the
 * platform and may carry settings the task reads, which is how the same task
 * serves several jobs: the accrual task runs at one rate for savings and
 * another for the notice accounts.
 *
 * Mounted under /api/ops, so the staff area gate applies.
 */

const express = require("express");
const { q, one, all } = require("../db");
const { runJob, availableTasks } = require("../jobs/runner");
const { scheduledJob } = require("../schemas");

const router = express.Router();

router.get("/api/ops/jobs", async (req, res) => {
  const rows = await all(
    `SELECT j.*, (SELECT MAX(started_at) FROM job_runs r WHERE r.job_id = j.id) AS last_run
       FROM scheduled_jobs j ORDER BY j.id`);
  res.json({ jobs: rows, tasks: availableTasks() });
});

router.post("/api/ops/jobs", async (req, res) => {
  const parsed = scheduledJob.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: "invalid job" });
  const { name, task, env } = parsed.data;

  if (!availableTasks().includes(task)) {
    return res.status(400).json({ error: "unknown task", tasks: availableTasks() });
  }

  const row = await one(
    `INSERT INTO scheduled_jobs (name, task, env, created_by)
     VALUES ($1,$2,$3::jsonb,$4) RETURNING *`,
    [name, task, JSON.stringify(env || {}), req.customer ? req.customer.id : null]);
  res.json({ ok: true, job: row });
});

router.patch("/api/ops/jobs/:id", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "bad job" });

  const job = await one("SELECT * FROM scheduled_jobs WHERE id = $1", [id]);
  if (!job) return res.status(404).json({ error: "job not found" });

  const env = req.body.env && typeof req.body.env === "object" ? req.body.env : job.env;
  const enabled = typeof req.body.enabled === "boolean" ? req.body.enabled : job.enabled;

  const row = await one(
    "UPDATE scheduled_jobs SET env = $1::jsonb, enabled = $2 WHERE id = $3 RETURNING *",
    [JSON.stringify(env), enabled, id]);
  res.json({ ok: true, job: row });
});

router.post("/api/ops/jobs/:id/run", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  if (!Number.isInteger(id)) return res.status(400).json({ error: "bad job" });
  try {
    const result = await runJob(id, req.customer ? req.customer.id : null);
    res.json({ ok: true, ...result });
  } catch (e) {
    res.status(400).json({ error: e.message });
  }
});

router.get("/api/ops/jobs/:id/runs", async (req, res) => {
  const id = parseInt(req.params.id, 10);
  const rows = await all(
    `SELECT id, started_at, finished_at, exit_code, output
       FROM job_runs WHERE job_id = $1 ORDER BY id DESC LIMIT 20`, [id]);
  res.json(rows);
});

module.exports = router;
