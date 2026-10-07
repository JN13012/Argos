/*
 * Customer document upload.
 *
 * Identity documents and proof of address for onboarding and for disputes.
 * Files are written under the upload directory with a generated name so two
 * customers cannot collide, and the original name is kept only for display.
 */

const express = require("express");
const crypto = require("crypto");
const path = require("path");
const fs = require("fs");
const multer = require("multer");
const { q, one, all } = require("../db");
const { requireCustomer } = require("../middleware/auth");

const router = express.Router();

const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(__dirname, "..", "..", "uploads");
fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const ALLOWED = new Set(["application/pdf", "image/png", "image/jpeg"]);
const MAX_BYTES = 4 * 1024 * 1024;

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase().slice(0, 6);
    cb(null, `${crypto.randomBytes(12).toString("hex")}${ext}`);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: MAX_BYTES, files: 1 },
  fileFilter: (req, file, cb) => {
    if (!ALLOWED.has(file.mimetype)) return cb(new Error("unsupported file type"));
    cb(null, true);
  },
});

router.post("/api/documents", requireCustomer, (req, res) => {
  upload.single("document")(req, res, async (err) => {
    if (err) return res.status(400).json({ error: err.message });
    if (!req.file) return res.status(400).json({ error: "no file" });

    const kind = String(req.body.kind || "identity").slice(0, 40);
    const row = await one(
      `INSERT INTO documents (customer_id, kind, original_name, stored_path, byte_size)
       VALUES ($1,$2,$3,$4,$5) RETURNING id, kind, original_name, stored_path, byte_size, created_at`,
      [req.customer.id, kind, req.file.originalname, req.file.path, req.file.size]);
    res.json({ ok: true, document: row });
  });
});

router.get("/api/documents", requireCustomer, async (req, res) => {
  const rows = await all(
    `SELECT id, kind, original_name, stored_path, byte_size, created_at
       FROM documents WHERE customer_id = $1 ORDER BY id DESC`, [req.customer.id]);
  res.json(rows);
});

module.exports = router;
