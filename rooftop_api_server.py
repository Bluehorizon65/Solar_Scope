#!/usr/bin/env python3

"""
FastAPI for Rooftop Detection & Solar Panel Placement
Takes image path and number of panels as input, returns measurements and output image path
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
import uvicorn

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from rooftop_fastapi import process_rooftop_detection
except ImportError as e:
    print(f"Error importing rooftop_fastapi: {e}")
    print("Make sure rooftop_fastapi.py exists in the same directory")

# Create FastAPI app
app = FastAPI(
    title="Rooftop Detection API",
    description="API for detecting rooftops and placing solar panels with real-world measurements",
    version="1.0.0"
)

# Request model
class RooftopRequest(BaseModel):
    image_path: str
    num_panels: int

# Response model
class RooftopResponse(BaseModel):
    length: float
    width: float
    image_location: str

@app.post("/detect-rooftop", response_model=RooftopResponse)
async def detect_rooftop_endpoint(request: RooftopRequest):
    """
    Detect rooftops and place solar panels
    
    **Input:**
    - image_path: Path to the satellite image file
    - num_panels: Number of solar panels to place
    
    **Output:**
    - length: Roof length in meters
    - width: Roof width in meters  
    - image_location: Path to the generated output image
    """
    
    try:
        # Validate inputs
        if request.num_panels <= 0:
            raise HTTPException(status_code=400, detail="Number of panels must be positive")
        
        if not os.path.exists(request.image_path):
            # List available test images for debugging
            available_images = []
            testcases_dir = "testcases"
            if os.path.exists(testcases_dir):
                for file in os.listdir(testcases_dir):
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        available_images.append(f"testcases/{file}")
            
            error_msg = f"Image not found at path: {request.image_path}"
            if available_images:
                error_msg += f". Available test images: {', '.join(available_images)}"
            
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Process the rooftop detection
        result = process_rooftop_detection(request.image_path, request.num_panels)
        
        if not result:
            raise HTTPException(status_code=404, detail="No rooftops detected in the image")
        
        # Verify output file was created
        if not os.path.exists(result['output_path']):
            raise HTTPException(status_code=500, detail="Output image was not generated successfully")
        
        # Return the response in the requested format
        return RooftopResponse(
            length=result['length'],
            width=result['breadth'],  # Map breadth to width as requested
            image_location=result['output_path']
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Rooftop Detection & Solar Panel Placement API",
        "version": "1.0.0",
        "endpoints": {
            "/detect-rooftop": "POST - Main detection endpoint",
            "/docs": "GET - API documentation",
            "/health": "GET - Health check"
        },
        "example_usage": {
            "image_path": "testcases/image copy 2.png",
            "num_panels": 25
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if the processing module is available
        from rooftop_fastapi import process_rooftop_detection
        return {
            "status": "healthy", 
            "message": "API is running and rooftop_fastapi module is available"
        }
    except ImportError:
        raise HTTPException(status_code=503, detail="rooftop_fastapi module not available")

@app.get("/test-images")
async def list_test_images():
    """List available test images"""
    testcases_dir = "testcases"
    available_images = []
    
    if os.path.exists(testcases_dir):
        for file in os.listdir(testcases_dir):
            if file.endswith(('.png', '.jpg', '.jpeg')):
                available_images.append(f"testcases/{file}")
    
    return {
        "available_test_images": available_images,
        "total_count": len(available_images)
    }

if __name__ == "__main__":
    print("🔋 ROOFTOP DETECTION FASTAPI SERVER")
    print("=" * 50)
    print("🚀 Starting server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)