/**
 * Jest tests for Node.js API
 */

const request = require("supertest")
const app = require("../server")

describe("API Server Tests", () => {
  describe("Health Check", () => {
    test("GET /health returns 200", async () => {
      const response = await request(app).get("/health")

      expect(response.status).toBe(200)
      expect(response.body).toHaveProperty("status", "healthy")
      expect(response.body).toHaveProperty("service")
      expect(response.body).toHaveProperty("version")
    })
  })

  describe("Bug Scanning", () => {
    test("POST /api/scan with valid code", async () => {
      const code = `
function test() {
  var x = 10;
  console.log(x);
}
      `

      const response = await request(app).post("/api/scan").send({ code })

      expect(response.status).toBe(200)
      expect(response.body).toHaveProperty("success", true)
      expect(response.body).toHaveProperty("results")
      expect(response.body.results).toHaveProperty("has_bugs")
      expect(response.body.results).toHaveProperty("confidence")
      expect(response.body.results).toHaveProperty("bugs_found")
    })

    test("POST /api/scan without code returns 400", async () => {
      const response = await request(app).post("/api/scan").send({})

      expect(response.status).toBe(400)
      expect(response.body).toHaveProperty("error")
    })

    test("POST /api/scan detects hardcoded secrets", async () => {
      const code = `
const apiKey = "sk-1234567890";
const password = "admin123";
      `

      const response = await request(app).post("/api/scan").send({ code })

      expect(response.status).toBe(200)
      expect(response.body.results.has_bugs).toBe(true)
      expect(response.body.results.total_issues).toBeGreaterThan(0)
    })

    test("POST /api/scan with different languages", async () => {
      const pythonCode = "password = 'test'"

      const response = await request(app).post("/api/scan").send({
        code: pythonCode,
        language: "python",
      })

      expect(response.status).toBe(200)
      expect(response.body.results.language).toBe("python")
    })
  })

  describe("Batch Scanning", () => {
    test("POST /api/scan/batch with multiple files", async () => {
      const files = [
        { filename: "test1.js", code: "var x = 10;" },
        { filename: "test2.js", code: "const y = 20;" },
      ]

      const response = await request(app).post("/api/scan/batch").send({ files })

      expect(response.status).toBe(200)
      expect(response.body).toHaveProperty("success", true)
      expect(response.body).toHaveProperty("total_files", 2)
      expect(response.body).toHaveProperty("results")
      expect(Array.isArray(response.body.results)).toBe(true)
    })

    test("POST /api/scan/batch without files returns 400", async () => {
      const response = await request(app).post("/api/scan/batch").send({})

      expect(response.status).toBe(400)
      expect(response.body).toHaveProperty("error")
    })
  })

  describe("Supported Languages", () => {
    test("GET /api/languages returns supported languages", async () => {
      const response = await request(app).get("/api/languages")

      expect(response.status).toBe(200)
      expect(response.body).toHaveProperty("supported")
      expect(Array.isArray(response.body.supported)).toBe(true)
      expect(response.body.supported).toContain("python")
      expect(response.body.supported).toContain("javascript")
    })
  })

  describe("Error Handling", () => {
    test("Invalid endpoint returns 404", async () => {
      const response = await request(app).get("/api/invalid")

      expect(response.status).toBe(404)
    })

    test("Large payload is handled", async () => {
      const largeCode = "x = 1;\n".repeat(10000)

      const response = await request(app).post("/api/scan").send({ code: largeCode })

      expect(response.status).toBe(200)
    })
  })
})

describe("Route Tests", () => {
  const scanRoutes = require("../routes/scan")

  describe("Quick Scan", () => {
    test("Quick scan detects basic issues", async () => {
      const code = `
password = "test123"
console.log("debug")
// TODO: fix this
      `

      const response = await request(app).post("/api/scan/quick").send({ code })

      expect(response.status).toBe(200)
      expect(response.body.scan_type).toBe("quick")
      expect(response.body.total_issues).toBeGreaterThan(0)
    })
  })

  describe("Deep Scan", () => {
    test("Deep scan provides detailed analysis", async () => {
      const code = `
function complex() {
  if (x) {
    for (let i = 0; i < 10; i++) {
      process(i);
    }
  }
}
      `

      const response = await request(app).post("/api/scan/deep").send({ code })

      expect(response.status).toBe(200)
      expect(response.body.scan_type).toBe("deep")
      expect(response.body.results).toHaveProperty("complexity_score")
      expect(response.body.results).toHaveProperty("maintainability_index")
    })
  })
})

describe("Performance Tests", () => {
  test("API responds within acceptable time", async () => {
    const start = Date.now()

    await request(app).get("/health")

    const duration = Date.now() - start

    expect(duration).toBeLessThan(100) // Less than 100ms
  })

  test("Concurrent requests are handled", async () => {
    const requests = Array(10)
      .fill()
      .map(() => request(app).get("/health"))

    const responses = await Promise.all(requests)

    responses.forEach((response) => {
      expect(response.status).toBe(200)
    })
  })
})
