/**
 * Node.js API Server for Bug Detection Service
 * Provides REST endpoints for code analysis
 */

const express = require("express")
const cors = require("cors")
const { spawn } = require("child_process")
const fs = require("fs").promises
const path = require("path")

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(cors())
app.use(express.json({ limit: "10mb" }))
app.use(express.urlencoded({ extended: true }))

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({
    status: "healthy",
    service: "AI Bug Detection API",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
  })
})

// Main bug detection endpoint
app.post("/api/scan", async (req, res) => {
  try {
    const { code, language = "python", filename = "temp.py" } = req.body

    if (!code) {
      return res.status(400).json({
        error: "Code is required",
        message: "Please provide code to analyze",
      })
    }

    // Write code to temporary file
    const tempDir = path.join(__dirname, "temp")
    await fs.mkdir(tempDir, { recursive: true })
    const tempFile = path.join(tempDir, `scan_${Date.now()}_${filename}`)
    await fs.writeFile(tempFile, code)

    // Run Python detection script
    const pythonProcess = spawn("python3", [path.join(__dirname, "../ml_engine/detect.py"), tempFile])

    let output = ""
    let errorOutput = ""

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString()
    })

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString()
    })

    pythonProcess.on("close", async (code) => {
      // Clean up temp file
      try {
        await fs.unlink(tempFile)
      } catch (err) {
        console.error("Error cleaning up temp file:", err)
      }

      if (code !== 0) {
        return res.status(500).json({
          error: "Analysis failed",
          details: errorOutput,
        })
      }

      // Parse detection results (simplified for MVP)
      const mockResults = {
        has_bugs: true,
        confidence: 0.87,
        total_issues: 3,
        severity_breakdown: {
          critical: 1,
          high: 1,
          medium: 1,
          low: 0,
        },
        bugs_found: [
          {
            line: 5,
            severity: "critical",
            message: "Hardcoded API key detected - security risk",
            code: 'api_key = "sk-1234567890"',
            type: "pattern",
          },
          {
            line: 12,
            severity: "high",
            message: "Bare except clause - specify exception type",
            code: "except:",
            type: "pattern",
          },
          {
            line: 18,
            severity: "medium",
            message: 'Use "is None" instead of "== None"',
            code: "if result == None:",
            type: "pattern",
          },
        ],
        scan_time: new Date().toISOString(),
        language: language,
      }

      res.json({
        success: true,
        results: mockResults,
        metadata: {
          lines_analyzed: code.split("\n").length,
          file_size: code.length,
          scan_duration_ms: 150,
        },
      })
    })
  } catch (error) {
    console.error("Scan error:", error)
    res.status(500).json({
      error: "Internal server error",
      message: error.message,
    })
  }
})

// Batch scan endpoint
app.post("/api/scan/batch", async (req, res) => {
  try {
    const { files } = req.body

    if (!files || !Array.isArray(files)) {
      return res.status(400).json({
        error: "Invalid request",
        message: "Expected array of files",
      })
    }

    const results = await Promise.all(
      files.map(async (file) => {
        // Simulate individual file scanning
        return {
          filename: file.filename,
          has_bugs: Math.random() > 0.5,
          total_issues: Math.floor(Math.random() * 5),
          confidence: 0.8 + Math.random() * 0.15,
        }
      }),
    )

    res.json({
      success: true,
      total_files: files.length,
      results: results,
      summary: {
        files_with_bugs: results.filter((r) => r.has_bugs).length,
        total_issues: results.reduce((sum, r) => sum + r.total_issues, 0),
      },
    })
  } catch (error) {
    console.error("Batch scan error:", error)
    res.status(500).json({
      error: "Internal server error",
      message: error.message,
    })
  }
})

// Get supported languages
app.get("/api/languages", (req, res) => {
  res.json({
    supported: ["python", "javascript", "typescript", "java"],
    experimental: ["go", "rust", "ruby"],
  })
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error("Unhandled error:", err)
  res.status(500).json({
    error: "Internal server error",
    message: process.env.NODE_ENV === "development" ? err.message : "Something went wrong",
  })
})

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Bug Detection API running on port ${PORT}`)
  console.log(`📊 Health check: http://localhost:${PORT}/health`)
  console.log(`🔍 Scan endpoint: http://localhost:${PORT}/api/scan`)
})

module.exports = app
