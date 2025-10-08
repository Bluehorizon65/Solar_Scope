from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import cv2
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image
import os
import tempfile
from typing import Optional

app = FastAPI(title="Rooftop Detection & Solar Panel Placement API", version="1.0.0")

# Configuration
TOLERANCE_VALUES = [3, 2]
METERS_PER_PIXEL = 0.15  # For Google Maps zoom level 20

def detect_rooftops_targeted(image, tolerance_values):
    """Detect rooftops in the image using targeted color detection"""
    rooftop_masks = []
    
    for tolerance in tolerance_values:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        rooftop_colors = [
            ([110, 50, 50], [130, 255, 255]),   # Blue
            ([0, 0, 50], [180, 30, 200]),       # Gray
            ([10, 100, 100], [25, 255, 255]),   # Orange/Brown
            ([20, 50, 50], [40, 255, 255]),     # Yellow/Tan
            ([0, 50, 50], [10, 255, 255]),      # Red
            ([160, 50, 50], [180, 255, 255]),   # Red (wrap-around)
        ]
        
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for (lower, upper) in rooftop_colors:
            lower = np.array([max(0, lower[0] - tolerance), max(0, lower[1] - tolerance), max(0, lower[2] - tolerance)])
            upper = np.array([min(179, upper[0] + tolerance), min(255, upper[1] + tolerance), min(255, upper[2] + tolerance)])
            
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        rooftop_masks.append(combined_mask)
    
    final_mask = np.zeros_like(rooftop_masks[0])
    for mask in rooftop_masks:
        final_mask = cv2.bitwise_or(final_mask, mask)
    
    return final_mask

def place_solar_panels_custom(image, rooftop_mask, target_panels):
    """Place solar panels on detected rooftops with adaptive sizing"""
    result_image = image.copy()
    h, w = rooftop_mask.shape
    
    panel_configs = [
        {"size": (40, 25), "gap": 3, "color": (255, 0, 0), "min_coverage": 0.4},
        {"size": (30, 20), "gap": 2, "color": (255, 0, 0), "min_coverage": 0.3},
        {"size": (20, 15), "gap": 1, "color": (255, 0, 0), "min_coverage": 0.25},
        {"size": (12, 8), "gap": 1, "color": (255, 0, 0), "min_coverage": 0.15}
    ]
    
    for config in panel_configs:
        panel_w, panel_h = config["size"]
        gap = config["gap"]
        color = config["color"]
        
        panels_placed = 0
        
        for y in range(0, h - panel_h, panel_h + gap):
            for x in range(0, w - panel_w, panel_w + gap):
                if panels_placed >= target_panels:
                    break
                
                panel_region = rooftop_mask[y:y+panel_h, x:x+panel_w]
                coverage = np.sum(panel_region == 255) / (panel_w * panel_h)
                
                if coverage >= config["min_coverage"]:
                    cv2.rectangle(result_image, (x, y), (x + panel_w, y + panel_h), color, -1)
                    panels_placed += 1
            
            if panels_placed >= target_panels:
                break
        
        if panels_placed >= target_panels:
            return result_image, panels_placed
    
    return result_image, panels_placed

def calculate_roof_measurements(rooftop_mask):
    """Calculate roof measurements from the mask"""
    contours, _ = cv2.findContours(rooftop_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Get ALL contours to find the full polygon dimensions
    all_points = []
    for contour in contours:
        for point in contour:
            all_points.append(point[0])
    
    if not all_points:
        return None
    
    all_points = np.array(all_points)
    # Get the full bounding rectangle of ALL rooftop areas
    x_min = np.min(all_points[:, 0])
    x_max = np.max(all_points[:, 0])
    y_min = np.min(all_points[:, 1])
    y_max = np.max(all_points[:, 1])
    
    # Full polygon dimensions
    full_width = x_max - x_min
    full_height = y_max - y_min
    length = max(full_width, full_height)
    breadth = min(full_width, full_height)
    
    # Convert to meters
    length_m = length * METERS_PER_PIXEL
    breadth_m = breadth * METERS_PER_PIXEL
    
    return {
        'length_m': length_m,
        'breadth_m': breadth_m,
        'total_roof_area_m2': length_m * breadth_m
    }

def process_rooftop_detection(image, num_panels):
    """Main processing function"""
    results = []
    
    for tolerance in TOLERANCE_VALUES:
        rooftop_mask = detect_rooftops_targeted(image, [tolerance])
        measurements = calculate_roof_measurements(rooftop_mask)
        
        if measurements:
            result_image, panels_placed = place_solar_panels_custom(image, rooftop_mask, num_panels)
            
            results.append({
                'tolerance': tolerance,
                'measurements': measurements,
                'mask': rooftop_mask,
                'result_image': result_image,
                'panels_placed': panels_placed
            })
    
    # Calculate average measurements
    if results:
        valid_measurements = [r['measurements'] for r in results if r['measurements'] is not None]
        if valid_measurements:
            avg_length = sum(m['length_m'] for m in valid_measurements) / len(valid_measurements)
            avg_breadth = sum(m['breadth_m'] for m in valid_measurements) / len(valid_measurements)
            
            # Get best result (highest panel placement)
            best_result = max(results, key=lambda x: x['panels_placed'])
            
            return {
                'avg_length': avg_length,
                'avg_breadth': avg_breadth,
                'best_result_image': best_result['result_image'],
                'panels_placed': best_result['panels_placed']
            }
    
    return None

@app.post("/detect-rooftop")
async def detect_rooftop(
    image: UploadFile = File(..., description="Google Maps satellite image"),
    num_panels: int = Form(..., description="Number of solar panels to place")
):
    """
    API to detect rooftops and place solar panels
    
    **Input:**
    - image: Google Maps satellite image file
    - num_panels: Number of solar panels to place
    
    **Output:**
    - length: Average roof length in meters
    - breadth: Average roof breadth in meters  
    - panels_placed: Number of panels successfully placed
    - result_image: Base64 encoded image with solar panels placed
    """
    
    try:
        # Validate inputs
        if num_panels <= 0:
            raise HTTPException(status_code=400, detail="Number of panels must be positive")
        
        # Read and validate image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if cv_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Process the image
        result = process_rooftop_detection(cv_image, num_panels)
        
        if result is None:
            raise HTTPException(status_code=404, detail="No rooftops detected in the image")
        
        # Convert result image to base64
        _, buffer = cv2.imencode('.jpg', result['best_result_image'])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return JSONResponse({
            "success": True,
            "data": {
                "length": round(result['avg_length'], 1),
                "breadth": round(result['avg_breadth'], 1),
                "panels_placed": result['panels_placed'],
                "result_image": img_base64
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Rooftop Detection & Solar Panel Placement API",
        "version": "1.0.0",
        "endpoints": {
            "/detect-rooftop": "POST - Main detection endpoint",
            "/docs": "GET - API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)