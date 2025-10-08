"""
AI-POWERED SOLAR INVOICE GENERATOR - FastAPI Server
==================================================

FastAPI server that uses Gemini AI to generate professional solar panel invoices
and converts them to PDF using reportlab.

Features:
- Gemini AI for intelligent invoice content generation
- Professional PDF generation with reportlab
- FastAPI REST API endpoints
- Error handling for API quota limits
- Fallback to local generation

Requirements:
  pip install fastapi uvicorn google-genai reportlab pandas

Usage:
  python ai_invoice_server.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime
import tempfile
import os
from typing import Optional
import pandas as pd

# Gemini AI imports
from google import genai
from google.genai import types

# PDF generation imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = FastAPI(
    title="AI-Powered Solar Invoice Generator",
    description="Generate professional solar panel invoices using Gemini AI and convert to PDF",
    version="3.0.0"
)

# Simplified Pydantic models - Only essential parameters
class InvoiceRequest(BaseModel):
    solar_panel_name: str
    count: int
    name: str
    email: str
    phone_number: str
    address: str

class InvoiceResponse(BaseModel):
    invoice_id: str
    status: str
    generated_content: str
    pdf_filename: str
    generation_method: str  # "ai" or "local"
    timestamp: str

# Global variables
gemini_client = None

def initialize_gemini():
    """Initialize Gemini AI client"""
    global gemini_client
    try:
        gemini_client = genai.Client(
            api_key="AIzaSyBxaN0tnsxKq60e4rujR0jw3k_9O_mGNBA"
        )
        print("✅ Gemini AI client initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️ Failed to initialize Gemini AI: {e}")
        return False

def generate_ai_invoice_content(solar_panel_name, count, name, email, phone_number, address):
    """Generate invoice content using Gemini AI - Simplified version"""
    global gemini_client
    
    # Enhanced prompt for professional invoice generation
    prompt = f"""
    Generate a comprehensive and professional solar panel purchase inquiry email for a customer.
    
    CUSTOMER DETAILS:
    - Name: {name}
    - Email: {email}
    - Phone: {phone_number}
    - Address: {address}
    
    PRODUCT REQUIREMENTS:
    - Solar Panel Model: {solar_panel_name}
    - Quantity: {count} units
    
    Please create a professional email that includes:
    
    1. SUBJECT LINE: Clear and professional subject for the email
    
    2. GREETING: Professional greeting to the sales team
    
    
    3. PRODUCT SPECIFICATIONS: 
       - Detailed request for {solar_panel_name}
       - Quantity: {count} units
       - Technical specifications needed

    4. COMPREHENSIVE QUOTATION REQUEST:
       - Unit pricing and total cost breakdown
       - Installation charges and services
       - Inverter and electrical components
       - Mounting structures and hardware
       - Warranty details (25-year performance, product warranty)
       - Government subsidy assistance
       - Financing options available
       - Grid connection support
       - After-sales maintenance packages
    
    6. SITE INFORMATION:
       - Installation address: {address}
       - Request for site survey if needed
       - Energy generation estimates for location
    
    7. TIMELINE REQUIREMENTS:
       - Expected delivery schedule
       - Installation timeline
       - Project completion date
    
    8. PROFESSIONAL CLOSING:
       - Thank you note
       - Contact information
       - Expected response time (3-5 business days)
       - My signature with {name}
    
    Make it sound professional, detailed, and like a serious buyer inquiry. Include all relevant technical and commercial aspects that a solar panel company would need to provide a comprehensive quotation.
    
    Format it as a complete ready-to-send email with proper paragraphs and professional structure.
    """
    
    try:
        model = "gemini-2.5-flash"  # Use reliable model
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["TEXT"],
        )
        
        # Generate content
        response_text = ""
        for chunk in gemini_client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (chunk.candidates and 
                chunk.candidates[0].content and 
                chunk.candidates[0].content.parts and
                chunk.text):
                response_text += chunk.text
        
        return response_text.strip(), "ai"
        
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            print("⚠️ Gemini API quota exceeded, falling back to local generation")
            return generate_local_invoice_content(solar_panel_name, count, name, email, phone_number, address), "local"
        else:
            print(f"❌ Gemini AI error: {e}")
            return generate_local_invoice_content(solar_panel_name, count, name, email, phone_number, address), "local"

def generate_local_invoice_content(solar_panel_name, count, name, email, phone_number, address):
    """Generate invoice content locally as fallback - Simplified version"""
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Load pricing data for estimates
    estimated_cost = None
    try:
        prices_df = pd.read_csv("solar_prices.csv")
        panel_row = prices_df[prices_df['model_name'].str.contains(solar_panel_name.split()[0], case=False, na=False)]
        if not panel_row.empty:
            unit_price = panel_row.iloc[0]['unit_price']
            estimated_cost = unit_price * count
    except:
        pass
    
    cost_estimate = f"\nEstimated Investment: ₹{estimated_cost:,} (for reference)" if estimated_cost else ""
    
    content = f"""Subject: Solar Panel Purchase Inquiry - {count} Units of {solar_panel_name}

Dear Solar Sales Team,

I hope this message finds you well. I am writing to request a comprehensive quotation for a solar panel installation project.

CUSTOMER INFORMATION:
====================
Full Name: {name}
Email Address: {email}
Contact Number: {phone_number}
Installation Address: {address}
Date of Inquiry: {current_date}

PROJECT REQUIREMENTS:
====================
Solar Panel Model: {solar_panel_name}
Quantity Required: {count} units
Installation Type: Rooftop/Ground Mount (please recommend optimal solution){cost_estimate}

COMPREHENSIVE QUOTATION REQUEST:
===============================

I would appreciate a detailed quotation covering the following aspects:

1. PRODUCT SPECIFICATIONS:
   • Unit price for {solar_panel_name}
   • Total cost for {count} panels
   • Technical specification sheets
   • Efficiency ratings and performance data
   • 25-year performance warranty details
   • Product warranty terms

2. COMPLETE SYSTEM COMPONENTS:
   • Inverter recommendations (string/power optimizers/micro-inverters)
   • Mounting structures and hardware
   • DC and AC electrical components
   • Monitoring system and app access
   • Safety equipment and surge protection

3. PROFESSIONAL SERVICES:
   • Site survey and system design
   • Installation charges and timeline
   • Electrical permits and approvals
   • Grid connection assistance
   • System commissioning and testing

4. FINANCIAL ASPECTS:
   • Total turnkey project cost
   • Payment schedule options
   • Available financing schemes
   • Government subsidy assistance (MNRE/State subsidies)
   • Tax benefits and depreciation details
   • EMI options if available

5. PERFORMANCE & SUPPORT:
   • Energy generation estimates for {address.split(',')[-1] if ',' in address else 'my location'}
   • System monitoring and maintenance packages
   • After-sales service network
   • Performance guarantee terms
   • Annual maintenance contract options

6. PROJECT TIMELINE:
   • Equipment delivery schedule
   • Installation duration
   • Grid synchronization timeline
   • Project completion date
   • Warranty activation process

ADDITIONAL INFORMATION:
======================
• Looking for a complete turnkey solution with reliable after-sales support
• Interested in branded components with proven track record
• Prefer systems with remote monitoring capabilities
• Open to site visit for accurate assessment and customized recommendations

I would greatly appreciate receiving your comprehensive quotation within 3-5 business days. Please feel free to contact me at {phone_number} or {email} for any clarifications or to schedule a site survey.

I look forward to your detailed proposal and to exploring this renewable energy investment opportunity.

Thank you for your time and consideration.

Best regards,

{name}
Phone: {phone_number}
Email: {email}
Date: {current_date}

---
Solar Panel Inquiry Generated: {current_date}
Model: {solar_panel_name} | Quantity: {count} units
Customer: {name}
"""
    
    return content

def create_professional_pdf(content, invoice_id, customer_name):
    """Create professional PDF from generated content"""
    
    # Create temporary file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp_file.name, pagesize=A4, 
                          rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=72)
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.darkgreen
    )
    
    # Story content
    story = []
    
    # Title
    story.append(Paragraph("SOLAR PANEL PURCHASE INQUIRY", title_style))
    story.append(Spacer(1, 20))
    
    # Document info
    doc_info = [
        ['Document ID:', invoice_id],
        ['Generated:', datetime.now().strftime('%d-%m-%Y %I:%M %p')],
        ['Customer:', customer_name],
        ['Type:', 'Solar Panel Quotation Request']
    ]
    
    doc_table = Table(doc_info, colWidths=[2*inch, 4*inch])
    doc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue)
    ]))
    
    story.append(doc_table)
    story.append(Spacer(1, 20))
    
    # Content sections
    content_lines = content.split('\n')
    current_section = ""
    
    for line in content_lines:
        line = line.strip()
        if not line:
            if current_section:
                story.append(Paragraph(current_section, styles['Normal']))
                story.append(Spacer(1, 10))
                current_section = ""
            continue
            
        # Check if it's a heading (contains === or uppercase sections)
        if ('===' in line or 
            line.isupper() or 
            line.startswith('Subject:') or
            any(keyword in line for keyword in ['CUSTOMER', 'PROJECT', 'QUOTATION', 'ADDITIONAL'])):
            
            if current_section:
                story.append(Paragraph(current_section, styles['Normal']))
                story.append(Spacer(1, 10))
                current_section = ""
            
            if line != '=' * len(line):  # Skip separator lines
                clean_line = line.replace('=', '').strip()
                if clean_line:
                    story.append(Paragraph(clean_line, heading_style))
        else:
            current_section += line + "<br/>"
    
    # Add remaining content
    if current_section:
        story.append(Paragraph(current_section, styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"""
    <para align="center">
    <b>AI-Generated Solar Panel Inquiry</b><br/>
    Generated on: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}<br/>
    Document ID: {invoice_id}
    </para>
    """
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    return tmp_file.name

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting AI-Powered Solar Invoice Generator")
    print("=" * 50)
    initialize_gemini()
    print("✅ Server initialization complete")

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "AI-Powered Solar Invoice Generator",
        "version": "3.0.0",
        "features": [
            "Gemini AI-powered content generation",
            "Professional PDF creation",
            "Fallback to local generation",
            "Comprehensive solar panel quotations"
        ],
        "endpoints": {
            "generate_invoice": "/generate-invoice",
            "download_pdf": "/download-invoice-pdf",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global gemini_client
    
    gemini_status = "connected" if gemini_client else "disconnected"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gemini_ai": gemini_status,
        "pdf_generation": "available",
        "service": "AI Invoice Generator"
    }

@app.post("/generate-invoice", response_model=InvoiceResponse)
async def generate_invoice(request: InvoiceRequest):
    """Generate solar panel purchase invoice using AI"""
    try:
        # Generate unique invoice ID
        invoice_id = f"AI-SOL-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        
        print(f"📄 Generating invoice {invoice_id} for {request.name}")
        print(f"   Product: {request.solar_panel_name}")
        print(f"   Quantity: {request.count} units")
        
        # Generate content using AI or local fallback
        content, method = generate_ai_invoice_content(
            request.solar_panel_name,
            request.count,
            request.name,
            request.email,
            request.phone_number,
            request.address
        )
        

        
        return InvoiceResponse(
            invoice_id=invoice_id,
            status="success",
            generated_content=content,
            pdf_filename=f"Solar_Invoice_{invoice_id}.pdf",
            generation_method=method,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating invoice: {str(e)}")

@app.post("/download-invoice-pdf")
async def download_invoice_pdf(request: InvoiceRequest):
    """Generate and download invoice PDF directly"""
    try:
        # Generate unique invoice ID
        invoice_id = f"AI-SOL-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        
        print(f"📄 Generating PDF invoice {invoice_id} for {request.name}")
        print(f"   Product: {request.solar_panel_name}")
        print(f"   Quantity: {request.count} units")
        
        # Generate content
        content, method = generate_ai_invoice_content(
            request.solar_panel_name,
            request.count,
            request.name,
            request.email,
            request.phone_number,
            request.address
        )
        
        # Create PDF
        pdf_path = create_professional_pdf(content, invoice_id, request.name)
        
        # Return PDF file
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"Solar_Invoice_{invoice_id}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("🌞 AI-POWERED SOLAR INVOICE GENERATOR - SIMPLIFIED")
    print("=" * 55)
    print("🤖 Powered by Gemini AI")
    print("📄 Professional PDF Generation")
    print("⚡ Essential Parameters Only")
    print("🌐 Server URL: http://localhost:8002")
    print("📖 API Documentation: http://localhost:8002/docs")
    print("🏥 Health Check: http://localhost:8002/health")
    print("\n📋 Required Parameters:")
    print("   • solar_panel_name")
    print("   • count")
    print("   • name")
    print("   • email") 
    print("   • phone_number")
    print("   • address")
    print("\n✨ Starting server...")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)