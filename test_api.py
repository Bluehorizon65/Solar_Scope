import requests
import base64
import json
from PIL import Image
import io

def test_rooftop_api():
    """Test the rooftop detection API"""
    
    # API endpoint
    url = "http://localhost:8000/detect-rooftop"
    
    # Test image path (use one of your test images)
    image_path = "testcases/image copy 2.png"
    
    # API parameters
    num_panels = 25
    
    try:
        # Prepare the request
        with open(image_path, 'rb') as f:
            files = {
                'image': ('test_image.png', f, 'image/png')
            }
            data = {
                'num_panels': num_panels
            }
            
            # Make the API call
            print(f"🚀 Testing API with {num_panels} panels...")
            response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response Success!")
            print(f"📏 Length: {result['data']['length']}m")
            print(f"📐 Breadth: {result['data']['breadth']}m") 
            print(f"🔋 Panels Placed: {result['data']['panels_placed']}")
            
            # Decode and save the result image
            img_data = base64.b64decode(result['data']['result_image'])
            img = Image.open(io.BytesIO(img_data))
            img.save('api_result_image.jpg')
            print("💾 Result image saved as 'api_result_image.jpg'")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
    except FileNotFoundError:
        print(f"❌ Image file not found: {image_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API Health Check: OK")
        else:
            print("❌ API Health Check: Failed")
    except:
        print("❌ API is not running")

if __name__ == "__main__":
    print("🔋 ROOFTOP DETECTION API TEST CLIENT")
    print("=" * 50)
    
    # Test health first
    test_api_health()
    print()
    
    # Test main functionality
    test_rooftop_api()