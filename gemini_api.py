from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from weasyprint import HTML
import tempfile
import pandas as pd

app = FastAPI(title="Solar Purchase Invoice Generator")

# Load CSV once at startup
try:
    prices_df = pd.read_csv("solar_prices.csv")
except FileNotFoundError:
    raise RuntimeError("CSV file 'solar_prices.csv' not found")

class InvoiceRequest(BaseModel):
    company_name: str
    model_name: str
    budget: float             # total customer budget
    num_panels: int           # number of solar panels
    contact_email: str | None = None
    address: str | None = None

def get_unit_price(model_name: str) -> float:
    """Fetch unit price from CSV file"""
    row = prices_df[prices_df["model_name"] == model_name]
    if row.empty:
        raise ValueError(f"Unknown solar panel model: {model_name}")
    return float(row["unit_price"].values[0])

@app.post("/invoice")
async def generate_purchase_invoice_pdf(data: InvoiceRequest):
    try:
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date_today = datetime.now().strftime('%d-%m-%Y')

        # ✅ Get unit price from CSV
        try:
            unit_price = get_unit_price(data.model_name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        total_amount = data.num_panels * unit_price
        remaining_budget = data.budget - total_amount

        # Prevent overspending
        if remaining_budget < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Budget exceeded! Total cost ₹{total_amount:,.2f} is greater than your budget ₹{data.budget:,.2f}."
            )

        invoice_text = f"""
PROFORMA INVOICE

Invoice Number: {invoice_number}
Date: {date_today}

Buyer Details:
{data.company_name}
{data.address or ""}

Contact Email: {data.contact_email or "Not Provided"}

----------------------------------------
Item Details:
----------------------------------------
Description     : {data.model_name}
Number of Panels: {data.num_panels}
Unit Price      : ₹{unit_price:,.2f}
Total Amount    : ₹{total_amount:,.2f}

----------------------------------------
Customer Budget : ₹{data.budget:,.2f}
Remaining Budget: ₹{remaining_budget:,.2f}
----------------------------------------

"""

        html_text = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Helvetica', sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                    font-size: 15px;
                    white-space: pre-wrap;
                }}
                h2 {{
                    text-align: center;
                    font-size: 22px;
                    text-transform: uppercase;
                }}
            </style>
        </head>
        <body>
            <h2>PROFORMA INVOICE</h2>
            <pre>{invoice_text}</pre>
        </body>
        </html>
        """

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        HTML(string=html_text).write_pdf(tmp_file.name)

        return FileResponse(
            tmp_file.name,
            media_type="application/pdf",
            filename=f"Invoice_{invoice_number}.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
