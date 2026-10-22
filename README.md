
☀️ Solar Planning Platform: Architecture & Overview
Welcome to the Solar Planning Web Application repository. This project is a comprehensive, microservice-based platform designed for automated photovoltaic (PV) analysis, rooftop measurement, and solar array planning.

🏗️ System Architecture
The application is built on a decoupled, service-oriented architecture. A central API Proxy acts as the orchestrator, seamlessly routing data between the frontend and several specialized backend microservices:

PV Analysis Service: Calculates solar irradiance, potential energy yield, and system efficiency.

Satellite Imagery Service: Ingests and processes high-resolution geospatial and satellite data.

Rooftop Detection Service: Utilizes computer vision algorithms to automatically identify, segment, and measure roof boundaries and usable surface area.

3D Modeling Service: Generates interactive, 3-dimensional representations of the target structures and planned solar arrays.

🔄 Core Workflow
The primary data flow for the application operates as follows:

User Configuration: The user selects a geographic location and defines their desired solar system parameters via the frontend interface.

Proxy Orchestration: The frontend submits these parameters to the central API Proxy.

Data Aggregation: The Proxy securely coordinates with the backend services to fetch localized satellite imagery and baseline solar data.

Analysis & Measurement: The Rooftop Detection service analyzes the imagery to extract physical roof dimensions, while the PV service calculates energy potential.

Rendering & Response: The fully aggregated dataset—including the generated 3D models and financial/energy metrics—is returned to the frontend for interactive user display.

🛠️ Standalone Modules & Tools
In addition to the primary web application, this repository provides standalone entry points for testing and modular development:

Simulation Engine: A headless entry point to run localized PV yield simulations independent of the UI.

3D Model Viewer: An isolated rendering environment for visualizing and debugging generated structural models.

(Note: This repository focuses on the core orchestration and integration of these services. Documentation regarding specific frontend components or internal service logic is provided where cross-module integration occurs.)

# How To Run The Application
## AI 
```
uvicorn rooftop_fastapi:app --port 8005 --reload  
```

## Backend
```
node index.js
```

## Frontend
```
npm run dev
```

## pv simulation
```
python .\main_v2.py 
```

## satellite
```
python .\satellite_zoom_server.py
```

## stl 
```
uvicorn api:app --port 8007 --reload
```
for simulation
```
python .\web.py
```

