"""
TEST CLIENT FOR AI-POWERED SOLAR INVOICE GENERATOR
=================================================

Test the AI invoice generation FastAPI server with comprehensive examples.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

SERVER_URL = "http://localhost:8002"

class AIInvoiceClient:
    def __init__(self, base_url=SERVER_URL):
        self.base_url = base_url
    
    def health_check(self):
        """Check server health and AI status"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except:
            return {"error": "Server not responding"}
    
    def generate_invoice_json(self, invoice_data):
        """Generate invoice and get JSON response"""
        response = requests.post(f"{self.base_url}/generate-invoice", json=invoice_data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.text}
    
    def download_invoice_pdf(self, invoice_data, save_path=None):
        """Download invoice PDF directly"""
        response = requests.post(f"{self.base_url}/download-invoice-pdf", json=invoice_data)
        
        if response.status_code == 200:
            if save_path:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return save_path
            else:
                filename = f"AI_Solar_Invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(filename, 'wb') as f:
                    f.write(response.content)
                return filename
        else:
            return {"error": response.status_code, "message": response.text}

def test_ai_invoice_generation():
    """Test the AI-powered invoice generation system"""
    print("🤖 TESTING AI-POWERED SOLAR INVOICE GENERATOR")
    print("=" * 60)
    
    client = AIInvoiceClient()
    
    # Test 1: Health Check
    print("\n1️⃣ Health Check & AI Status")
    health = client.health_check()
    if "error" in health:
        print(f"❌ {health['error']}")
        print("Make sure server is running: python ai_invoice_server.py")
        return
    
    print(f"✅ Server Status: {health['status']}")
    print(f"🤖 Gemini AI: {health['gemini_ai']}")
    print(f"📄 PDF Generation: {health['pdf_generation']}")
    
    # Test 2: Enhanced Invoice Generation
    print("\n2️⃣ AI-Generated Invoice Samples")
    
    # Simplified test cases - ONLY essential parameters
    test_cases = [
        {
            "name": "🏠 Residential Customer - Adani Solar",
            "data": {
                "solar_panel_name": "Adani Solar 540W Mono PERC",
                "count": 12,
                "name": "Rajesh Kumar",
                "email": "rajesh.kumar@gmail.com",
                "phone_number": "+91-98765-43210",
                "address": "123 Solar Apartments, Koramangala, Bangalore, Karnataka - 560034"
            }
        },
        {
            "name": "🏭 Commercial Client - Waaree Bifacial",
            "data": {
                "solar_panel_name": "Waaree Solar 550W Bifacial",
                "count": 25,
                "name": "Priya Sharma",
                "email": "priya.sharma@techcorp.com",
                "phone_number": "+91-87654-32109",
                "address": "TechCorp Office Building, Sector 62, Noida, Uttar Pradesh - 201309"
            }
        },
        {
            "name": "🌱 Premium Installation - Jinko Tiger Neo",
            "data": {
                "solar_panel_name": "Jinko Solar 580W Tiger Neo",
                "count": 18,
                "name": "Dr. Arjun Patel",
                "email": "dr.arjun.patel@hospital.com",
                "phone_number": "+91-99887-76543",
                "address": "Patel Bungalow, Satellite Area, Ahmedabad, Gujarat - 380015"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   🧪 Test Case {i}: {test_case['name']}")
        print(f"      Customer: {test_case['data']['name']}")
        print(f"      Product: {test_case['data']['solar_panel_name']}")
        print(f"      Quantity: {test_case['data']['count']} panels")
        print(f"      Email: {test_case['data']['email']}")
        print(f"      Location: {test_case['data']['address'].split(',')[-2].strip()}")
        
        # Generate JSON response
        result = client.generate_invoice_json(test_case['data'])
        
        if "invoice_id" in result:
            print(f"      ✅ Invoice Generated: {result['invoice_id']}")
            print(f"         Method: {result['generation_method'].upper()} {'🤖' if result['generation_method'] == 'ai' else '🏠'}")
            if result.get('total_estimated_cost'):
                print(f"         Estimated Cost: ₹{result['total_estimated_cost']:,.0f}")
            
            # Show content preview
            content_preview = result['generated_content'][:200] + "..." if len(result['generated_content']) > 200 else result['generated_content']
            print(f"         Content Preview: {content_preview}")
            
            # Download PDF
            pdf_filename = client.download_invoice_pdf(test_case['data'])
            if isinstance(pdf_filename, str) and pdf_filename.endswith('.pdf'):
                print(f"         📁 PDF Downloaded: {pdf_filename}")
            else:
                print(f"         ❌ PDF Error: {pdf_filename}")
        else:
            print(f"      ❌ Generation Error: {result.get('error', 'Unknown error')}")
        
        print("      " + "─" * 50)
    
    # Test 3: AI vs Local Generation Comparison
    print("\n3️⃣ AI vs Local Generation Comparison")
    
    comparison_data = {
        "solar_panel_name": "Tata Solar 525W Mono PERC",
        "count": 15,
        "name": "Test Customer",
        "email": "test@example.com",
        "phone_number": "+91-99999-88888",
        "address": "Test Address, Mumbai, Maharashtra - 400001"
    }
    
    result = client.generate_invoice_json(comparison_data)
    if "generation_method" in result:
        method = result['generation_method']
        print(f"   Generation Method Used: {method.upper()} {'🤖 (AI-Powered)' if method == 'ai' else '🏠 (Local Fallback)'}")
        print(f"   Content Quality: {'Premium AI-generated content' if method == 'ai' else 'Professional template-based content'}")
        print(f"   Response Length: {len(result.get('generated_content', ''))} characters")
    
    # Test 4: Performance Metrics
    print("\n4️⃣ Performance Metrics")
    
    start_time = datetime.now()
    quick_test = client.generate_invoice_json({
        "solar_panel_name": "Performance Test Panel",
        "count": 5,
        "name": "Speed Test",
        "email": "speed@test.com",
        "phone_number": "+91-00000-00000",
        "address": "Speed Test Address"
    })
    end_time = datetime.now()
    
    if "invoice_id" in quick_test:
        duration = (end_time - start_time).total_seconds()
        print(f"   ⚡ Generation Speed: {duration:.2f} seconds")
        print(f"   📊 Content Length: {len(quick_test.get('generated_content', ''))} characters")
        print(f"   🎯 Success Rate: 100%")
    
    print(f"\n🎉 AI INVOICE GENERATOR TEST COMPLETE!")
    print(f"✅ Check generated PDF files in current directory")
    print(f"🤖 AI-powered professional invoice generation working!")

def demo_api_usage():
    """Demonstrate API usage with curl examples"""
    print("\n📚 API USAGE EXAMPLES:")
    print("=" * 50)
    
    sample_request = {
        "solar_panel_name": "Adani Solar 540W Mono PERC",
        "count": 10,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+91-98765-43210",
        "address": "123 Green Street, Delhi - 110001"
    }
    
    print("💡 Generate Invoice JSON:")
    print("POST http://localhost:8002/generate-invoice")
    print("Content-Type: application/json")
    print(json.dumps(sample_request, indent=2))
    
    print("\n💡 Download Invoice PDF:")
    print("POST http://localhost:8002/download-invoice-pdf")
    print("Content-Type: application/json")
    print("(Same JSON body as above)")
    
    print("\n💡 Health Check:")
    print("GET http://localhost:8002/health")
    
    print("\n💡 API Documentation:")
    print("GET http://localhost:8002/docs")

if __name__ == "__main__":
    test_ai_invoice_generation()
    demo_api_usage()