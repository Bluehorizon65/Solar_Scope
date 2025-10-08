import requests
import json

def test_rooftop_fastapi():
    """Test the new rooftop detection FastAPI"""
    
    # API endpoint
    url = "http://localhost:8000/detect-rooftop"
    
    # Test data
    test_data = {
        "image_path": "testcases/image copy 2.png",  # Update this path as needed
        "num_panels": 25
    }
    
    try:
        print("🚀 Testing Rooftop Detection API...")
        print(f"📸 Image: {test_data['image_path']}")
        print(f"🔋 Panels: {test_data['num_panels']}")
        print("-" * 50)
        
        # Make the API call
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response Success!")
            print(f"📏 Length: {result['length']}m")
            print(f"📐 Width: {result['width']}m") 
            print(f"📁 Image Location: {result['image_location']}")
            
            # Pretty print the JSON response
            print("\n📋 Full JSON Response:")
            print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error Details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
        print("Start server with: uvicorn rooftop_fastapi:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print("❌ API Health Check: Failed")
            return False
    except:
        print("❌ API is not running")
        return False

if __name__ == "__main__":
    print("🔋 ROOFTOP DETECTION FASTAPI TEST CLIENT")
    print("=" * 50)
    
    # Test health first
    if test_api_health():
        print()
        test_rooftop_fastapi()
    else:
        print("\n💡 To start the API server:")
        print("uvicorn rooftop_fastapi:app --host 0.0.0.0 --port 8000")