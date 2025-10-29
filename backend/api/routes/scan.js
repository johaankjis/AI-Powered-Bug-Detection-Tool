/**
 * Scan routes for bug detection
 * Modular route handlers for code analysis
 */

const express = require("express")
const router = express.Router()

// Rate limiting helper (simplified for MVP)
const requestCounts = new Map()

function rateLimit(req, res, next) {
  const ip = req.ip
  const now = Date.now()
  const windowMs = 60000 // 1 minute
  const maxRequests = 30

  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, [])
  }

  const requests = requestCounts.get(ip).filter((time) => now - time < windowMs)
  requests.push(now)
  requestCounts.set(ip, requests)

  if (requests.length > maxRequests) {
    return res.status(429).json({
      error: "Too many requests",
      message: "Please try again later",
    })
  }

  next()
}

// Apply rate limiting to all routes
router.use(rateLimit)

// Quick scan endpoint (fast pattern matching only)
router.post("/quick", async (req, res) => {
  const { code } = req.body

  if (!code) {
    return res.status(400).json({ error: "Code is required" })
  }

  // Quick pattern-based checks
  const quickIssues = []
  const lines = code.split("\n")

  const patterns = [
    { regex: /password\s*=\s*['"]/, severity: "critical", msg: "Hardcoded password" },
    { regex: /console\.log/, severity: "low", msg: "Console log statement" },
    { regex: /TODO|FIXME/, severity: "medium", msg: "Unresolved comment" },
  ]

  lines.forEach((line, idx) => {
    patterns.forEach(({ regex, severity, msg }) => {
      if (regex.test(line)) {
        quickIssues.push({
          line: idx + 1,
          severity,
          message: msg,
          code: line.trim(),
        })
      }
    })
  })

  res.json({
    success: true,
    scan_type: "quick",
    total_issues: quickIssues.length,
    issues: quickIssues,
    scan_time_ms: 10,
  })
})

// Deep scan endpoint (full ML analysis)
router.post("/deep", async (req, res) => {
  const { code, options = {} } = req.body

  if (!code) {
    return res.status(400).json({ error: "Code is required" })
  }

  // Simulate deep analysis with ML model
  const deepResults = {
    has_bugs: true,
    confidence: 0.92,
    total_issues: 5,
    complexity_score: 7.5,
    maintainability_index: 65,
    bugs_found: [
      {
        line: 10,
        severity: "high",
        message: "Potential null pointer exception",
        suggestion: "Add null check before accessing property",
        type: "ml_prediction",
      },
    ],
    code_metrics: {
      cyclomatic_complexity: 8,
      lines_of_code: code.split("\n").length,
      comment_ratio: 0.15,
    },
  }

  res.json({
    success: true,
    scan_type: "deep",
    results: deepResults,
    scan_time_ms: 250,
  })
})

// Get scan history (mock data for MVP)
router.get("/history", (req, res) => {
  const mockHistory = [
    {
      id: "scan_001",
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      files_scanned: 5,
      bugs_found: 12,
      status: "completed",
    },
    {
      id: "scan_002",
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      files_scanned: 3,
      bugs_found: 7,
      status: "completed",
    },
  ]

  res.json({
    success: true,
    history: mockHistory,
    total_scans: mockHistory.length,
  })
})

module.exports = router
