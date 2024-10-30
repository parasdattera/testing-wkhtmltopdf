from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import pdfkit
from fastapi.responses import FileResponse
import os

# FastAPI application
app = FastAPI()

# Database configuration
DB_HOST = "your_db_host"
DB_PORT = "your_db_port"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
DB_NAME = "your_db_name"

# PDF Configuration for wkhtmltopdf
PDF_CONFIG = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

# Data model for incoming request
class PDFRequest(BaseModel):
    param1: str
    param2: str

# Endpoint to convert HTML content to PDF
@app.post("/convert-html-to-pdf/")
async def convert_html_to_pdf(request: PDFRequest):
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host="host.docker.internal",
            port=5432,
            user="postgres",
            password="postgres",
            dbname="postgres"
        )
        cursor = connection.cursor()

        # Call stored procedure (UDF) to get dynamic data
        cursor.callproc("local.udf_testing")
        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Data not found")

        # Generate HTML content with the result from UDF
        html_content = f"""
        <html>
            <body>
                <h1>Generated PDF Report</h1>
                <p>Data from UDF: {result[0]}</p>
            </body>
        </html>
        """

        # Convert HTML to PDF
        pdf_output_path = "/tmp/output.pdf"
        pdfkit.from_string(html_content, pdf_output_path, configuration=PDF_CONFIG)

        # Return the generated PDF as a response
        # with open(pdf_output_path, "rb") as pdf_file:
        #     pdf_data = pdf_file.read()

        # Clean up and close database connection
        cursor.close()
        connection.close()
        # os.remove(pdf_output_path)
        return FileResponse(pdf_output_path,media_type="application/pdf",filename="report.pdf")

        # return {"pdf": pdf_data.hex()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
