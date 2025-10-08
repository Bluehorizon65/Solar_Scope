#!/usr/bin/env node
/**
 * Proxy Backend Server for Solar PV System Calculator + Satellite Data + Rooftop Detection
 * Runs on port 3000
 */

import express from "express";
import axios from "axios";
import fs from "fs";
import path from "path";

const app = express();
const PORT = 3000;

const CALCULATOR_API = "http://localhost:8001/calculate";
const SATELLITE_API = "http://localhost:8000/satellite";
const ROOFTOP_API = "http://localhost:8005/detect-rooftop";

const SATELLITE_FOLDER = "C:\\Users\\Enemb\\OneDrive\\Documents\\google_hackathon_satalite\\satellite_images";

// Middleware
app.use(express.json());

// Root endpoint for health check
app.get("/", (req, res) => {
  res.json({
    message: "Backend proxy for Solar PV Calculator, Satellite & Rooftop API",
    forward_to: [CALCULATOR_API, SATELLITE_API, ROOFTOP_API],
  });
});

// POST /solar -> call Calculator + Satellite + Rooftop Detection
app.post("/solar", async (req, res) => {
  try {
    const inputData = req.body;

    // --- Prepare PV Calculator payload ---
    const calculatorPayload = {
      latitude: inputData.latitude,
      longitude: inputData.longitude,
      system_capacity_kw: inputData.system_capacity_kw,
      year: inputData.year,
      optimize_orientation: inputData.optimize_orientation,
      electricity_rate_inr: inputData.electricity_rate_inr,
      budget_inr: inputData.budget_inr,
      prefer_brand: inputData.prefer_brand,
      max_payback_years: inputData.max_payback_years,
      num_panels: inputData.num_panels,
    };

    // --- Prepare Satellite payload using client input ---
    const satellitePayload = {
      latitude: inputData.latitude,
      longitude: inputData.longitude,
      location_name: inputData.location_name || "unknown",
      zoom_level: inputData.zoom_level || 6,
    };

    // --- Call Calculator and Satellite APIs concurrently ---
    const [calcResponse, satelliteResponse] = await Promise.all([
      axios.post(CALCULATOR_API, calculatorPayload, { headers: { "Content-Type": "application/json" } }),
      axios.post(SATELLITE_API, satellitePayload, { headers: { "Content-Type": "application/json" } }),
    ]);

    // --- Pick any image from satellite_images folder ---
    const imageFiles = fs.readdirSync(SATELLITE_FOLDER).filter(file => {
      const ext = path.extname(file).toLowerCase();
      return ext === ".png" || ext === ".jpg" || ext === ".jpeg";
    });

    if (imageFiles.length === 0) {
      return res.status(404).json({ detail: "No images found in satellite_images folder" });
    }

    const savedImagePath = path.join(SATELLITE_FOLDER, imageFiles[0]);
    console.log("Using satellite image for rooftop detection:", savedImagePath);

    // --- Call Rooftop Detection API ---
    const rooftopPayload = {
      image_path: savedImagePath,
      num_panels: inputData.num_panels,
    };

    const rooftopResponse = await axios.post(ROOFTOP_API, rooftopPayload, { headers: { "Content-Type": "application/json" } });

    // --- Merge all results ---
    const result = {
      success: true,
      message: "Combined response from Solar Calculator, Satellite API, and Rooftop Detection",
      calculator_result: calcResponse.data,
      satellite_result: satelliteResponse.data,
      rooftop_result: rooftopResponse.data,
    };

    res.status(200).json(result);

  } catch (error) {
    console.error("Error in /solar route:", error.message);

    if (error.response) {
      res.status(error.response.status).json({
        detail: `Error from remote API: ${error.response.statusText}`,
        data: error.response.data,
      });
    } else if (error.request) {
      res.status(504).json({
        detail: "No response received from one or more APIs",
        hint: "Ensure all remote APIs (8000, 8001, 8005) are running",
      });
    } else {
      res.status(500).json({
        detail: "Internal proxy error",
        message: error.message,
      });
    }
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`✅ Proxy backend running on http://localhost:${PORT}`);
  console.log(`📡 Forwarding requests to ${CALCULATOR_API}, ${SATELLITE_API}, and ${ROOFTOP_API}`);
});
