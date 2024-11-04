import json
from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
import psycopg2 # type: ignore
import pdfkit # type: ignore
from fastapi.responses import FileResponse # type: ignore
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







async def get_gppdi_data(stateLGDCode,gpLGDCode):
    con = None
    cursor_obj = None
    try:
        con = psycopg2.connect(
            database="pdi_db",
            user="pdi_db_ro",
            password="pdiro*321",
            host="10.248.213.201",
            port="5432",
        )
        cursor_obj = con.cursor()
        cursor_obj.callproc(
            "data_export.get_gsn_gp_pdi_score_v1",
            (1, stateLGDCode, gpLGDCode),
        )
        result = cursor_obj.fetchall()
        con.close()
        cursor_obj.close()
        if result:
            return result[0][0]
    except Exception as e:
        return {
            "status": 500,
            "message":f"An error occurred while fetching data. {str(e)}",
            "data":None
        }







class TemplateData(BaseModel):
    stateLGDCode:int
    gpLGDCode:int









# Endpoint to convert HTML content to PDF
@app.post("/convert-html-to-pdf/")
async def convert_html_to_pdf(request: TemplateData):
    try:
        api_data = await get_gppdi_data(request.stateLGDCode,request.gpLGDCode)
        # print("hi")
        # api_data = json.dumps(api_data)
        # api_data = json.load(api_data)
        # print(api_data)
        # Connect to PostgreSQL
        # connection = psycopg2.connect(
        #     host="host.docker.internal",
        #     port=5432,
        #     user="postgres",
        #     password="postgres",
        #     dbname="postgres"
        # )
        # cursor = connection.cursor()

        # Call stored procedure (UDF) to get dynamic data
        # cursor.callproc("public.udf_testing")
        # result = cursor.fetchone()

        if not api_data:
            raise HTTPException(status_code=404, detail="Data not found")

        # Generate HTML content with the result from UDF
        # html_content = f"""
        # <html>
        #     <body>
        #         <h1>Generated PDF Report</h1>
        #         <p>Data from UDF: {result[0]}</p>
        #     </body>
        # </html>
        # """
        
        image_src_map = {
          1: """<svg width="21" height="10" viewBox="0 0 21 10" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0.5 4.375C0.223858 4.375 -6.87182e-09 4.59886 -7.46043e-09 4.875C-8.04904e-09 5.15114 0.223858 5.375 0.5 5.375L0.5 4.375ZM6.5 5.375C6.77614 5.375 7 5.15114 7 4.875C7 4.59886 6.77614 4.375 6.5 4.375L6.5 5.375ZM4 1.375C4 1.09886 3.77614 0.875 3.5 0.875C3.22386 0.875 3 1.09886 3 1.375L4 1.375ZM3 8.625C3 8.90114 3.22386 9.125 3.5 9.125C3.77614 9.125 4 8.90114 4 8.625L3 8.625ZM0.5 5.375L3.5 5.375L3.5 4.375L0.5 4.375L0.5 5.375ZM3.5 5.375L6.5 5.375L6.5 4.375L3.5 4.375L3.5 5.375ZM4 4.875L4 1.375L3 1.375L3 4.875L4 4.875ZM3 1.375L3 8.625L4 8.625L4 1.375L3 1.375Z" fill="#23B67A"/>
  <path d="M15.5493 1L10.5 9L20.5 9L15.5493 1Z" fill="#23B67A"/>
  </svg>
  """,  
          2: """<svg width="21" height="9" viewBox="0 0 21 9" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M0.5 4.5L6.5 4.5" stroke="#C81515" stroke-linecap="round"/>
  <path d="M15.5 8.5L20.5 0.5H10.5L15.5 8.5Z" fill="#C81515"/>
  </svg>
  """,  
          3: "no image",
      }
        
        
        
        l1, l2, l3, l4 = [], [], [], []

        def categorize_value(value):
            if value[:1] == "-":
                return 1
            elif value == "0.00":
                return 3
            else:
                return 2

        for i, item in enumerate(api_data["matrix"][1:], start=1):
            target_list = [l1, l2, l3, l4][(i - 1) % 4]

            target_list.append(categorize_value(item["pdi_score"]))

            for t in range(1, 10):
                target_list.append(categorize_value(item[f"t{t}"]))



        if api_data["matrix"][1]["pdi_score"][:1] == "-":
            image_src1 = """<svg width="21" height="9" viewBox="0 0 21 9" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M0.5 4.5L6.5 4.5" stroke="#C81515" stroke-linecap="round"/>
    <path d="M15.5 8.5L20.5 0.5H10.5L15.5 8.5Z" fill="#C81515"/>
    </svg>
    "/>
    </svg>"""
        else:
            image_src1 = """<svg width="21" height="10" viewBox="0 0 21 10" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M0.5 4.375C0.223858 4.375 -6.87182e-09 4.59886 -7.46043e-09 4.875C-8.04904e-09 5.15114 0.223858 5.375 0.5 5.375L0.5 4.375ZM6.5 5.375C6.77614 5.375 7 5.15114 7 4.875C7 4.59886 6.77614 4.375 6.5 4.375L6.5 5.375ZM4 1.375C4 1.09886 3.77614 0.875 3.5 0.875C3.22386 0.875 3 1.09886 3 1.375L4 1.375ZM3 8.625C3 8.90114 3.22386 9.125 3.5 9.125C3.77614 9.125 4 8.90114 4 8.625L3 8.625ZM0.5 5.375L3.5 5.375L3.5 4.375L0.5 4.375L0.5 5.375ZM3.5 5.375L6.5 5.375L6.5 4.375L3.5 4.375L3.5 5.375ZM4 4.875L4 1.375L3 1.375L3 4.875L4 4.875ZM3 1.375L3 8.625L4 8.625L4 1.375L3 1.375Z" fill="#23B67A"/>
    <path d="M15.5493 1L10.5 9L20.5 9L15.5493 1Z" fill="#23B67A"/>
    </svg>
    """
            
            
        fin_year = "2022-2023"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>/* @import url("https://cdnjs.cloudflare.com/ajax/libs/meyer-reset/2.0/reset.min.css"); */
                /* @import url("https://fonts.googleapis.com/css?family=Noto+Sans:800,600,500,400,700|Inter:600,500,400,700|Kadwa:700"); */
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                html,
                body,
                div,
                span,
                applet,
                object,
                iframe,
                h1,
                h2,
                h3,
                h4,
                h5,
                h6,
                p,
                blockquote,
                pre,
                a,
                abbr,
                acronym,
                address,
                big,
                cite,
                code,
                del,
                dfn,
                em,
                img,
                ins,
                kbd,
                q,
                s,
                samp,
                small,
                strike,
                strong,
                sub,
                sup,
                tt,
                var,
                b,
                u,
                i,
                center,
                dl,
                dt,
                dd,
                ol,
                ul,
                li,
                fieldset,
                form,
                label,
                legend,
                table,
                caption,
                tbody,
                tfoot,
                thead,
                tr,
                th,
                td,
                article,
                aside,
                canvas,
                details,
                embed,
                figure,
                figcaption,
                footer,
                header,
                hgroup,
                menu,
                nav,
                output,
                ruby,
                section,
                summary,
                time,
                mark,
                audio,
                video {{
                  margin: 0;
                  padding: 0;
                  border: 0;
                  font-size: 100%;
                  font: inherit;
                  vertical-align: baseline;
                }}
                article,
                aside,
                details,
                figcaption,
                figure,
                footer,
                header,
                hgroup,
                menu,
                nav,
                section {{
                  display: block;
                }}
                body {{
                  line-height: 1;
                }}
                ol,
                ul {{
                  list-style: none;
                }}
                blockquote,
                q {{
                  quotes: none;
                }}
                blockquote:before,
                blockquote:after,
                q:before,
                q:after {{
                  content: "";
                  content: none;
                }}
                table {{
                  border-collapse: collapse;
                  border-spacing: 0;
                }}
                
                * {{
                  -webkit-font-smoothing: antialiased;
                  box-sizing: border-box;
                }}
                html,
                body {{
                  margin: 0px;
                  height: 100%;
                }}
                /* a blue color as a generic focus style */
                button:focus-visible {{
                  outline: 2px solid #4a90e2 !important;
                  outline: -webkit-focus-ring-color auto 5px !important;
                }}
                a {{
                  text-decoration: none;
                }}
                
                .final-done {{
                  background-color: #ffffff;
                  display: flex;
                  flex-direction: row;
                  justify-content: center;
                  width: 100%;
                }}
                
                .final-done .overlap-wrapper {{
                  background-color: #ffffff;
                  width: 1514px;
                  height: 2664px;
                }}
                
                .final-done .overlap {{
                  position: relative;
                  width: 1243px;
                  height: 2367px;
                  top: 72px;
                  left: 135px;
                  background-color: #f9f9f9;
                  border-radius: 24px;
                  border: 0.8px dashed;
                  border-color: #944b88;
                  box-shadow: 0px 0px 8px #00000040;
                }}
                
                .final-done .state {{
                  display: flex;
                  width: 1243px;
                  height: 43px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 13px 246px;
                  position: absolute;
                  top: -1px;
                  left: -1px;
                  background-color: #944b88;
                  border-radius: 24px 24px 0px 0px;
                }}
                
                .final-done .text-wrapper {{
                  position: relative;
                  width: fit-content;
                  margin-top: -0.5px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 22px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .group {{
                  position: absolute;
                  width: 1198px;
                  height: 133px;
                  top: 263px;
                  left: 22px;
                }}
                
                .final-done .frame {{
                  display: flex;
                  flex-direction: column;
                  width: 1198px;
                  align-items: flex-start;
                  gap: 22px;
                  position: absolute;
                  top: 0;
                  left: 0;
                }}
                
                .final-done .group-wrapper {{
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  height: 26px;
                }}
                
                .final-done .overlap-group-wrapper {{
                  width: 1200px;
                  height: 26px;
                }}
                
                .final-done .overlap-group {{
                  position: relative;
                  width: 1198px;
                  height: 26px;
                }}
                
                .final-done .vector {{
                  position: absolute;
                  width: 1198px;
                  height: 1px;
                  top: 12px;
                  left: 0;
                  object-fit: cover;
                }}
                
                .final-done .rectangle {{
                  position: absolute;
                  width: 170px;
                  height: 26px;
                  top: 0;
                  left: 514px;
                  background-color: #f9f9f9;
                }}
                
                .final-done .div {{
                  position: absolute;
                  top: 5px;
                  left: 547px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #3b7fed;
                  font-size: 18px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .p {{
                  position: relative;
                  align-self: stretch;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #2e2e2e;
                  font-size: 16px;
                  text-align: justify;
                  letter-spacing: 0;
                  line-height: 20.8px;
                }}
                
                .final-done .img {{
                  position: absolute;
                  width: 1198px;
                  height: 1px;
                  top: 132px;
                  left: 0;
                  object-fit: cover;
                }}
                
                .final-done .frame-2 {{
                  display: flex;
                  flex-direction: column;
                  width: 350px;
                  align-items: flex-start;
                  gap: 27.95px;
                  position: absolute;
                  top: 75px;
                  left: 22px;
                }}
                
                .final-done .gram-panchayat-karni {{
                  position: relative;
                  align-self: stretch;
                  margin-top: -1.22px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 19.4px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .span {{
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 19.4px;
                  letter-spacing: 0;
                }}
                
                .final-done .text-wrapper-2 {{
                  font-weight: 700;
                  font-size: 26.7px;
                }}
                
                .final-done .div-2 {{
                  position: relative;
                  align-self: stretch;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 17px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .text-wrapper-3 {{
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 17px;
                  letter-spacing: 0;
                }}
                
                .final-done .text-wrapper-4 {{
                  font-weight: 700;
                }}
                
                .final-done .frame-3 {{
                  display: flex;
                  flex-direction: column;
                  width: 134px;
                  align-items: center;
                  gap: 8px;
                  position: absolute;
                  top: 60px;
                  left: 1086px;
                }}
                
                .final-done .frame-4 {{
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  gap: 8px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  flex: 0 0 auto;
                }}
                
                .final-done .text-wrapper-5 {{
                  align-self: stretch;
                  margin-top: -1px;
                  font-weight: 400;
                  color: #000000;
                  font-size: 14px;
                  position: relative;
                  font-family: "Noto Sans", Helvetica;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-5 {{
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  height: 130px;
                }}
                
                .final-done .text-wrapper-6 {{
                  position: relative;
                  align-self: stretch;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 700;
                  color: #000000;
                  font-size: 16px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-6 {{
                  display: flex;
                  flex-direction: column;
                  width: 134px;
                  align-items: center;
                  gap: 8px;
                  position: absolute;
                  top: 60px;
                  left: 934px;
                }}
                
                .final-done .frame-7 {{
                  display: flex;
                  flex-direction: column;
                  width: 1197px;
                  height: 922px;
                  align-items: center;
                  gap: 33px;
                  position: absolute;
                  top: 869px;
                  left: 23px;
                  background-color: #ffffff;
                  border-radius: 5px;
                  border: 1px solid;
                  border-color: #696969;
                }}
                
                .final-done .div-wrapper {{
                  display: flex;
                  height: 49px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 16px 270px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  background-color: #696969;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .text-wrapper-7 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Inter", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 18px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-8 {{
                  display: inline-flex;
                  align-items: center;
                  gap: 38px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-9 {{
                  display: flex;
                  flex-direction: column;
                  width: 362px;
                  align-items: flex-start;
                  position: relative;
                  box-shadow: 0px 2px 10px #0000001a;
                }}
                
                .final-done .frame-10 {{
                  display: flex;
                  height: 39px;
                  align-items: center;
                  gap: 190px;
                  padding: 15px 10px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  background-color: #ffe0e0;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .text-wrapper-8 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -2.9px;
                  margin-bottom: -2.1px;
                  font-family: "Inter", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 11.5px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .group-2 {{
                  position: relative;
                  width: 28.64px;
                  height: 28.64px;
                  margin-top: -9.82px;
                  margin-bottom: -9.82px;
                  margin-right: -6.82px;
                }}
                
                .final-done .frame-11 {{
                  display: flex;
                  flex-direction: column;
                  height: 211px;
                  align-items: flex-start;
                  justify-content: center;
                  gap: 16px;
                  padding: 22px 9px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  background-color: #ffffff;
                  border-radius: 0px 0px 5px 5px;
                }}
                
                .final-done .frame-12 {{
                  display: flex;
                  width: 191px;
                  align-items: center;
                  gap: 8px;
                  position: relative;
                  flex: 0 0 auto;
                  margin-top: -5px;
                }}
                
                .final-done .frame-13 {{
                  display: flex;
                  width: 187px;
                  height: 22px;
                  align-items: center;
                  gap: 21px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 5px;
                }}
                
                .final-done .rectangle-2 {{
                  position: relative;
                  width: 108px;
                  height: 22px;
                  background-color: #5a9bd5;
                  border-radius: 5px 0px 0px 5px;
                }}
                
                .final-done .text-wrapper-9 {{
                  position: relative;
                  width: 53px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: 12px;
                }}
                
                .final-done .text-wrapper-10 {{
                  position: absolute;
                  top: 0;
                  left: 6px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .best-panchayat {{
                  width: 143px;
                  margin-top: -1px;
                  margin-right: -147px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  text-align: center;
                  position: relative;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .text-wrapper-11 {{
                  font-weight: 500;
                }}
                
                .final-done .frame-14 {{
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-15 {{
                  display: flex;
                  width: 187px;
                  height: 22px;
                  align-items: center;
                  gap: 69px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 5px;
                }}
                
                .final-done .rectangle-3 {{
                  position: relative;
                  width: 58px;
                  height: 22px;
                  background-color: #fc852d;
                  border-radius: 5px 0px 0px 5px;
                }}
                
                .final-done .text-wrapper-12 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: 12px;
                  white-space: nowrap;
                }}
                
                .final-done .text-wrapper-13 {{
                  position: absolute;
                  top: 2px;
                  left: 6px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .text-wrapper-14 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-16 {{
                  display: inline-flex;
                  align-items: center;
                  gap: 8px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-17 {{
                  display: flex;
                  width: 187px;
                  height: 22px;
                  align-items: center;
                  gap: 85px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 5px;
                }}
                
                .final-done .rectangle-4 {{
                  position: relative;
                  width: 45px;
                  height: 22px;
                  background-color: #ffdc5e;
                  border-radius: 5px 0px 0px 5px;
                }}
                
                .final-done .text-wrapper-15 {{
                  position: absolute;
                  top: 2px;
                  left: 5px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-18 {{
                  display: flex;
                  width: 187px;
                  height: 22px;
                  align-items: center;
                  gap: 110px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 5px;
                }}
                
                .final-done .rectangle-5 {{
                  position: relative;
                  width: 20px;
                  height: 22px;
                  background-color: #95192f;
                  border-radius: 5px 0px 0px 5px;
                }}
                
                .final-done .text-wrapper-16 {{
                  position: absolute;
                  top: 1px;
                  left: 5px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-19 {{
                  display: inline-flex;
                  align-items: center;
                  gap: 8px;
                  position: relative;
                  flex: 0 0 auto;
                  margin-bottom: -5px;
                }}
                
                .final-done .frame-20 {{
                  display: flex;
                  width: 187px;
                  height: 22px;
                  align-items: center;
                  gap: 50px;
                  padding: 0px 1px 0px 0px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 5px;
                }}
                
                .final-done .rectangle-6 {{
                  position: relative;
                  width: 81px;
                  height: 22px;
                  background-color: #90cf8e;
                  border-radius: 5px 0px 0px 5px;
                }}
                
                .final-done .text-wrapper-17 {{
                  position: absolute;
                  top: 1px;
                  left: 5px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-21 {{
                  height: 39px;
                  gap: 215px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #c6ffe8;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .group-3 {{
                  position: relative;
                  width: 28.64px;
                  height: 28.64px;
                  margin-top: -9.82px;
                  margin-bottom: -9.82px;
                  margin-right: -0.82px;
                }}
                
                .final-done .best-panchayat-2 {{
                  width: 150px;
                  margin-top: -1px;
                  margin-right: -154px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  text-align: center;
                  position: relative;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-22 {{
                  width: 187px;
                  height: 22px;
                  gap: 51px;
                  padding: 0px 1px 0px 0px;
                  border-radius: 5px;
                  display: flex;
                  align-items: center;
                  position: relative;
                  background-color: #d9d9d9;
                }}
                
                .final-done .frame-23 {{
                  height: 39px;
                  gap: 185px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #ffe7ba;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .text-wrapper-18 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -2.9px;
                  margin-bottom: -2.1px;
                  font-family: "Inter", Helvetica;
                  font-weight: 600;
                  color: #2e2e2e;
                  font-size: 11.5px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .group-4 {{
                  position: relative;
                  width: 21.01px;
                  height: 21.01px;
                  margin-top: -6px;
                  margin-bottom: -6px;
                  margin-right: -1.01px;
                  background-color: #fcb732;
                  border-radius: 10.5px;
                }}
                
                .final-done .group-5 {{
                  position: relative;
                  width: 16px;
                  height: 15px;
                  top: 3px;
                  left: 3px;
                }}
                /* 
                .final-done .ellipse-wrapper {{
                  width: 17px;
                  height: 16px;
                  background-image: url(https://c.animaapp.com/h1sXVOSf/img/vector-1.svg);
                  background-size: 100% 100%;
                }} */
                
                .final-done .ellipse {{
                  position: relative;
                  width: 3px;
                  height: 3px;
                  top: 7px;
                  left: 6px;
                  border-radius: 1.63px;
                  border: 0.76px solid;
                  border-color: #ffffff;
                }}
                
                .final-done .best-panchayat-3 {{
                  position: relative;
                  width: 147px;
                  margin-top: -1px;
                  margin-right: -151px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-24 {{
                  width: 187px;
                  height: 22px;
                  gap: 49px;
                  padding: 0px 1px 0px 0px;
                  border-radius: 5px;
                  display: flex;
                  align-items: center;
                  position: relative;
                  background-color: #d9d9d9;
                }}
                
                .final-done .frame-25 {{
                  height: 39px;
                  gap: 170px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;  
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                  background-color: #c0efff;
                }}
                
                .final-done .group-6 {{
                  position: relative;
                  width: 28.64px;
                  height: 28.64px;
                  margin-top: -9.82px;
                  margin-bottom: -9.82px;
                  margin-right: -2.82px;
                }}
                
                .final-done .best-panchayat-4 {{
                  width: 148px;
                  margin-top: -1px;
                  margin-right: -152px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  text-align: center;
                  position: relative;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-26 {{
                  height: 39px;
                  gap: 169px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #e6ffb4;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .group-7 {{
                  position: relative;
                  width: 28.64px;
                  height: 28.64px;
                  margin-top: -9.82px;
                  margin-bottom: -9.82px;
                  margin-right: -3.82px;
                }}
                
                .final-done .best-panchayat-dilla {{
                  width: 146px;
                  margin-top: -1px;
                  margin-right: -150px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  text-align: center;
                  position: relative;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-27 {{
                  height: 39px;
                  gap: 102px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #ffd2b1;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .frame-28 {{
                  height: 39px;
                  gap: 165px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #b6e2ff;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .frame-29 {{
                  height: 39px;
                  gap: 158px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #dcccff;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .best-panchayat-5 {{
                  width: 149px;
                  margin-top: -1px;
                  margin-right: -153px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  text-align: center;
                  position: relative;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-30 {{
                  width: 187px;
                  height: 22px;
                  gap: 52px;
                  padding: 0px 1px 0px 0px;
                  border-radius: 5px;
                  display: flex;
                  align-items: center;
                  position: relative;
                  background-color: #d9d9d9;
                }}
                
                .final-done .frame-31 {{
                  height: 39px;
                  gap: 174px;
                  padding: 15px 10px;
                  align-self: stretch;
                  width: 100%;
                  background-color: #ffb1aa;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .frame-32 {{
                  width: 187px;
                  height: 22px;
                  gap: 63px;
                  padding: 0px 1px 0px 0px;
                  border-radius: 5px;
                  display: flex;
                  align-items: center;
                  position: relative;
                  background-color: #d9d9d9;
                }}
                
                .final-done .frame-33 {{
                  display: flex;
                  flex-direction: column;
                  width: 268px;
                  height: 412px;
                  align-items: flex-start;
                  gap: 12px;
                  position: absolute;
                  top: 428px;
                  left: 22px;
                  border-radius: 5px;
                  border: 0.6px solid;
                  border-color: #909090;
                }}
                
                .final-done .frame-34 {{
                  display: flex;
                  height: 42px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  background-color: #696969;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .text-wrapper-19 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Inter", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 18px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-35 {{
                  display: flex;
                  flex-direction: column;
                  align-items: flex-start;
                  gap: 35px;
                  padding: 0px 14px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-wrapper {{
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-36 {{
                  display: flex;
                  align-items: center;
                  gap: 4px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  flex: 0 0 auto;
                }}
                
                .final-done .rectangle-7 {{
                  position: relative;
                  width: 37px;
                  height: 37px;
                  background-color: #5a9bd5;
                  border-radius: 4px;
                  box-shadow: 0px 4px 4px #00000040;
                }}
                
                .final-done .frame-37 {{
                  display: flex;
                  flex-direction: column;
                  width: 213px;
                  align-items: flex-start;
                  gap: 14px;
                  padding: 0px 3px;
                  position: relative;
                  margin-right: -14px;
                }}
                
                .final-done .text-wrapper-20 {{
                  position: relative;
                  align-self: stretch;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 800;
                  color: #2e2e2e;
                  font-size: 14px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .text-wrapper-21 {{
                  position: relative;
                  align-self: stretch;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 14px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-38 {{
                  display: flex;
                  flex-direction: column;
                  align-items: center;
                  justify-content: center;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  flex: 0 0 auto;
                }}
                
                .final-done .rectangle-8 {{
                  background-color: #90cf8e;
                  position: relative;
                  width: 37px;
                  height: 37px;
                  border-radius: 4px;
                  box-shadow: 0px 4px 4px #00000040;
                }}
                
                .final-done .rectangle-9 {{
                  background-color: #ffdc5e;
                  position: relative;
                  width: 37px;
                  height: 37px;
                  border-radius: 4px;
                  box-shadow: 0px 4px 4px #00000040;
                }}
                
                .final-done .rectangle-10 {{
                  background-color: #fc852d;
                  position: relative;
                  width: 37px;
                  height: 37px;
                  border-radius: 4px;
                  box-shadow: 0px 4px 4px #00000040;
                }}
                
                .final-done .rectangle-11 {{
                  background-color: #95192f;
                  position: relative;
                  width: 37px;
                  height: 37px;
                  border-radius: 4px;
                  box-shadow: 0px 4px 4px #00000040;
                }}
                
                .final-done .frame-39 {{
                  display: flex;
                  flex-direction: column;
                  width: 570px;
                  height: 412px;
                  align-items: center;
                  gap: 36px;
                  position: absolute;
                  top: 428px;
                  left: 651px;
                  background-color: #ffffff;
                  border-radius: 5px;
                  border: 0.4px solid;
                  border-color: #696969;
                }}
                
                .final-done .frame-40 {{
                  display: flex;
                  flex-wrap: wrap;
                  width: 552px;
                  align-items: flex-start;
                  gap: 32px 12px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .group-8 {{
                  position: relative;
                  width: 176px;
                  height: 76px;
                }}
                
                .final-done .overlap-2 {{
                  position: relative;
                  height: 76px;
                  border-radius: 12px;
                }}
                
                .final-done .t {{
                  position: absolute;
                  width: 176px;
                  height: 76px;
                  top: 0;
                  left: 0;
                  background-color: #ffffff;
                  border-radius: 12px;
                  box-shadow: 0px 0px 4px #00000040;
                }}
                
                .final-done .img-wrapper {{
                  position: absolute;
                  width: 56px;
                  height: 76px;
                  top: 0;
                  left: 0;
                  background-color: #95192f;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .group-9 {{
                  position: absolute;
                  width: 42px;
                  height: 42px;
                  top: 28px;
                  left: 7px;
                }}
                
                .final-done .group-10 {{
                  position: absolute;
                  width: 112px;
                  height: 61px;
                  top: 5px;
                  left: 60px;
                }}
                
                .final-done .text-wrapper-22 {{
                  position: absolute;
                  width: 101px;
                  top: 0;
                  left: 2px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #95192f;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .group-11 {{
                  position: absolute;
                  width: 112px;
                  height: 14px;
                  top: 47px;
                  left: 0;
                }}
                
                .final-done .overlap-group-2 {{
                  position: relative;
                  width: 110px;
                  height: 14px;
                  background-color: #d9d9d9;
                  border-radius: 4px;
                }}
                
                .final-done .rectangle-12 {{
                  position: absolute;
                  width: 67px;
                  height: 14px;
                  top: 0;
                  left: 0;
                  background-color: #23b67a;
                  border-radius: 4px 0px 0px 4px;
                }}
                
                .final-done .text-wrapper-23 {{
                  position: absolute;
                  top: 3px;
                  left: 25px;
                  font-family: "Inter", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 10px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 14.6px;
                  white-space: nowrap;
                }}
                
                .final-done .group-12 {{
                  position: absolute;
                  width: 27px;
                  height: 25px;
                  top: 2px;
                  left: 29px;
                }}
                
                .final-done .overlap-3 {{
                  position: relative;
                  width: 25px;
                  height: 25px;
                  background-color: #2e2e2e;
                  border-radius: 12.5px;
                }}
                
                .final-done .text-wrapper-24 {{
                  position: absolute;
                  top: 8px;
                  left: 6px;
                  font-family: "Inter", Helvetica;
                  font-weight: 400;
                  font-size: 12px;
                  text-align: center;
                  line-height: 17.6px;
                  color: #ffffff;
                  letter-spacing: 0;
                  white-space: nowrap;
                }}
                
                .final-done .overlap-4 {{
                  position: relative;
                  width: 178px;
                  height: 76px;
                }}
                
                .final-done .t-2 {{
                  position: absolute;
                  width: 178px;
                  height: 76px;
                  top: 0;
                  left: 0;
                }}
                
                .final-done .overlap-5 {{
                  position: relative;
                  width: 176px;
                  height: 76px;
                  background-color: #ffffff;
                  border-radius: 12px;
                  box-shadow: 0px 0px 4px #00000040;
                }}
                
                .final-done .group-13 {{
                  position: absolute;
                  width: 112px;
                  height: 14px;
                  top: 53px;
                  left: 60px;
                }}
                
                .final-done .text-wrapper-25 {{
                  position: absolute;
                  top: 15px;
                  left: 92px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #23b67a;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                  white-space: nowrap;
                }}
                
                .final-done .overlap-6 {{
                  position: absolute;
                  width: 56px;
                  height: 76px;
                  top: 0;
                  left: 0;
                  background-color: #23b67a;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .group-14 {{
                  position: absolute;
                  width: 42px;
                  height: 42px;
                  top: 27px;
                  left: 7px;
                }}
                
                .final-done .group-15 {{
                  position: absolute;
                  width: 27px;
                  height: 25px;
                  top: 0;
                  left: 29px;
                }}
                
                .final-done .text-wrapper-26 {{
                  position: absolute;
                  top: 8px;
                  left: 5px;
                  font-family: "Inter", Helvetica;
                  font-weight: 400;
                  color: #ffffff;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                  white-space: nowrap;
                }}
                
                .final-done .overlap-7 {{
                  height: 76px;
                  background-color: #fcb732;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .text-wrapper-27 {{
                  position: absolute;
                  width: 89px;
                  top: 10px;
                  left: 72px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #fcb732;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .group-16 {{
                  position: relative;
                  width: 176px;
                  height: 75px;
                }}
                
                .final-done .overlap-8 {{
                  position: relative;
                  width: 178px;
                  height: 75px;
                }}
                
                .final-done .t-3 {{
                  position: absolute;
                  width: 178px;
                  height: 75px;
                  top: 0;
                  left: 0;
                }}
                
                .final-done .overlap-9 {{
                  position: relative;
                  width: 176px;
                  height: 75px;
                  background-color: #ffffff;
                  border-radius: 12px;
                  box-shadow: 0px 0px 4px #00000040;
                }}
                
                .final-done .overlap-10 {{
                  height: 75px;
                  background-color: #47bfe8;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .group-17 {{
                  position: absolute;
                  width: 112px;
                  height: 14px;
                  top: 52px;
                  left: 60px;
                }}
                
                .final-done .text-wrapper-28 {{
                  position: absolute;
                  width: 119px;
                  top: 6px;
                  left: 56px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #47bfe8;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .overlap-11 {{
                  height: 75px;
                  background-color: #99c83a;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .text-wrapper-29 {{
                  position: absolute;
                  width: 106px;
                  top: 11px;
                  left: 62px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #99c83a;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .overlap-12 {{
                  height: 75px;
                  background-color: #fc852d;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .self-sufficient {{
                  position: absolute;
                  width: 100px;
                  top: 5px;
                  left: 64px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #fc852d;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 14.6px;
                }}
                
                .final-done .text-wrapper-30 {{
                  position: absolute;
                  top: 8px;
                  left: 4px;
                  font-family: "Inter", Helvetica;
                  font-weight: 400;
                  color: #ffffff;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                  white-space: nowrap;
                }}
                
                .final-done .overlap-13 {{
                  height: 76px;
                  background-color: #044b79;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .text-wrapper-31 {{
                  position: absolute;
                  width: 115px;
                  top: 7px;
                  left: 59px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #044b79;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .group-18 {{
                  position: absolute;
                  width: 27px;
                  height: 25px;
                  top: 3px;
                  left: 29px;
                }}
                
                .final-done .overlap-14 {{
                  height: 76px;
                  background-color: #7b64ac;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .good-governance {{
                  position: absolute;
                  width: 108px;
                  top: 10px;
                  left: 62px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #7b64ac;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .overlap-15 {{
                  height: 76px;
                  background-color: #fa3e2b;
                  position: absolute;
                  width: 56px;
                  top: 0;
                  left: 0;
                  border-radius: 12px 0px 0px 12px;
                }}
                
                .final-done .text-wrapper-32 {{
                  position: absolute;
                  width: 104px;
                  top: 10px;
                  left: 64px;
                  font-family: "Kadwa", Helvetica;
                  font-weight: 700;
                  color: #fa3e2b;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 17.6px;
                }}
                
                .final-done .frame-41 {{
                  display: flex;
                  flex-direction: column;
                  width: 330px;
                  align-items: flex-start;
                  position: absolute;
                  top: 428px;
                  left: 302px;
                }}
                
                .final-done .your-panchayat-PDI-wrapper {{
                  width: 330px;
                  height: 42px;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  background-color: #696969;
                  display: flex;
                  align-items: center;
                  position: relative;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .your-panchayat-PDI {{
                  position: relative;
                  width: fit-content;
                  margin-top: -0.4px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-42 {{
                  display: flex;
                  flex-direction: column;
                  width: 330px;
                  height: 267px;
                  align-items: flex-start;
                  gap: 21px;
                  padding: 8px 9px;
                  position: relative;
                  background-color: #ffffff;
                  border-radius: 0px 0px 5px 5px;
                  border: 1px solid;
                  border-color: #696969;
                }}
                
                .final-done .frame-43 {{
                  display: inline-flex;
                  align-items: center;
                  gap: 11px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-44 {{
                  display: flex;
                  width: 200px;
                  height: 28px;
                  align-items: center;
                  gap: 27px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 0px 5px 5px 0px;
                }}
                
                .final-done .rectangle-13 {{
                  position: relative;
                  width: 130px;
                  height: 28px;
                  background-color: #fc852d;
                  border-radius: 5px 0px 0px 5px;
                }}
                
                .final-done .text-wrapper-33 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: 12px;
                  white-space: nowrap;
                }}
                
                .final-done .c-aspirant {{
                  position: absolute;
                  top: 2px;
                  left: 11px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .text-wrapper-34 {{
                  position: relative;
                  width: 100px;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 13px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 16px;
                }}
                
                .final-done .frame-45 {{
                  display: flex;
                  width: 203px;
                  height: 28px;
                  align-items: center;
                  gap: 7px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 0px 5px 5px 0px;
                }}
                
                .final-done .rectangle-14 {{
                  position: relative;
                  width: 152px;
                  height: 29px;
                  margin-top: -0.5px;
                  margin-bottom: -0.5px;
                  background-color: #5a9bd5;
                }}
                
                .final-done .div-3 {{
                  position: absolute;
                  top: 2px;
                  left: 12px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .flexcontainer {{
                  display: flex;
                  flex-direction: column;
                  width: 104px;
                  align-items: flex-start;
                  gap: 16px;
                }}
                
                .final-done .text {{
                  position: relative;
                  align-self: stretch;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 13px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 8px;
                }}
                
                .final-done .frame-46 {{
                  display: flex;
                  width: 205px;
                  height: 28px;
                  align-items: center;
                  gap: 26px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 0px 5px 5px 0px;
                }}
                
                .final-done .rectangle-15 {{
                  position: relative;
                  width: 135px;
                  height: 28px;
                  background-color: #ffdc5e;
                }}
                
                .final-done .block-PDI-score {{
                  position: relative;
                  width: 73px;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 13px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 16px;
                }}
                
                .final-done .frame-47 {{
                  display: flex;
                  width: 207px;
                  height: 28px;
                  align-items: center;
                  gap: 41px;
                  position: relative;
                  background-color: #d9d9d9;
                  border-radius: 0px 5px 5px 0px;
                }}
                
                .final-done .rectangle-16 {{
                  position: relative;
                  width: 121px;
                  height: 28px;
                  background-color: #95192f;
                }}
                
                .final-done .d-beginner {{
                  position: absolute;
                  top: 2px;
                  left: 12px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #ffffff;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .district-PDI-score {{
                  position: relative;
                  width: 81px;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 13px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 16px;
                }}
                
                .final-done .frame-48 {{
                  width: 207px;
                  height: 28px;
                  gap: 12px;
                  padding: 0px 1px;
                  border-radius: 0px 5px 5px 0px;
                  display: flex;
                  align-items: center;
                  position: relative;
                  background-color: #d9d9d9;
                }}
                
                .final-done .rectangle-17 {{
                  position: relative;
                  width: 151px;
                  height: 28px;
                  background-color: #90cf8e;
                }}
                
                .final-done .text-wrapper-35 {{
                  position: relative;
                  width: 72px;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 500;
                  color: #000000;
                  font-size: 13px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: 16px;
                }}
                
                .final-done .frame-49 {{
                  display: flex;
                  flex-direction: column;
                  width: 331px;
                  height: 90px;
                  align-items: center;
                  position: absolute;
                  top: 750px;
                  left: 302px;
                  background-color: #fcfcfc;
                  border-radius: 4.45px;
                  box-shadow: 0px 0px 11.96px #00000026;
                }}
                
                .final-done .frame-50 {{
                  display: flex;
                  height: 42px;
                  align-items: center;
                  justify-content: center;
                  gap: 14.95px;
                  padding: 17.78px 14.95px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  background-color: #696969;
                  border-radius: 4.45px 4.45px 0px 0px;
                }}
                
                .final-done .text-wrapper-36 {{
                  width: fit-content;
                  margin-top: -4.78px;
                  margin-bottom: -1.79px;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 18px;
                  text-align: center;
                  white-space: nowrap;
                  position: relative;
                  font-family: "Noto Sans", Helvetica;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-51 {{
                  display: flex;
                  height: 38px;
                  align-items: center;
                  justify-content: center;
                  gap: 9px;
                  padding: 30px 8px 8px;
                  position: relative;
                  align-self: stretch;
                  width: 100%;
                  margin-top: -4px;
                }}
                
                .final-done .people-together-wrapper {{
                  display: flex;
                  width: 22px;
                  height: 22px;
                  align-items: center;
                  gap: 14.95px;
                  position: relative;
                  margin-top: -11px;
                  margin-bottom: -11px;
                }}
                
                .final-done .people-together {{
                  position: relative;
                  width: 22px;
                  height: 22px;
                  object-fit: cover;
                }}
                
                .final-done .text-wrapper-37 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -6.99px;
                  margin-bottom: -4.01px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .group-19 {{
                  position: absolute;
                  width: 1201px;
                  height: 528px;
                  top: 1811px;
                  left: 22px;
                }}
                
                .final-done .overlap-16 {{
                  position: relative;
                  width: 1199px;
                  height: 528px;
                }}
                
                .final-done .frame-52 {{
                  display: flex;
                  flex-wrap: wrap;
                  width: 1170px;
                  align-items: flex-start;
                  gap: 0px 0px;
                  position: absolute;
                  top: 131px;
                  left: 15px;
                }}
                
                .final-done .frame-53 {{
                  width: 46px;
                  border-radius: 5px 0px 0px 0px;
                  display: flex;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-38 {{
                  position: relative;
                  width: fit-content;
                  margin-left: -6.5px;
                  margin-right: -6.5px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #ffffff;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-54 {{
                  width: 64px;
                  display: flex;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-39 {{
                  position: relative;
                  width: fit-content;
                  margin-left: -0.5px;
                  margin-right: -0.5px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #ffffff;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .overall-PDI-score-wrapper {{
                  width: 175px;
                  display: flex;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .img-2 {{
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-55 {{
                  display: flex;
                  width: 98px;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-40 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  font-size: 16px;
                  line-height: normal;
                  color: #ffffff;
                  letter-spacing: 0;
                  white-space: nowrap;
                }}
                
                .final-done .frame-56 {{
                  width: 99px;
                  display: flex;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-57 {{
                  width: 97px;
                  display: flex;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-58 {{
                  width: 99px;
                  border-radius: 0px 5px 0px 0px;
                  border-right-width: 1px;
                  border-right-style: solid;
                  display: flex;
                  height: 48px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 10px;
                  position: relative;
                  background-color: #944b88;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-59 {{
                  width: 46px;
                  height: 66px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-2 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 600;
                  color: #000000;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-60 {{
                  width: 64px;
                  height: 66px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-61 {{
                  display: inline-flex;
                  align-items: center;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .frame-62 {{
                  display: flex;
                  flex-direction: column;
                  width: 24px;
                  height: 24px;
                  align-items: center;
                  justify-content: center;
                  gap: 10px;
                  padding: 7px 8px;
                  position: relative;
                  background-color: #3b3b3b;
                  border-radius: 12px;
                }}
                
                .final-done .text-wrapper-41 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -0.5px;
                  font-family: "Inter", Helvetica;
                  font-weight: 700;
                  color: #ffffff;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-63 {{
                  flex-direction: column;
                  width: 175px;
                  height: 66px;
                  gap: 16px;
                  background-color: #90cf8e;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-42 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Inter", Helvetica;
                  font-weight: 700;
                  color: #ffffff;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-64 {{
                  flex-direction: column;
                  width: 98px;
                  height: 66px;
                  gap: 16px;
                  background-color: #ffdc5e;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-43 {{
                  color: #000000;
                  position: relative;
                  width: fit-content;
                  font-family: "Inter", Helvetica;
                  font-weight: 700;
                  font-size: 16px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-65 {{
                  flex-direction: column;
                  width: 99px;
                  height: 66px;
                  gap: 16px;
                  background-color: #5a9bd5;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-66 {{
                  flex-direction: column;
                  width: 97px;
                  height: 66px;
                  gap: 16px;
                  background-color: #95192f;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-67 {{
                  flex-direction: column;
                  width: 98px;
                  height: 66px;
                  gap: 16px;
                  background-color: #95192f;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-68 {{
                  display: flex;
                  flex-direction: column;
                  width: 99px;
                  height: 66px;
                  align-items: center;
                  justify-content: center;
                  gap: 16px;
                  padding: 10px;
                  position: relative;
                  background-color: #fc852d;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-69 {{
                  flex-direction: column;
                  width: 98px;
                  height: 66px;
                  gap: 16px;
                  background-color: #fc852d;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-70 {{
                  flex-direction: column;
                  width: 99px;
                  height: 66px;
                  gap: 16px;
                  background-color: #90cf8e;
                  border-right-width: 1px;
                  border-right-style: solid;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-71 {{
                  width: 46px;
                  height: 65px;
                  gap: 10px;
                  background-color: #ffffff;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-72 {{
                  width: 64px;
                  height: 65px;
                  gap: 10px;
                  background-color: #ffffff;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-73 {{
                  display: inline-flex;
                  align-items: center;
                  justify-content: center;
                  gap: 8px;
                  position: relative;
                  flex: 0 0 auto;
                  margin-left: -1.5px;
                }}
                
                .final-done .text-wrapper-44 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -0.5px;
                  margin-left: -4px;
                  margin-right: -4px;
                  font-family: "Inter", Helvetica;
                  font-weight: 700;
                  color: #ffffff;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .openmoji-crown {{
                  position: relative;
                  width: 13px;
                  height: 13px;
                  margin-right: -1.5px;
                }}
                
                .final-done .frame-74 {{
                  width: 175px;
                  height: 65px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-45 {{
                  position: relative;
                  width: fit-content;
                  font-family: "Inter", Helvetica;
                  font-weight: 700;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .frame-75 {{
                  width: 98px;
                  height: 65px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-76 {{
                  width: 99px;
                  height: 65px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-77 {{
                  width: 97px;
                  height: 65px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-78 {{
                  width: 99px;
                  height: 65px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  border-right-width: 1px;
                  border-right-style: solid;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-79 {{
                  width: 46px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-80 {{
                  width: 64px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-81 {{
                  width: 175px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-82 {{
                  display: inline-flex;
                  align-items: center;
                  gap: 4px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .vector-2 {{
                  position: relative;
                  width: 7px;
                  height: 8.25px;
                  margin-top: -0.12px;
                  margin-bottom: -0.12px;
                  margin-left: -0.5px;
                }}
                
                .final-done .icon {{
                  position: relative;
                  width: 10px;
                  height: 8px;
                }}
                
                .final-done .frame-83 {{
                  width: 98px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-84 {{
                  width: 99px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-85 {{
                  width: 97px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .icon-2 {{
                  position: relative;
                  width: 13.5px;
                  height: 7.5px;
                }}
                
                .final-done .vector-3 {{
                  position: relative;
                  width: 7px;
                  height: 1px;
                  margin-left: -0.5px;
                  object-fit: cover;
                }}
                
                .final-done .frame-86 {{
                  width: 99px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  border-right-width: 1px;
                  border-right-style: solid;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-87 {{
                  width: 46px;
                  height: 66px;
                  gap: 10px;
                  background-color: #ffffff;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-88 {{
                  width: 64px;
                  height: 66px;
                  gap: 10px;
                  background-color: #ffffff;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .text-wrapper-46 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -0.5px;
                  margin-left: -0.5px;
                  margin-right: -0.5px;
                  font-family: "Inter", Helvetica;
                  font-weight: 700;
                  color: #ffffff;
                  font-size: 12px;
                  white-space: nowrap;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-89 {{
                  width: 175px;
                  height: 66px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-90 {{
                  width: 98px;
                  height: 66px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-91 {{
                  width: 99px;
                  height: 66px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-92 {{
                  width: 97px;
                  height: 66px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-93 {{
                  width: 99px;
                  height: 66px;
                  gap: 10px;
                  background-color: #f9f9f9;
                  border-right-width: 1px;
                  border-right-style: solid;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-94 {{
                  width: 46px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  border-radius: 0px 0px 0px 5px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-95 {{
                  width: 99px;
                  height: 65px;
                  gap: 10px;
                  background-color: #eeeeee;
                  border-radius: 0px 0px 5px 0px;
                  border-right-width: 1px;
                  border-right-style: solid;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  position: relative;
                  border-bottom-width: 1px;
                  border-bottom-style: solid;
                  border-left-width: 1px;
                  border-left-style: solid;
                  border-color: #c4c4c4;
                }}
                
                .final-done .frame-96 {{
                  display: flex;
                  width: 1170px;
                  align-items: center;
                  gap: 109px;
                  padding: 9px 12px;
                  position: absolute;
                  top: 63px;
                  left: 15px;
                  background-color: #ededed;
                  border-radius: 5px;
                }}
                
                .final-done .frame-97 {{
                  display: inline-flex;
                  align-items: center;
                  justify-content: center;
                  gap: 8px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .openmoji-crown-2 {{
                  position: relative;
                  width: 13px;
                  height: 13px;
                }}
                
                .final-done .text-wrapper-47 {{
                  width: fit-content;
                  font-family: "Inter", Helvetica;
                  font-weight: 500;
                  white-space: nowrap;
                  position: relative;
                  color: #000000;
                  font-size: 12px;
                  letter-spacing: 0;
                  line-height: normal;
                }}
                
                .final-done .frame-98 {{
                  display: flex;
                  flex-wrap: wrap;
                  width: 570px;
                  align-items: center;
                  gap: 24px 24px;
                  position: relative;
                  margin-right: -10px;
                }}
                
                .final-done .frame-99 {{
                  display: inline-flex;
                  align-items: center;
                  gap: 18px;
                  position: relative;
                  flex: 0 0 auto;
                }}
                
                .final-done .div-4 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 14px;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .text-wrapper-48 {{
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 400;
                  color: #000000;
                  font-size: 14px;
                  letter-spacing: 0;
                }}
                
                .final-done .text-wrapper-49 {{
                  position: relative;
                  width: fit-content;
                  margin-top: -1px;
                  font-family: "Noto Sans", Helvetica;
                  font-weight: 700;
                  color: #000000;
                  font-size: 26.7px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                
                .final-done .rectangle-18 {{
                  position: absolute;
                  width: 1199px;
                  height: 499px;
                  top: 29px;
                  left: 0;
                  border-radius: 5px;
                  border: 1px solid;
                  border-color: #696969;
                }}
                
                .final-done .rectangle-19 {{
                  position: absolute;
                  width: 1199px;
                  height: 37px;
                  top: 0;
                  left: 0;
                  background-color: #696969;
                  border-radius: 5px 5px 0px 0px;
                }}
                
                .final-done .text-wrapper-50 {{
                  position: absolute;
                  top: 12px;
                  left: 289px;
                  font-family: "Inter", Helvetica;
                  font-weight: 500;
                  color: #ffffff;
                  font-size: 18px;
                  text-align: center;
                  letter-spacing: 0;
                  line-height: normal;
                  white-space: nowrap;
                }}
                </style>
        
        
        
        </head>
        <body>
            <div class="final-done">
                <div class="overlap-wrapper">
                    <div class="overlap">
                        <div class="state">
                            <p class="text-wrapper">{api_data['g']['gp_name_en']}, Panchayat Development Index (PDI) Score for {fin_year}</p>
                          </div>
                          <div class="frame-2">
                            <!-- <p class="gram-panchayat-">
                              <span class="span">Gram Panchayat :&nbsp;&nbsp;</span> <span class="text-wrapper-2">{api_data['g']['gp_name_en']} </span>
                            </p> -->
                            <p class="div-2">
                                <span class="text-wrapper-3">Gram Panchayat :</span> <span class="text-wrapper-4">&nbsp;&nbsp;{api_data['g']['gp_name_en']} </span>
                              </p>
                            <p class="div-2">
                              <span class="text-wrapper-3">Block :</span> <span class="text-wrapper-4">&nbsp;&nbsp; {api_data['g']['b_name_en']}</span>
                            </p>
                            <p class="div-2">
                              <span class="text-wrapper-3">District:</span> <span class="text-wrapper-4">&nbsp;&nbsp; {api_data['g']['d_name_en']}</span>
                            </p>
                            <p class="div-2">
                              <span class="text-wrapper-3">State :</span> <span class="text-wrapper-4">&nbsp;&nbsp;{api_data['g']['state_name_en']}</span>
                            </p>
                          </div>

                          <div class="group">
                            <div class="frame">
                                
                              <div class="group-wrapper">
                                <div class="overlap-group-wrapper">
                                  <div class="overlap-group">
                                    <svg style="position: absolute; top: 20px; left: 0px;" xmlns="http://www.w3.org/2000/svg" width="1198" height="2" viewBox="0 0 1198 2" fill="none">
                                                                 <path d="M0 1L1198 1.0001" stroke="black" stroke-dasharray="12 12"/>
                                                                 </svg>
                                        
                                    <!-- <img class="vector" src="https://c.animaapp.com/Qr0MpKdr/img/vector-12-1.svg" /> -->
                                    <div class="rectangle"></div>
                                    <div class="div">DISCLAIMER</div>
                                  </div>
                                </div>
                              </div>
                              <p class="p">
                                The indicators value, the thematic Scores of 9 LSDG Themes and the PDI Score visible here are purely
                                provisional and computed on the basis of data entered and submitted by Panchayats. The aim is to to help
                                the States / UTs to check the discrepancy, if any, in the data submitted by Panchayats. The indicators
                                value, the thematic scores as well as PDI Scores will be finalized after the correction, if any, and
                                validation of entire data by the State / UT.
                              </p>
                            </div>
                            <!-- <img class="img" src="https://c.animaapp.com/Qr0MpKdr/img/vector-12-1.svg" /> -->
                            <svg style="position: absolute; top: 130px; left: 0px;" xmlns="http://www.w3.org/2000/svg" width="1198" height="2" viewBox="0 0 1198 2" fill="none">
                                                 <path d="M0 1L1198 1.0001" stroke="black" stroke-dasharray="12 12"/>
                                             </svg> 
                          </div>

                          <div class="frame-3">
                            <div class="frame-4">
                              <div class="text-wrapper-5">Panchayat Secretary</div>
                              <svg width="134" height="130" viewBox="0 0 134 130" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect x="0.2" y="0.2" width="133.6" height="129.6" rx="4.8" fill="#F4F4F4"/>
                                <rect x="0.2" y="0.2" width="133.6" height="129.6" rx="4.8" stroke="#1956B8" stroke-width="0.4"/>
                                <path d="M34.8228 78.717C18.4892 85.8629 16.1073 101.261 16.958 108.066C16.958 108.066 47.7644 117.132 68 116.999C87.4999 116.87 117.128 108.066 117.128 108.066C118.149 89.1806 106.494 80.6311 100.539 78.717L85.0766 71.9133C84.7832 71.7842 84.4429 71.8473 84.2129 72.0708C82.4231 73.81 74.5775 81.062 68 81.2691C61.0019 81.4894 52.4048 73.8303 50.5143 72.0602C50.2809 71.8418 49.9431 71.7867 49.6525 71.9199L34.8228 78.717Z" fill="#4C4C4C"/>
                                <path d="M67.9998 76.3051C55.2393 76.3051 49.497 59.7164 49.497 59.7164C45.8815 55.2502 40.0542 45.1693 45.6689 40.5755L46.2484 28.9894C46.2867 28.2239 46.5534 27.4883 47.0068 26.8705C47.7485 25.8598 48.7568 24.4589 49.497 23.3488C50.1033 22.4395 53.9635 11.6575 69.9142 13.1395C79.0973 13.9928 86.5029 21.4338 88.417 27.815L89.055 40.5755C94.6697 47.211 88.8422 56.5262 85.2266 60.3544C85.2266 60.3544 78.8463 76.3051 67.9998 76.3051Z" fill="#4C4C4C"/>
                                </svg>
                            </div>
                            <div class="text-wrapper-6">{api_data['g']['secretary_name']}</div>
                          </div>

                          <div class="frame-6">
                            <div class="frame-4">
                              <div class="text-wrapper-5">Panchayat Sarpanch</div>
                              <svg width="134" height="130" viewBox="0 0 134 130" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect x="0.2" y="0.2" width="133.6" height="129.6" rx="4.8" fill="#F4F4F4"/>
                                <rect x="0.2" y="0.2" width="133.6" height="129.6" rx="4.8" stroke="#1956B8" stroke-width="0.4"/>
                                <path d="M34.8228 78.717C18.4892 85.8629 16.1073 101.261 16.958 108.066C16.958 108.066 47.7644 117.132 68 116.999C87.4999 116.87 117.128 108.066 117.128 108.066C118.149 89.1806 106.494 80.6311 100.539 78.717L85.0766 71.9133C84.7832 71.7842 84.4429 71.8473 84.2129 72.0708C82.4231 73.81 74.5775 81.062 68 81.2691C61.0019 81.4894 52.4048 73.8303 50.5143 72.0602C50.2809 71.8418 49.9431 71.7867 49.6525 71.9199L34.8228 78.717Z" fill="#4C4C4C"/>
                                <path d="M67.9998 76.3051C55.2393 76.3051 49.497 59.7164 49.497 59.7164C45.8815 55.2502 40.0542 45.1693 45.6689 40.5755L46.2484 28.9894C46.2867 28.2239 46.5534 27.4883 47.0068 26.8705C47.7485 25.8598 48.7568 24.4589 49.497 23.3488C50.1033 22.4395 53.9635 11.6575 69.9142 13.1395C79.0973 13.9928 86.5029 21.4338 88.417 27.815L89.055 40.5755C94.6697 47.211 88.8422 56.5262 85.2266 60.3544C85.2266 60.3544 78.8463 76.3051 67.9998 76.3051Z" fill="#4C4C4C"/>
                                </svg>
                            </div>
                            <div class="text-wrapper-6">{api_data['g']['sarpanch_name']}</div>
                          </div>
                          <div class="frame-7">
                            <div class="div-wrapper">
                              <p class="text-wrapper-7">Thematic Score of My Panchayat, Best Panchayat, Block, District and State</p>
                            </div>
                            <div class="frame-8">
                              <div class="frame-9">
                                <div class="frame-10">
                                  <p class="text-wrapper-8">Theme 1 - Poverty Free</p>
                                  <!-- <img class="group-2" src="https://c.animaapp.com/Qr0MpKdr/img/group-3339@3x.png" /> -->
                                   <svg class="group-2" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <g id="Group 3339">
                                <g id="Group 5">
                                <circle id="Ellipse 3" cx="21" cy="21" r="21" fill="#95192F"/>
                                <g id="Group 3">
                                <path id="Vector 2" d="M10.6418 26.5587V21.967C10.7223 20.7587 11.7534 18.4387 15.2334 18.8253M15.2334 18.8253V24.142M15.2334 18.8253C15.7168 17.1337 17.3601 14.0403 20.0668 15.2003M20.0668 15.2003V22.4503M20.0668 15.2003V11.817C20.3084 9.64197 24.1751 8.91696 25.3834 11.817V23.417C25.6251 23.417 26.0907 22.7962 26.3501 22.4503C27.0751 21.4836 29.4918 18.5836 31.9084 20.7586C31.1029 22.2086 29.7334 25.012 29.7334 25.592C29.7334 26.172 26.189 29.8614 24.4168 31.6336C24.6584 33.567 23.3091 37.917 18.6168 37.917C13.7834 37.917 12.0918 33.8086 12.3334 31.8753C12.0918 28.0086 17.1668 23.6586 22.4834 27.5253M15.2334 29.7003H19.3418M22.0001 29.7003H19.3418M19.3418 29.7003C19.5029 30.667 19.5834 32.697 18.6168 33.0836M18.6168 33.0836H22.0001H17.2884M18.6168 33.0836H17.2884M14.9918 33.0836H17.2884M17.2884 33.0836C17.1673 33.8892 17.4084 35.5486 19.3418 35.742" stroke="white" stroke-width="1.35733" stroke-linecap="round" stroke-linejoin="round"/>
                                <circle id="Ellipse 3_2" cx="12.0919" cy="14.957" r="1.49634" stroke="white" stroke-width="1.35733"/>
                                <circle id="Ellipse 4" cx="16.9257" cy="11.5749" r="1.49634" stroke="white" stroke-width="1.35733"/>
                                <circle id="Ellipse 5" cx="22.7257" cy="6.2577" r="1.49634" stroke="white" stroke-width="1.35733"/>
                                </g>
                                </g>
                                </g>
                                </svg>
                                </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t1bp"></div>
                                      
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp; {api_data['pdi_s'][1]['bgp_g'][0:1]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][1]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][1]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][1]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][1]['gp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][1]['gps']}</div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4bp"></div>
                                      <!-- <div class="text-wrapper-12"></div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][1]['b_g'][:2]}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;{api_data['pdi_s'][1]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5dp"></div>
                                      <!-- <div class="text-wrapper-12"></div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][1]['d_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][1]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-20">
                                      <div class="rectangle-6s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][1]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][1]['s_g'][:2]}   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][1]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                              </div>
                              <div class="frame-9">
                                <div class="frame-21">
                                  <div class="text-wrapper-8">Theme 2 - Healthy</div>
                                  <!-- <img class="group-3" src="https://c.animaapp.com/Qr0MpKdr/img/group-3336@3x.png" /> -->
                                  <svg class="group-3" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="21" cy="21" r="21" fill="#23B67A"/>
                                    <path d="M30.0688 23.3209H38.2209C37.8183 27.5693 34.2958 36.0659 23.4263 36.0659V31.62H28.5591V25.9885H23.4263V24.2101C25.9424 22.8269 30.733 19.0529 29.7669 15.0219H25.5398C24.6341 15.0219 23.9698 15.1404 23.7283 16.8003V18.875C23.7283 19.7642 23.4263 20.6534 22.2186 20.6534H18.8974M18.5955 15.0219L11.9531 15.0219C11.6514 18.2822 12.9797 21.7204 18.2937 23.6173V25.9885H13.4629V31.62H18.2937V36.0659C12.5571 36.9551 5.31084 31.9164 3.49927 23.3209H11.0475" stroke="white" stroke-width="1.84209" stroke-linecap="round" stroke-linejoin="round"/>
                                    <path d="M17.6749 9.09329C17.6749 10.3693 16.6164 11.4326 15.2747 11.4326C13.933 11.4326 12.8745 10.3693 12.8745 9.09329C12.8745 7.81732 13.933 6.75399 15.2747 6.75399C16.6164 6.75399 17.6749 7.81732 17.6749 9.09329Z" stroke="white" stroke-width="1.84209"/>
                                    <path d="M29.1485 9.09329C29.1485 10.3693 28.09 11.4326 26.7483 11.4326C25.4066 11.4326 24.3481 10.3693 24.3481 9.09329C24.3481 7.81732 25.4066 6.75399 26.7483 6.75399C28.09 6.75399 29.1485 7.81732 29.1485 9.09329Z" stroke="white" stroke-width="1.84209"/>
                                    <path d="M37.602 17.9843C37.602 19.2603 36.5436 20.3236 35.2018 20.3236C33.8601 20.3236 32.8017 19.2603 32.8017 17.9843C32.8017 16.7083 33.8601 15.645 35.2018 15.645C36.5436 15.645 37.602 16.7083 37.602 17.9843Z" stroke="white" stroke-width="1.84209"/>
                                    <path d="M9.22066 17.9843C9.22066 19.2603 8.1622 20.3236 6.82049 20.3236C5.47877 20.3236 4.42031 19.2603 4.42031 17.9843C4.42031 16.7083 5.47877 15.645 6.82049 15.645C8.1622 15.645 9.22066 16.7083 9.22066 17.9843Z" stroke="white" stroke-width="1.84209"/>
                                    </svg>
                                </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t2bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][2]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][2]['bgp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][2]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-2">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][2]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3mp2"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][2]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][2]['gp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][2]['gps']} </div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t2b"></div>
                                      <!-- <div class="text-wrapper-12">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][2]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][2]['b_g'][:2]}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;{api_data['pdi_s'][2]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t2d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][2]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][2]['d_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;  {api_data['pdi_s'][2]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-22">
                                      <div class="rectangle-6t2s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][2]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][2]['s_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;{api_data['pdi_s'][2]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div> 
                                </div>
                                </div>
                                <div class="frame-9">
                                    <div class="frame-23">
                                        <p class="text-wrapper-8">Theme 3 - Child Friendly</p>
                                        <!-- <img class="group-2" src="/frontend/images/Group 3341.svg" /> -->
                                        <svg class="group-2" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="21" cy="21" r="21" fill="#FCB732"/>
                                            <path d="M29.5071 18.8415C33.9793 26.4287 27.2293 35.3346 22.3247 36.1876C20.9696 29.9538 23.9509 26.9725 26.1192 23.178C21.5116 30.4959 15.5489 27.7856 11.2124 23.9911C15.4648 27.5145 15.7296 33.8386 15.2779 36.1876C4.00295 31.6342 6.24348 21.8229 8.77312 17.4863L6.60486 15.5891L5.24969 16.6732L5.52073 8.8133L13.6517 9.35536L12.2965 10.9816L14.1938 13.4209C14.8442 12.7704 16.6331 12.6078 17.4462 12.6078L17.7172 10.4395H15.82L20.4275 5.83194L24.764 10.9816H23.1378V13.1498C26.2586 14.8258 28.295 16.7852 29.5071 18.8415ZM29.5071 18.8415L31.2688 17.4863M31.2688 17.4863C33.2203 19.6546 35.1536 18.5705 35.8764 17.7574C37.7736 15.3181 36.1474 13.4209 35.0633 12.8788M31.2688 17.4863C30.5921 16.8096 30.5912 15.322 31.2324 14.1707M35.0633 12.8788C37.0147 7.89179 32.895 6.10297 30.7268 6.64504C26.7045 7.65059 27.2033 12.0657 28.8295 13.4209M35.0633 12.8788C33.1636 12.2003 31.8753 13.0164 31.2324 14.1707M26.9323 15.5891L28.8295 13.4209M28.8295 13.4209C29.3716 13.8726 30.4557 14.505 31.2324 14.1707" stroke="white" stroke-width="1.67327" stroke-linecap="round" stroke-linejoin="round"/>
                                            <circle cx="18.8011" cy="22.906" r="2.41575" stroke="white" stroke-width="1.67327"/>
                                            </svg>
                                            
                                      </div>
                                <!-- <div class="frame-23">
                                  <p class="text-wrapper-18">Theme 3 - Child Friendly</p>
                                  <div class="group-4">
                                    <div class="group-5">
                                      <div class="ellipse-wrapper"><div class="ellipse"></div></div>
                                    </div>
                                  </div>
                                </div> -->
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t3bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][3]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][3]['bgp_g'][:2]}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][3]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-3">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][3]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t3mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][3]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][3]['gp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;  {api_data['pdi_s'][3]['gps']}</div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t3b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][3]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][3]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][3]['b']} </div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t3d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][3]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][3]['d_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][3]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-24">
                                      <div class="rectangle-6t3s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][3]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][3]['s_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;  {api_data['pdi_s'][3]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                </div>
                                <div class="frame-8">
                                <div class="frame-9">
                                    <div class="frame-25">
                                        <p class="text-wrapper-8">Theme 4 - Water Sufficient</p>
                                        <!-- <img class="group-2" src="/frontend/images/Group 3338.svg" /> -->
                                        <svg class="group-2" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <circle cx="21" cy="21" r="21" fill="#47BFE8"/>
                                            <path d="M16.9411 9.28507C16.6881 10.563 25.7954 10.8185 25.2894 9.28507M14.4113 17.208C15.9292 17.208 16.4123 19.1311 17.953 18.997C19.3726 18.8735 19.564 16.9524 20.9888 16.9524C22.4136 16.9524 22.6 18.9707 24.0246 18.997C25.3968 19.0224 25.5424 16.9524 27.0603 17.208M12.8934 9.28507C11.6286 4.94032 29.0842 4.42914 29.0842 9.28507C29.0841 10.563 27.9036 11.2445 27.5663 11.5853C26.0484 13.1188 26.8073 14.5793 28.0722 15.6746C29.8431 17.208 33.7681 20.275 32.3729 26.92C30.9562 33.6673 25.2052 35.8652 22.5067 36.1208C15.9292 36.632 11.1119 32.7059 9.60471 26.92C8.33977 22.064 11.7972 17.5488 13.9054 15.6746C15.6762 13.8855 15.4232 13.1188 14.1584 11.5853C14.1584 11.5853 13.3399 10.8186 12.8934 9.28507Z" stroke="white" stroke-width="1.70768" stroke-linecap="round" stroke-linejoin="round"/>
                                            </svg>
                                            
                                      </div>
                                <!-- <div class="frame-25">
                                  <p class="text-wrapper-8">Theme 4 - Water Sufficient</p>
                                  <img class="group-6" src="https://c.animaapp.com/Qr0MpKdr/img/group-3338@3x.png" />
                                </div> -->
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t4bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][4]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][4]['bgp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][4]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-4">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][4]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t4mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][4]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][4]['gp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;{api_data['pdi_s'][4]['gps']} </div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t4b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][4]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][4]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][4]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t4d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][4]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][4]['d_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;  {api_data['pdi_s'][4]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-20">
                                      <div class="rectangle-6t4s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][4]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][4]['s_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][4]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                <div class="frame-9">
                                    <div class="frame-26">
                                        <p class="text-wrapper-8">Theme 5 - Clean and Green</p>
                                        <!-- <img class="group-7" src="/frontend/images/Group 3342.svg" /> -->
                                        <svg class="group-7" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                          <circle cx="21" cy="21" r="21" fill="#99C83A"/>
                                          <path d="M16.6678 7.58243C12.5779 7.58243 4.12616 10.4721 4.12616 21.3007C4.12616 30.9305 16.1671 38.8755 26.7191 32.2925C28.416 31.2338 30.4827 28.8694 31.6272 26.2026M30.4002 23.2125C26.2775 21.7597 27.0464 17.9158 27.9462 16.1755C33.035 18.3983 33.1821 22.5795 31.6272 26.2026M31.6272 26.2026C32.4452 25.2816 34.7683 23.6665 37.5167 24.5745C37.5985 26.4662 36.4861 30.1133 31.3818 29.5685M25.7376 30.9305C25.3286 29.8712 23.4309 27.2077 19.1119 25.0285V20.4885H20.8297L14.6947 14.1324L7.82358 20.4885H9.78676V23.6665C9.13236 23.8804 7.62726 24.4978 6.84198 25.2555" stroke="white" stroke-width="2.24292" stroke-linecap="round" stroke-linejoin="round"/>
                                          <circle cx="22.2563" cy="12.7379" r="2.65598" stroke="white" stroke-width="2.24292"/>
                                          </svg>
                                          
                                      </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t5bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][5]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][5]['bgp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][5]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-dilla">
                                      <span class="text-wrapper-11">Best Panchayat&nbsp;&nbsp;</span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][5]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t5mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][5]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][5]['gp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][5]['gps']} </div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t5b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][5]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][5]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][5]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t5d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][5]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][5]['d_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; {api_data['pdi_s'][5]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-22">
                                      <div class="rectangle-6t5s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][5]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][5]['s_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][5]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                <div class="frame-9">
                                    <div class="frame-27">
                                        <p class="text-wrapper-8">Theme 6 - Self-sufficient Infrastructure</p>
                                        <!-- <img class="group-7" src="/frontend/images/Group 3337.svg" /> -->
                                        <svg class="group-7" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                          <circle cx="21" cy="21" r="21" fill="#FC852D"/>
                                          <path d="M21.5147 34.4158H6.18856V23.5824C6.0093 23.4019 4.79038 22.7699 3.49976 22.7699L13.9861 15.9991L23.9347 22.4991C23.3073 22.6797 21.9987 23.1491 21.7836 23.5824C21.5685 24.0158 21.694 26.2908 21.7836 27.3741C23.128 26.0199 27.1612 25.2074 27.9679 28.4574C28.3307 28.2747 28.8022 28.1742 29.3123 28.1681M27.9679 34.1449H32.0011C32.8615 33.7116 33.0766 32.5199 33.0766 31.9783C33.285 29.2492 31.0702 28.1473 29.3123 28.1681M29.3123 28.1681V22.2283M26.3546 13.0199V7.33243L29.3123 4.08243V10.0408M26.3546 13.0199H20.1703L23.9347 16.5408H29.3123M26.3546 13.0199H32.2699M29.3123 10.0408H34.6899L37.9164 13.0199H32.2699M29.3123 10.0408V16.5408M29.3123 16.5408V22.2283M29.3123 22.2283L32.2699 18.9783V13.0199" stroke="white" stroke-width="1.6805" stroke-linecap="round" stroke-linejoin="round"/>
                                          </svg>
                                          
                                      </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t6bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][6]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][6]['bgp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][6]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-4">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][6]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t6mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][6]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][6]['gp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;     {api_data['pdi_s'][6]['gps']}</div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t6b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][6]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;  {api_data['pdi_s'][6]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][6]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t6d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][6]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][6]['d_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][6]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-22">
                                      <div class="rectangle-6t6s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][6]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][6]['s_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][6]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                </div>
                                <div class="frame-8">
                                <div class="frame-9">
                                    <div class="frame-28">
                                        <div class="text-wrapper-8">Theme 7 -&nbsp;&nbsp;Socially Secured</div>
                                        <!-- <img class="group-6" src="/frontend/images/Group 3335.png" /> -->
                                        <svg class="group-6" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                          <circle cx="21" cy="21" r="21" fill="#044B79"/>
                                          <path d="M20.8023 21.8487V16.2776M20.8023 16.2776C19.62 16.1118 17.2553 17.299 17.2553 19.5274C17.7283 15.8134 10.6345 14.4206 9.92508 19.7595C9.76744 15.6586 11.7222 7.54971 20.8023 7.92111M20.8023 16.2776C23.6398 16.2776 24.428 18.4442 24.5856 19.5274C25.7679 13.9564 31.9159 16.5098 31.9159 19.5274C31.9947 15.8134 29.8823 8.29251 20.8023 7.92111M20.8023 7.92111C22.1422 8.84961 24.7275 11.6351 24.3492 15.3491M20.8023 7.92111C20.0949 8.37039 19.0406 9.32848 18.2584 10.7066C17.5587 11.9393 17.0767 13.5079 17.2553 15.3491M20.8023 7.92111V5.83197" stroke="white" stroke-width="1.71282" stroke-linecap="round" stroke-linejoin="round"/>
                                          <path d="M23.0196 26.0266C23.0196 27.2053 22.0418 28.1878 20.802 28.1878C19.5623 28.1878 18.5845 27.2053 18.5845 26.0266C18.5845 24.8478 19.5623 23.8653 20.802 23.8653C22.0418 23.8653 23.0196 24.8478 23.0196 26.0266Z" stroke="white" stroke-width="1.71282"/>
                                          <path d="M29.1681 23.705C29.1681 24.8837 28.1902 25.8662 26.9505 25.8662C25.7108 25.8662 24.7329 24.8837 24.7329 23.705C24.7329 22.5262 25.7108 21.5437 26.9505 21.5437C28.1902 21.5437 29.1681 22.5262 29.1681 23.705Z" stroke="white" stroke-width="1.71282"/>
                                          <path d="M15.4526 23.705C15.4526 24.8837 14.4748 25.8662 13.235 25.8662C11.9953 25.8662 11.0175 24.8837 11.0175 23.705C11.0175 22.5262 11.9953 21.5437 13.235 21.5437C14.4748 21.5437 15.4526 22.5262 15.4526 23.705Z" stroke="white" stroke-width="1.71282"/>
                                          <path d="M23.876 36.4716V33.0461C23.876 31.3484 22.4998 29.9721 20.802 29.9721V29.9721C19.1043 29.9721 17.7281 31.3484 17.7281 33.0461V36.4716" stroke="white" stroke-width="1.71282" stroke-linecap="round"/>
                                          <path d="M23.8765 29.7414C24.0852 27.2835 27.9758 26.9944 29.3756 28.874C29.7588 29.3885 29.788 30.0659 29.788 30.7074V34.1517" stroke="white" stroke-width="1.71282" stroke-linecap="round"/>
                                          <path d="M15.8362 34.1518V30.954C15.8362 29.3869 14.5658 28.1165 12.9987 28.1165V28.1165C11.4316 28.1165 10.1612 29.3869 10.1612 30.954V32.5424" stroke="white" stroke-width="1.71282" stroke-linecap="round"/>
                                          </svg>
                                          
                                      </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t7bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][7]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][7]['bgp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][7]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-3">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][7]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t7mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][7]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][7]['gp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][7]['gps']}</div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t7b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][7]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp; {api_data['pdi_s'][7]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][7]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t7d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][7]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][7]['d_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][7]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-24">
                                      <div class="rectangle-6t7s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][7]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][7]['s_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][7]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                <div class="frame-9">
                                    <div class="frame-29">
                                        <p class="text-wrapper-8">Theme 8 - Good Governance</p>
                                        <!-- <img class="group-3" src="/frontend/images/Group 3340.svg" /> -->
                                        <svg class="group-3" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                          <circle cx="21" cy="21" r="21" fill="#7B64AC"/>
                                          <path d="M32.4236 25.0832V22.9376M32.4236 20.792V22.9376M32.4236 22.9376H34.9996M32.4236 22.9376H28.1303M8.16626 22.9376H12.2449M12.2449 22.9376V20.3629M12.2449 22.9376H15.4649M12.2449 20.3629H9.88359M12.2449 20.3629H15.4649M29.8476 20.3629H28.1303M28.1303 20.3629V22.9376M28.1303 20.3629H25.1249M28.1303 22.9376H25.1249M25.1249 22.9376V20.3629M25.1249 22.9376H21.6903M25.1249 20.3629H21.6903M25.1249 20.3629V16.0717M21.6903 20.3629V22.9376M21.6903 20.3629H18.6849M21.6903 20.3629V16.0717M21.6903 22.9376H18.6849M18.6849 22.9376V20.3629M18.6849 22.9376H15.4649M18.6849 20.3629H15.4649M18.6849 20.3629V16.0717M15.4649 20.3629V22.9376M15.4649 20.3629V16.0717M12.6743 16.0717H15.4649M27.7009 16.0717H25.1249M25.1249 16.0717H21.6903M21.6903 16.0717H18.6849M18.6849 16.0717H15.4649M12.6743 13.7115H15.0356M27.7009 13.7115H25.5543M25.5543 13.7115C25.5543 13.7115 25.1249 8.34754 20.1876 8.34754M25.5543 13.7115H15.0356M20.1876 8.34754C14.6063 8.34754 15.0356 13.7115 15.0356 13.7115M20.1876 8.34754V6.4165" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                                          <circle cx="20.6197" cy="30.7151" r="5.33623" stroke="white" stroke-width="1.4"/>
                                          <path d="M21.482 29.8545L23.2066 28.3454M21.482 29.8545L21.9132 30.7168H24.5001M21.482 29.8545H20.6197M21.6976 31.5791L23.2066 33.5193M20.6197 34.3816V32.0103L19.7574 31.5791M19.7574 31.5791L17.8172 33.5193M19.7574 31.5791L19.5418 30.7168M19.5418 30.7168H16.9548M19.5418 30.7168L19.973 29.8545M19.973 29.8545L18.2483 28.3454M19.973 29.8545H20.6197M20.6197 29.8545V27.2675" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                                          <circle cx="20.8352" cy="30.933" r="0.809058" stroke="white" stroke-width="1.4"/>
                                          </svg>
                                          
                                      </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t8bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][8]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][8]['bgp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][8]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-5">
                                      <span class="text-wrapper-11">Best Panchayat&nbsp;&nbsp; </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][8]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t8mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][8]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][8]['gp_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;     {api_data['pdi_s'][8]['gps']}</div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t8b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][8]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][8]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;     {api_data['pdi_s'][8]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t8d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][8]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][8]['d_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][8]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-30">
                                      <div class="rectangle-6t8s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][8]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][8]['s_g'][:2]}   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][8]['s']} </div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                <div class="frame-9">
                                    <div class="frame-31">
                                        <p class="text-wrapper-8">Theme 9 - Women Friendly</p>
                                        <!-- <img class="group-2" src="/frontend/images/Group 3334.svg" /> -->
                                        <svg class="group-2" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                          <circle cx="21" cy="21" r="21" fill="#FA3E2B"/>
                                          <path d="M11.1953 31.2834H30.6847M11.1953 36.1676H30.6847" stroke="white" stroke-width="1.97136" stroke-linecap="round" stroke-linejoin="round"/>
                                          <path d="M18.9914 14.5745H11.9265C11.5204 14.8316 10.8058 15.5514 11.1956 16.374L16.068 26.3994C16.3116 26.8278 16.9937 27.4276 17.7733 26.3994L23.9889 16.374C24.272 15.6885 25.0818 14.7288 26.0563 16.374C27.0308 18.0192 29.5481 23.0576 30.685 25.3711C30.8474 25.7996 30.9286 26.7079 29.9542 26.9135H23.9889" stroke="white" stroke-width="1.97136" stroke-linecap="round" stroke-linejoin="round"/>
                                          <path d="M17.0312 9.1753C17.0312 10.5271 16.0053 11.5314 14.8498 11.5314C13.6943 11.5314 12.6685 10.5271 12.6685 9.1753C12.6685 7.82349 13.6943 6.81917 14.8498 6.81917C16.0053 6.81917 17.0312 7.82349 17.0312 9.1753Z" stroke="white" stroke-width="1.97136"/>
                                          <path d="M27.2634 9.1753C27.2634 10.5271 26.2375 11.5314 25.082 11.5314C23.9265 11.5314 22.9007 10.5271 22.9007 9.1753C22.9007 7.82349 23.9265 6.81917 25.082 6.81917C26.2375 6.81917 27.2634 7.82349 27.2634 9.1753Z" stroke="white" stroke-width="1.97136"/>
                                          </svg>
                                          
                                      </div>
                                <div class="frame-11">
                                  <div class="frame-12">
                                    <div class="frame-13">
                                      <div class="rectangle-2t9bp"></div>
                                      <!-- <div class="text-wrapper-9">{api_data['pdi_s'][9]['bgp']}</div> -->
                                      <div class="text-wrapper-10">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][9]['bgp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][9]['bgp']}</div>
                                    </div>
                                    <p class="best-panchayat-3">
                                      <span class="text-wrapper-11">Best Panchayat </span>
                                      <span class="text-wrapper-4">{api_data['pdi_s'][9]['bgpn']}</span>
                                    </p>
                                  </div>
                                  <div class="frame-14">
                                    <div class="frame-15">
                                      <div class="rectangle-3t9mp"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][9]['gps']}</div> -->
                                      <div class="text-wrapper-13">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][9]['gp_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][9]['gps']}</div>
                                    </div>
                                    <div class="text-wrapper-14">My Panchayat</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-17">
                                      <div class="rectangle-4t9b"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][9]['b']}</div> -->
                                      <div class="text-wrapper-15">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][9]['b_g'][:2]} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;   {api_data['pdi_s'][9]['b']}</div>
                                    </div>
                                    <div class="text-wrapper-14">Block</div>
                                  </div>
                                  <div class="frame-16">
                                    <div class="frame-18">
                                      <div class="rectangle-5t9d"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][9]['d']}</div> -->
                                      <div class="text-wrapper-16">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][9]['d_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][9]['d']}</div>
                                    </div>
                                    <div class="text-wrapper-14">District</div>
                                  </div>
                                  <div class="frame-19">
                                    <div class="frame-32">
                                      <div class="rectangle-6t9s"></div>
                                      <!-- <div class="text-wrapper-12">{api_data['pdi_s'][9]['s']}</div> -->
                                      <div class="text-wrapper-17">&nbsp; &nbsp;&nbsp;{api_data['pdi_s'][9]['s_g'][:2]}  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  &nbsp; &nbsp; &nbsp; &nbsp;    {api_data['pdi_s'][9]['s']}</div>
                                    </div>
                                    <div class="text-wrapper-14">State</div>
                                  </div>
                                </div>
                                </div>
                                </div>
                          </div>
                          <div class="frame-33">
                            <div class="frame-34"><div class="text-wrapper-19">Grade Guidance</div></div>
                            <div class="frame-35">
                              <div class="frame-wrapper">
                                <div class="frame-36">
                                  <div class="rectangle-7"></div>
                                  <div class="frame-37">
                                    <div class="text-wrapper-20">A+&nbsp;&nbsp;- Achiever</div>
                                    <p class="text-wrapper-21">PDI Score between 90 and 100</p>
                                  </div>
                                </div>
                              </div>
                              <div class="frame-38">
                                <div class="frame-36">
                                  <div class="rectangle-8"></div>
                                  <div class="frame-37">
                                    <div class="text-wrapper-20">A&nbsp;&nbsp;- Front Runner</div>
                                    <p class="text-wrapper-21">PDI Score between 75 and 89</p>
                                  </div>
                                </div>
                              </div>
                              <div class="frame-38">
                                <div class="frame-36">
                                  <div class="rectangle-9"></div>
                                  <div class="frame-37">
                                    <div class="text-wrapper-20">B&nbsp;&nbsp;-&nbsp;&nbsp;Performer</div>
                                    <p class="text-wrapper-21">PDI Score between 60 and 74</p>
                                  </div>
                                </div>
                              </div>
                              <div class="frame-38">
                                <div class="frame-36">
                                  <div class="rectangle-10"></div>
                                  <div class="frame-37">
                                    <div class="text-wrapper-20">C&nbsp;&nbsp;- Aspirant</div>
                                    <p class="text-wrapper-21">PDI Score between 40 and 59</p>
                                  </div>
                                </div>
                              </div>
                              <div class="frame-38">
                                <div class="frame-36">
                                  <div class="rectangle-11"></div>
                                  <div class="frame-37">
                                    <div class="text-wrapper-20">D&nbsp;&nbsp;- Beginner</div>
                                    <p class="text-wrapper-21">PDI Score between 0 and 39</p>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div class="frame-39">
                            <div class="frame-34"><p class="text-wrapper-7">PDI Score of Your Gram Panchayat</p></div>
                            <div class="frame-40">
                              <div class="group-8">
                                <div class="overlap-2">
                                  <div class="t">
                                    <div class="img-wrapper">
                                        <svg class="group-9" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <g id="Group 3339">
                                            <g id="Group 5">
                                            <circle id="Ellipse 3" cx="21" cy="21" r="21" fill="#95192F"/>
                                            <g id="Group 3">
                                            <path id="Vector 2" d="M10.6418 26.5587V21.967C10.7223 20.7587 11.7534 18.4387 15.2334 18.8253M15.2334 18.8253V24.142M15.2334 18.8253C15.7168 17.1337 17.3601 14.0403 20.0668 15.2003M20.0668 15.2003V22.4503M20.0668 15.2003V11.817C20.3084 9.64197 24.1751 8.91696 25.3834 11.817V23.417C25.6251 23.417 26.0907 22.7962 26.3501 22.4503C27.0751 21.4836 29.4918 18.5836 31.9084 20.7586C31.1029 22.2086 29.7334 25.012 29.7334 25.592C29.7334 26.172 26.189 29.8614 24.4168 31.6336C24.6584 33.567 23.3091 37.917 18.6168 37.917C13.7834 37.917 12.0918 33.8086 12.3334 31.8753C12.0918 28.0086 17.1668 23.6586 22.4834 27.5253M15.2334 29.7003H19.3418M22.0001 29.7003H19.3418M19.3418 29.7003C19.5029 30.667 19.5834 32.697 18.6168 33.0836M18.6168 33.0836H22.0001H17.2884M18.6168 33.0836H17.2884M14.9918 33.0836H17.2884M17.2884 33.0836C17.1673 33.8892 17.4084 35.5486 19.3418 35.742" stroke="white" stroke-width="1.35733" stroke-linecap="round" stroke-linejoin="round"/>
                                            <circle id="Ellipse 3_2" cx="12.0919" cy="14.957" r="1.49634" stroke="white" stroke-width="1.35733"/>
                                            <circle id="Ellipse 4" cx="16.9257" cy="11.5749" r="1.49634" stroke="white" stroke-width="1.35733"/>
                                            <circle id="Ellipse 5" cx="22.7257" cy="6.2577" r="1.49634" stroke="white" stroke-width="1.35733"/>
                                            </g>
                                            </g>
                                            </g>
                                            </svg>
                                            
                                      <!-- <img class="group-9" src="/frontend/images/Group 3339.svg" /> -->
                                    </div>
                                   <!-- <div class="img-wrapper">
                        <img class="group-9" src="https://c.animaapp.com/Qr0MpKdr/img/group-3339-1@3x.png" />
                        </div> -->
                        <div class="group-10">
                        <div class="text-wrapper-22">Poverty Free</div>
                        <div class="group-11">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s1"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t1']}</div>
                        </div>
                        </div>
                        </div>
                        </div>
                        <div class="group-12">
                        <div class="overlap-3"><div class="text-wrapper-24">T1</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-8">
                        <div class="overlap-4">
                        <div class="t-2">
                        <div class="overlap-5">
                        <div class="group-13">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s2"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t2']}</div>
                        </div>
                        </div>
                        <div class="text-wrapper-25">Healthy</div>
                        <div class="overlap-6">
                        <!-- <img class="group-14" src="/frontend/images/Group 3336.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#23B67A"/>
                            <path d="M30.0688 23.3209H38.2209C37.8183 27.5693 34.2958 36.0659 23.4263 36.0659V31.62H28.5591V25.9885H23.4263V24.2101C25.9424 22.8269 30.733 19.0529 29.7669 15.0219H25.5398C24.6341 15.0219 23.9698 15.1404 23.7283 16.8003V18.875C23.7283 19.7642 23.4263 20.6534 22.2186 20.6534H18.8974M18.5955 15.0219L11.9531 15.0219C11.6514 18.2822 12.9797 21.7204 18.2937 23.6173V25.9885H13.4629V31.62H18.2937V36.0659C12.5571 36.9551 5.31084 31.9164 3.49927 23.3209H11.0475" stroke="white" stroke-width="1.84209" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M17.6749 9.09329C17.6749 10.3693 16.6164 11.4326 15.2747 11.4326C13.933 11.4326 12.8745 10.3693 12.8745 9.09329C12.8745 7.81732 13.933 6.75399 15.2747 6.75399C16.6164 6.75399 17.6749 7.81732 17.6749 9.09329Z" stroke="white" stroke-width="1.84209"/>
                            <path d="M29.1485 9.09329C29.1485 10.3693 28.09 11.4326 26.7483 11.4326C25.4066 11.4326 24.3481 10.3693 24.3481 9.09329C24.3481 7.81732 25.4066 6.75399 26.7483 6.75399C28.09 6.75399 29.1485 7.81732 29.1485 9.09329Z" stroke="white" stroke-width="1.84209"/>
                            <path d="M37.602 17.9843C37.602 19.2603 36.5436 20.3236 35.2018 20.3236C33.8601 20.3236 32.8017 19.2603 32.8017 17.9843C32.8017 16.7083 33.8601 15.645 35.2018 15.645C36.5436 15.645 37.602 16.7083 37.602 17.9843Z" stroke="white" stroke-width="1.84209"/>
                            <path d="M9.22066 17.9843C9.22066 19.2603 8.1622 20.3236 6.82049 20.3236C5.47877 20.3236 4.42031 19.2603 4.42031 17.9843C4.42031 16.7083 5.47877 15.645 6.82049 15.645C8.1622 15.645 9.22066 16.7083 9.22066 17.9843Z" stroke="white" stroke-width="1.84209"/>
                            </svg>
                            
                        </div>
                        </div>
                        </div>
                        <div class="group-15">
                        <div class="overlap-3"><div class="text-wrapper-26">T2</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-8">
                        <div class="overlap-4">
                        <div class="t-2">
                        <div class="overlap-5">
                        <div class="group-13">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s3"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t3']}</div>
                        </div>
                        </div>
                        <div class="overlap-7">
                        <!-- <img class="group-14" src="/frontend/images/Group 3341.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#FCB732"/>
                            <path d="M29.5071 18.8415C33.9793 26.4287 27.2293 35.3346 22.3247 36.1876C20.9696 29.9538 23.9509 26.9725 26.1192 23.178C21.5116 30.4959 15.5489 27.7856 11.2124 23.9911C15.4648 27.5145 15.7296 33.8386 15.2779 36.1876C4.00295 31.6342 6.24348 21.8229 8.77312 17.4863L6.60486 15.5891L5.24969 16.6732L5.52073 8.8133L13.6517 9.35536L12.2965 10.9816L14.1938 13.4209C14.8442 12.7704 16.6331 12.6078 17.4462 12.6078L17.7172 10.4395H15.82L20.4275 5.83194L24.764 10.9816H23.1378V13.1498C26.2586 14.8258 28.295 16.7852 29.5071 18.8415ZM29.5071 18.8415L31.2688 17.4863M31.2688 17.4863C33.2203 19.6546 35.1536 18.5705 35.8764 17.7574C37.7736 15.3181 36.1474 13.4209 35.0633 12.8788M31.2688 17.4863C30.5921 16.8096 30.5912 15.322 31.2324 14.1707M35.0633 12.8788C37.0147 7.89179 32.895 6.10297 30.7268 6.64504C26.7045 7.65059 27.2033 12.0657 28.8295 13.4209M35.0633 12.8788C33.1636 12.2003 31.8753 13.0164 31.2324 14.1707M26.9323 15.5891L28.8295 13.4209M28.8295 13.4209C29.3716 13.8726 30.4557 14.505 31.2324 14.1707" stroke="white" stroke-width="1.67327" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="18.8011" cy="22.906" r="2.41575" stroke="white" stroke-width="1.67327"/>
                            </svg>
                            
                        </div>
                        <div class="text-wrapper-27">Child Friendly</div>
                        </div>
                        </div>
                        <div class="group-12">
                        <div class="overlap-3"><div class="text-wrapper-26">T3</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-16">
                        <div class="overlap-8">
                        <div class="t-3">
                        <div class="overlap-9">
                        <div class="overlap-10">
                        <!-- <img class="group-14" src="/frontend/images/Group 3338.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#47BFE8"/>
                            <path d="M16.9411 9.28507C16.6881 10.563 25.7954 10.8185 25.2894 9.28507M14.4113 17.208C15.9292 17.208 16.4123 19.1311 17.953 18.997C19.3726 18.8735 19.564 16.9524 20.9888 16.9524C22.4136 16.9524 22.6 18.9707 24.0246 18.997C25.3968 19.0224 25.5424 16.9524 27.0603 17.208M12.8934 9.28507C11.6286 4.94032 29.0842 4.42914 29.0842 9.28507C29.0841 10.563 27.9036 11.2445 27.5663 11.5853C26.0484 13.1188 26.8073 14.5793 28.0722 15.6746C29.8431 17.208 33.7681 20.275 32.3729 26.92C30.9562 33.6673 25.2052 35.8652 22.5067 36.1208C15.9292 36.632 11.1119 32.7059 9.60471 26.92C8.33977 22.064 11.7972 17.5488 13.9054 15.6746C15.6762 13.8855 15.4232 13.1188 14.1584 11.5853C14.1584 11.5853 13.3399 10.8186 12.8934 9.28507Z" stroke="white" stroke-width="1.70768" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            
                        </div>
                        <div class="group-17">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s4"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t4']}</div>
                        </div>
                        </div>
                        <div class="text-wrapper-28">Water Sufficient</div>
                        </div>
                        </div>
                        <div class="group-12">
                        <div class="overlap-3"><div class="text-wrapper-26">T4</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-16">
                        <div class="overlap-8">
                        <div class="t-3">
                        <div class="overlap-9">
                        <div class="group-17">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s5"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t5']}</div>
                        </div>
                        </div>
                        <div class="overlap-11">
                        <!-- <img class="group-14" src="/frontend/images/Group 3342.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#99C83A"/>
                            <path d="M16.6678 7.58243C12.5779 7.58243 4.12616 10.4721 4.12616 21.3007C4.12616 30.9305 16.1671 38.8755 26.7191 32.2925C28.416 31.2338 30.4827 28.8694 31.6272 26.2026M30.4002 23.2125C26.2775 21.7597 27.0464 17.9158 27.9462 16.1755C33.035 18.3983 33.1821 22.5795 31.6272 26.2026M31.6272 26.2026C32.4452 25.2816 34.7683 23.6665 37.5167 24.5745C37.5985 26.4662 36.4861 30.1133 31.3818 29.5685M25.7376 30.9305C25.3286 29.8712 23.4309 27.2077 19.1119 25.0285V20.4885H20.8297L14.6947 14.1324L7.82358 20.4885H9.78676V23.6665C9.13236 23.8804 7.62726 24.4978 6.84198 25.2555" stroke="white" stroke-width="2.24292" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="22.2563" cy="12.7379" r="2.65598" stroke="white" stroke-width="2.24292"/>
                            </svg>
                            
                        </div>
                        <div class="text-wrapper-29">Clean and Green</div>
                        </div>
                        </div>
                        <div class="group-12">
                        <div class="overlap-3"><div class="text-wrapper-26">T5</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-16">
                        <div class="overlap-8">
                        <div class="t-3">
                        <div class="overlap-9">
                        <div class="group-17">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s6"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t6']}</div>
                        </div>
                        </div>
                        <div class="overlap-12">
                        <!-- <img class="group-14" src="/frontend/images/Group 3337.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#FC852D"/>
                            <path d="M21.5147 34.4158H6.18856V23.5824C6.0093 23.4019 4.79038 22.7699 3.49976 22.7699L13.9861 15.9991L23.9347 22.4991C23.3073 22.6797 21.9987 23.1491 21.7836 23.5824C21.5685 24.0158 21.694 26.2908 21.7836 27.3741C23.128 26.0199 27.1612 25.2074 27.9679 28.4574C28.3307 28.2747 28.8022 28.1742 29.3123 28.1681M27.9679 34.1449H32.0011C32.8615 33.7116 33.0766 32.5199 33.0766 31.9783C33.285 29.2492 31.0702 28.1473 29.3123 28.1681M29.3123 28.1681V22.2283M26.3546 13.0199V7.33243L29.3123 4.08243V10.0408M26.3546 13.0199H20.1703L23.9347 16.5408H29.3123M26.3546 13.0199H32.2699M29.3123 10.0408H34.6899L37.9164 13.0199H32.2699M29.3123 10.0408V16.5408M29.3123 16.5408V22.2283M29.3123 22.2283L32.2699 18.9783V13.0199" stroke="white" stroke-width="1.6805" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            
                        </div>
                        <div class="self-sufficient">Self-Sufficient Infrastructure</div>
                        </div>
                        </div>
                        <div class="group-12">
                        <div class="overlap-3"><div class="text-wrapper-30">T6</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-8">
                        <div class="overlap-4">
                        <div class="t-2">
                        <div class="overlap-5">
                        <div class="overlap-13">
                        <!-- <img class="group-14" src="/frontend/images/Group 3335.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#044B79"/>
                            <path d="M20.8023 21.8487V16.2776M20.8023 16.2776C19.62 16.1118 17.2553 17.299 17.2553 19.5274C17.7283 15.8134 10.6345 14.4206 9.92508 19.7595C9.76744 15.6586 11.7222 7.54971 20.8023 7.92111M20.8023 16.2776C23.6398 16.2776 24.428 18.4442 24.5856 19.5274C25.7679 13.9564 31.9159 16.5098 31.9159 19.5274C31.9947 15.8134 29.8823 8.29251 20.8023 7.92111M20.8023 7.92111C22.1422 8.84961 24.7275 11.6351 24.3492 15.3491M20.8023 7.92111C20.0949 8.37039 19.0406 9.32848 18.2584 10.7066C17.5587 11.9393 17.0767 13.5079 17.2553 15.3491M20.8023 7.92111V5.83197" stroke="white" stroke-width="1.71282" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M23.0196 26.0266C23.0196 27.2053 22.0418 28.1878 20.802 28.1878C19.5623 28.1878 18.5845 27.2053 18.5845 26.0266C18.5845 24.8478 19.5623 23.8653 20.802 23.8653C22.0418 23.8653 23.0196 24.8478 23.0196 26.0266Z" stroke="white" stroke-width="1.71282"/>
                            <path d="M29.1681 23.705C29.1681 24.8837 28.1902 25.8662 26.9505 25.8662C25.7108 25.8662 24.7329 24.8837 24.7329 23.705C24.7329 22.5262 25.7108 21.5437 26.9505 21.5437C28.1902 21.5437 29.1681 22.5262 29.1681 23.705Z" stroke="white" stroke-width="1.71282"/>
                            <path d="M15.4526 23.705C15.4526 24.8837 14.4748 25.8662 13.235 25.8662C11.9953 25.8662 11.0175 24.8837 11.0175 23.705C11.0175 22.5262 11.9953 21.5437 13.235 21.5437C14.4748 21.5437 15.4526 22.5262 15.4526 23.705Z" stroke="white" stroke-width="1.71282"/>
                            <path d="M23.876 36.4716V33.0461C23.876 31.3484 22.4998 29.9721 20.802 29.9721V29.9721C19.1043 29.9721 17.7281 31.3484 17.7281 33.0461V36.4716" stroke="white" stroke-width="1.71282" stroke-linecap="round"/>
                            <path d="M23.8765 29.7414C24.0852 27.2835 27.9758 26.9944 29.3756 28.874C29.7588 29.3885 29.788 30.0659 29.788 30.7074V34.1517" stroke="white" stroke-width="1.71282" stroke-linecap="round"/>
                            <path d="M15.8362 34.1518V30.954C15.8362 29.3869 14.5658 28.1165 12.9987 28.1165V28.1165C11.4316 28.1165 10.1612 29.3869 10.1612 30.954V32.5424" stroke="white" stroke-width="1.71282" stroke-linecap="round"/>
                            </svg>
                            
                        </div>
                        <div class="group-13">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s7"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t7']}</div>
                        </div>
                        </div>
                        <div class="text-wrapper-31">Socially Secured</div>
                        </div>
                        </div>
                        <div class="group-18">
                        <div class="overlap-3"><div class="text-wrapper-26">T7</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-8">
                        <div class="overlap-4">
                        <div class="t-2">
                        <div class="overlap-5">
                        <div class="group-13">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s8"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t8']}</div>
                        </div>
                        </div>
                        <div class="overlap-14">
                        <!-- <img class="group-14" src="/frontend/images/Group 3340.svg" /> -->
                        <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="21" cy="21" r="21" fill="#7B64AC"/>
                            <path d="M32.4236 25.0832V22.9376M32.4236 20.792V22.9376M32.4236 22.9376H34.9996M32.4236 22.9376H28.1303M8.16626 22.9376H12.2449M12.2449 22.9376V20.3629M12.2449 22.9376H15.4649M12.2449 20.3629H9.88359M12.2449 20.3629H15.4649M29.8476 20.3629H28.1303M28.1303 20.3629V22.9376M28.1303 20.3629H25.1249M28.1303 22.9376H25.1249M25.1249 22.9376V20.3629M25.1249 22.9376H21.6903M25.1249 20.3629H21.6903M25.1249 20.3629V16.0717M21.6903 20.3629V22.9376M21.6903 20.3629H18.6849M21.6903 20.3629V16.0717M21.6903 22.9376H18.6849M18.6849 22.9376V20.3629M18.6849 22.9376H15.4649M18.6849 20.3629H15.4649M18.6849 20.3629V16.0717M15.4649 20.3629V22.9376M15.4649 20.3629V16.0717M12.6743 16.0717H15.4649M27.7009 16.0717H25.1249M25.1249 16.0717H21.6903M21.6903 16.0717H18.6849M18.6849 16.0717H15.4649M12.6743 13.7115H15.0356M27.7009 13.7115H25.5543M25.5543 13.7115C25.5543 13.7115 25.1249 8.34754 20.1876 8.34754M25.5543 13.7115H15.0356M20.1876 8.34754C14.6063 8.34754 15.0356 13.7115 15.0356 13.7115M20.1876 8.34754V6.4165" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="20.6197" cy="30.7151" r="5.33623" stroke="white" stroke-width="1.4"/>
                            <path d="M21.482 29.8545L23.2066 28.3454M21.482 29.8545L21.9132 30.7168H24.5001M21.482 29.8545H20.6197M21.6976 31.5791L23.2066 33.5193M20.6197 34.3816V32.0103L19.7574 31.5791M19.7574 31.5791L17.8172 33.5193M19.7574 31.5791L19.5418 30.7168M19.5418 30.7168H16.9548M19.5418 30.7168L19.973 29.8545M19.973 29.8545L18.2483 28.3454M19.973 29.8545H20.6197M20.6197 29.8545V27.2675" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="20.8352" cy="30.933" r="0.809058" stroke="white" stroke-width="1.4"/>
                            </svg>
                            
                        </div>
                        <div class="good-governance">Good Governance</div>
                        </div>
                        </div>
                        <div class="group-18">
                        <div class="overlap-3"><div class="text-wrapper-30">T8</div></div>
                        </div>
                        </div>
                        </div>
                        <div class="group-8">
                        <div class="overlap-4">
                        <div class="t-2">
                        <div class="overlap-5">
                        <div class="group-13">
                        <div class="overlap-group-2">
                        <div class="rectangle-12s9"></div>
                        <div class="text-wrapper-23">{api_data['matrix'][0]['t9']}</div>
                        </div>
                        </div>
                <div class="overlap-15">
                    <!-- <img class="group-14" src="/frontend/images/Group 3334.svg" /> -->
                    <svg class="group-14" width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="21" cy="21" r="21" fill="#FA3E2B"/>
                        <path d="M11.1953 31.2834H30.6847M11.1953 36.1676H30.6847" stroke="white" stroke-width="1.97136" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M18.9914 14.5745H11.9265C11.5204 14.8316 10.8058 15.5514 11.1956 16.374L16.068 26.3994C16.3116 26.8278 16.9937 27.4276 17.7733 26.3994L23.9889 16.374C24.272 15.6885 25.0818 14.7288 26.0563 16.374C27.0308 18.0192 29.5481 23.0576 30.685 25.3711C30.8474 25.7996 30.9286 26.7079 29.9542 26.9135H23.9889" stroke="white" stroke-width="1.97136" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M17.0312 9.1753C17.0312 10.5271 16.0053 11.5314 14.8498 11.5314C13.6943 11.5314 12.6685 10.5271 12.6685 9.1753C12.6685 7.82349 13.6943 6.81917 14.8498 6.81917C16.0053 6.81917 17.0312 7.82349 17.0312 9.1753Z" stroke="white" stroke-width="1.97136"/>
                        <path d="M27.2634 9.1753C27.2634 10.5271 26.2375 11.5314 25.082 11.5314C23.9265 11.5314 22.9007 10.5271 22.9007 9.1753C22.9007 7.82349 23.9265 6.81917 25.082 6.81917C26.2375 6.81917 27.2634 7.82349 27.2634 9.1753Z" stroke="white" stroke-width="1.97136"/>
                        </svg>
                        
                  </div>
                <div class="text-wrapper-32">Women Friendly</div>
              </div>
            </div>
            <div class="group-18">
              <div class="overlap-3"><div class="text-wrapper-30">T9</div></div>
            </div>
            </div>
            </div>
            </div>
            </div>
            <div class="frame-41">
            <div class="your-panchayat-PDI-wrapper">
            <div class="your-panchayat-PDI">Your Panchayat&nbsp;&nbsp;PDI Score</div>
            </div>
            <div class="frame-42">
            <div class="frame-43">
            <div class="frame-44">
            <div class="rectangle-scmp"></div>
                
                <div class="text-wrapper-101">{api_data['pdi_s'][0]['gp_g']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{api_data['pdi_s'][0]['gps']}</div>
            
            <!-- <div class="rectangle-mp"></div>
            <div class="text-wrapper-33">{ api_data['matrix'][0]['pdi_score'] }</div> -->
            <!-- <p class="c-aspirant">
              <span class="text-wrapper-11">{api_data['pdi_s'][0]['gp_g']}</span>
            </p> -->
            </div>
            <div class="text-wrapper-34">My Panchayat PDI Score</div>
            </div>
            <div class="frame-14">
            <div class="frame-45">
            <div class="rectangle-scmp2"></div>
                
                <div class="text-wrapper-101">{api_data['pdi_s'][0]['bgp_g']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{api_data['pdi_s'][0]['bgp']}</div>
            
            
            <!-- <div class="text-wrapper-33">{api_data['pdi_s'][0]['bgp'] }</div>
            <p class="div-3">
              <span class="text-wrapper-11">{api_data['pdi_s'][0]['bgp_g']}</span>
            </p> -->
            </div>
            <div class="flexcontainer">
            <p class="text">
              <span class="text-wrapper-11">BP&nbsp;&nbsp;Score </span>
            </p>
            <p class="text"><span class="text-wrapper-4">{api_data['pdi_s'][0]['bgpn'] }  </span></p>
            </div>
            </div>
            <div class="frame-16">
            <div class="frame-46">
            
            <div class="rectangle-scmp3"></div>
                
                <div class="text-wrapper-101">{api_data['pdi_s'][0]['b_g']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{api_data['pdi_s'][0]['b']}</div>
            
            
            <!-- <div class="rectangle-Block"></div>
            <div class="text-wrapper-33">{api_data['pdi_s'][0]['b']}</div>
            <p class="div-3">
              <span class="text-wrapper-11">{api_data['pdi_s'][0]['d_g']}</span>
            </p> -->
            </div>
            <div class="block-PDI-score">Block&nbsp;&nbsp;PDI Score</div>
            </div>
            <div class="frame-16">
            <div class="frame-47">
            
            <div class="rectangle-scmp4"></div>
                
                <div class="text-wrapper-101">{api_data['pdi_s'][0]['d_g']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{api_data['pdi_s'][0]['d']}</div>
            
            <!-- <div class="rectangle-16"></div>
            <div class="text-wrapper-33">{api_data['pdi_s'][0]['d']}</div>
            <p class="d-beginner">
              <span class="text-wrapper-11">{api_data['pdi_s'][0]['d_g']}</span>
            </p> -->
            </div>
            <div class="district-PDI-score">District&nbsp;&nbsp;PDI Score</div>
            </div>
            <div class="frame-16">
            <div class="frame-48">
            <div class="rectangle-scmp5"></div>
                
                <div class="text-wrapper-101">{api_data['pdi_s'][0]['s_g']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{api_data['pdi_s'][0]['s']}</div>
            <!-- <div class="rectangle-17sps"></div>
            <div class="text-wrapper-33">{api_data['pdi_s'][0]['s']}</div>
            <p class="div-3">
              <span class="text-wrapper-11">{api_data['pdi_s'][0]['s_g']}</span>
            </p> -->
            </div>
            <div class="text-wrapper-35">State PDI Score</div>
            </div>
            </div>
            </div>
            <div class="frame-49">
            <div class="frame-50"><div class="text-wrapper-36">Panchayat Population</div></div>
            <div class="frame-51">
            <div class="people-together-wrapper">
                        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                          <rect width="22" height="22" fill="url(#pattern0_1_655)"/>
                          <defs>
                          <pattern id="pattern0_1_655" patternContentUnits="objectBoundingBox" width="1" height="1">
                          <use xlink:href="#image0_1_655" transform="scale(0.00195312)"/>
                          </pattern>
                          <image id="image0_1_655" width="512" height="512" xlink:href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAACAASURBVHic7J13uF1F9bDfe9MDCaTQW0IJvVeVLlV6FSlBQUGQogiiKFJsKCDSFARURDr+EFB6lS6h95rQEwgkgfTk5n5/rHM/LpdbzjlrTdn7rPd51hNK9sya2fvsWXtmlSYcxykTA4GVgJHAiIosDgwDhlf+7Ff5uwsCTcCnwFygBfionXwIjKvIWODFyn93HKcENKVWwHGcuhkArAd8BVgXWANYDugVsM/3gGeBJ4GHgYeAiQH7cxwnEG4AOE5x6IUs+NsD21T+uU9SjYSXgLuAW4B7gOlp1XEcx3Gc4tMb2Ba4BNmSb81cZgD/AQ4EFggwH47jOI5TatYCzkO211Mv6vXKTOB6YEfCHks4juM4TqHpBxwE/I/0i7e1vA2cDCxiNVmO4ziOU3SGAz8DxpN+oY6xK3AxsIrJzDmO4zhOARmKfBVPIf3CHFvmATchRx2O4ziO0xDMB5xEYy78HaUF+AewjGpGHcdxHCdjmoC9kMQ6qRfe3GQWcDYwuN7JdRzHcZwcWRVJmpN6oc1d3gV2r3OOHcdxHCcb+gDHI85vqRfXIslNwFJ1zLfjOI7jJGcVJGVu6sW0qDIZ2K/mWXccx3GcRDQBhwDTSL+IlkGuQQoXOY7jOE62DAKuI/2iWTZ5FVi9hvvgOI7jONFYCXiB9ItlWWU68M1qb4bjON3j1QAdx4adgCuA+VMrgiyWbwOvVOQl4HXgY2QRnYqcr08H5iChd4OQ/ATzAUOApYFRFVkJWBboG3MQ3XAacAIyTsdxHMdJxpHAXNJ9Gc8C/gucAmwODAwwxt7AGsDRwA3ApITjbQWuAvoHGKfjOI7j9EgT8DvSLIAfIIlztibMgt8TvYB1kS/x56vQN4T8Fy857DiO40SmCVmAYy54M5H4+L2Q/AI5sSqyNf8+cefkcWChCONzHMdxHHoBlxJvkXsb+D7FCIXrDewKPEK8+XkOLzPsOI7jBKYJuJA4C9sbyJl7Uc+6N0Z2LGLM1TPAsDjDchzHcRqRc4mz8O+L7DSUgS8BdxN+3sbgPgGO4zhOAE4m7AI2EzgVGBBpPLH5BvAeYefwHvIJV3Qcx3FKwDeAeYRbuO4GVo42mnTMhxhSswg3l1fiOU4cx3EcA7YEZhNmsZqCbPc3GmsRNmviqfGG4jiO45SRpZGY+xCL1OPA8vGGkh0DCOdQOQ8Jl3Qcx3GcmukPPEaYBervlPesv1ZGA59iP8efIvkJHMdxHKcm/oz9ojQd/zLtjJWRegXW8/08aTIlOo7jOAVlN+wXo0nApjEHUTAWQY5FrOf9TzEH4TiO4xSXJYCJ2C5C7yGOb073zA/chr0RsEvMQTiO4zjF5BZsF5+XgGWijqDY9AOuwfYeTMAzBTqO4zjdMBrbhectYKmoIygHvYBrsb0Xl0YdgeM4jlMYFsZ2638CsELUEZSL/sB92BoB20YdgeM4jlMI/oLdQvMJsG5c9UvJYOAJ7O7La8gRg+M4juMAsli3YLPIzEKyBzo2LIYUSLIyAn4UV33HcRwnZ+7HboE5KrLujcA6SLEki/szBQk5dBzHcRqcnbFb/G/EC9GE4nDs7tM5kXV3HMdxMqMJeBKbRWUcMDSq9o3HP7A7phkZWXfHcRwnI/bCZkGZCawXWfdGZDDwCjb37KLIujuO4zgZYeVhflJsxRuYjZFqf9p7NhvP0eA4jtOQfBWbxf8VJGa9kRgEbA0cAnwTiXqIWd3QKmTzdxF1dhzHcTLBKuXvNrEVT8gQ4DxgKl+ch2nAucDwCHosBHzUiQ61ymTkWMFxHMdpEEZhs418dWzFE7IW8C49z8nbxCl8dEgVulQjR0TQ1XEcx8mE09EvHNORyoGNwCiknHG1czMeWDKwTs3AmBp06kqeCayn4ziOkwn9gA/QLxyNEkvei/pCJa+PoJtVDoeNIujqOI7jJGYP9AvGLBrHg/xA6pujeYQvhtQEPFWnfu3lwsB6Oo7jOBlwHb5g1IImTXKMtMh7K/Rrk4+BvhF0dRzHcRIxP+Ktrlks5gDLxVY8ESPRFUm6N4KOzcALCh3bZLsIujqO4ziJ2Af9QnFtdK3TcQr6+do+gp7fMdDzkgh6Oo7jOIm4DP1CsUN0rdPQH3gP/XyNRRIHhWQwEpWh0fN9vJCT4zhOKWlG7/0/HugdW/FEHIN+8W+TP0bQ90oDPdeNoKfjOI4TmQ3QLxC/j651GoZjk2mvTeYBWwXWeXsDPX8WWEfHcRwnAT9Gv0CsGV3rNFyC3eLfJhMJW4K3N/ojizsD6uc4juMk4kZ0i8NL8VVOwpbYpEnuTB4nbNGg85T6TQX6BNTPcRzHiUwT8gWqWRzOi651fBbBxvGvO7k8oP67Gei3fkD9HMdxnMiMQr8w7BFd67j0RuL2Qy7+bXJsoDEMAeYqdYuRvMhxHMeJxF7oFoUWYFh0rePRhGQ3jLH4tyKL9C6BxvKYUreLA+nlOI7jJOCX6BaFx+OrHJXfEW/xb5MZwKYBxvJbpV7/C6CT4ziOk4gb0C0KZ8VXORoW2f7qlUnAGsbj0YYDTkcqIDqO4zgl4EV0i8K346scnN7AaaRb/NtkArCK4biWMdBpaUN9HMdxnEQ0oU8Tu3F0rcMyFIl5T734t8l4YGWjsTWhL/i0mZEujuM4TkIWR79ADY+udThWB14n/aLfUd4GljUa4xNKXb5lpIfjZEtzagUcJwJLKa+fWJGi0wv4EeLkZrXQWrIkcBewhEFbLyuv9yMAp/S4AeA0Agspr9cuJjnwJeARxEO+f2JdumMEcBsSz69Bm7VR+8w4Tva4AeA0Atrt+/EmWqRhOSTz3oPAeoH6mGbc3qqIzpr3k/aelenIx3E6xQ0ApxHQfs19YqJFXEYgBX1eAvYlXJ37a4F1gA+N290e+Inieu09cwPAcRynBJyMziHs7Oga188o4CJgNuGd9h7ks+OEL6GPtOgos6g/R8AOyr4fqbNfxykMvgPgNAL9lNdPMdEiLGsDfwdeQHIWhK5oNxYpvDOz8u8PA19HUiZb0RdJT1zP7oV2B0D7zDhO9rgB4DQC2pf5VBMt7OkL7APcj4S9HUCcDHYfAdsBH3T47zcBxxj3tRGwdx3XaQ2AkCWLHcdxnEhoa8QfHl/lblkG+AXwPnHi89vLe0gege44ybjPp6l9F2BZZZ9v1Nif4ziOkyFaA+Cw+Cp/gf5IRcOb0Je7rVfGAStUqe+vjPveusp+2xip7G9sjf05juM4GVJUA6A/UjL3MmRLO8Wi3ybPU3uCnt8b9n9LjX27AeA4PdA7tQKO43yOIcA2yMK/IzAorTqAePvvSu3ZEH+I+F9YHKFsixx9vGnQluM4uAHgOKnphXjwbwV8DQmny+V32QqcAZyAHDvUc/0RwPzAaKUuTcDulLsss+NEJZcXjeM0CgOQBf8rSMW5TYDBSTXqnI+AbwL/VrbTCnwHSUy0qbItNwAcxxA3ABwnLCOAzZEv+w2A1cj/d/cgkj3wLaP2ZgMHAc+iC6/7MpKhrwyFmRzHcZwIpHACXB64EUmMk9J5rxb5EEkiFCo/yJkGOu5UZV/uBOg4PeCJgBzHnh2R2PWdKMZvbB5wAbAicHHl30PwB/SZAjeyUMRxnGK8nBynSGwE/BMYmFqRKrkXOZo4DPg4cF9vA/co2whV0dBxGg43ABzHjt5IPv6+qRWpgjsRp7wtgMcj9nur8vpRJlo4juMGgOMYsjfVZ8pLxS2IM93WSA2B2DyovH5pvFCP45jgBoDj2LFbagW6oBVxSFwfyTXwcEJdnkCiAuqlGRhmpIvjNDRuADiOHfXWrg/FVMS5bw0ks+CYtOoAsvi/r2xjQQtFHKfRyT0e2XGKRC5fpi8BfwQuRV8WNwQfIGl96yWH9MiOU3jcAHAcO1LuqM0D7gbOQbL3tSbUpSe0oYC+c+k4BrgB4DjF5gngKuBK4J3EujiOUyDcAHCc4jEWuAb4G7Ld7ziOUzNuADhOMXgdSTB0JfBUYl0cxykBbgA4Tp7MQGLm76xIzGQ9juM0AG4AOE4+PI8k6rkNSdIzK606juOUGTcAHCcfNgYmp1bCcZzGwMNpHMdxHKcBcQPAcRzHcRoQNwAcx3EcpwFxA8BxHMdxGhA3ABzHcRynAXEDwHEcx3EaEDcAHMdxHKcBcQPAcRzHcRoQNwAcx3EcpwFxA8Bx7GhVXt9kokX+aMepnWfHcXADwHEsmaG8foCJFvkzn/L6aSZaOE6D4waA49jxqfL6+U20yJ/Byus/MdHCcRocNwAcxw7twrSgiRb5s4Dyeq2h5TgObgA4jiXahWmkiRZ5MxS9AeA7AI5jgBsAjmPHJOX1K5pokTcrKa//FJhroYjjNDpuADiOHa8or1/VRIu8WUV5vXaOHcep4AaA49jxovL6TSh/KOBmyutfMNHCcRw3ABzHEK0BsBjlPwbYQnm9do4dx6ngBoDj2PEiME/ZxvYWimTKGsASyjZ8B8BxjHADwHHsmA68rGzjAAtFMmV/gzaeNGjDcRzcAHAca+5QXr82sJqFIpnRC9hX2cZLwFsGujiOgxsAjmON1gAAONKgjdzYA/32/20WijiOI7gB4Di23APMUrbxLWBpA11yoQk43qCd2w3acBynghsAjmPLNOAhZRt9sFkwc2E3YB1lG7OA+wx0cRynghsAjmPPFQZtHIr4AxSdAcAZBu38C68C6DimuAHgOPZchb4uQC/gjxT/N/pTbGoc/MWgDcdx2lH0l4vj5MhU4GqDdjYCfmzQTio2BH5k0M7bwF0G7TiO0w43ABwnDBcbtXMqsKVRWzEZghhBfQzauhhoMWjHcZx2uAHgOGF4tCJaegGXA8satBWLfsA/gWUM2pqBnTHlOE473ABwnHCcaNTOokgI3KJG7YWkGbgMfc7/Ns4H3jNqy3GcdrgB4DjhuAO70LXlECNgMaP2QtAH+Cuwl1F7nwK/NWrLcZwOuAHgOGH5qWFbqyM5BnKsGDgQuB4Ybdjm74GJhu05jtMONwAcJywPAjcatjcCMQJ2MmxTyyhknDsYtjkeOMuwPcdxOuAGgOOE53BgsmF7Q4EbkAQ7/Q3brYf9gTHAWsbtHgZMMW7TcRzHaTDOA1oVcpiBDt9S6tCVvAZ8zUC/WlkeuKUOfauRyw30G6nUYayBDo7jOE5icjAAINyC2QrcDHzZSM/uWBqZz5mBxjEBGG6gpxsAjuM4TjYGwJLAB0pdepK7gX2QHPxWNAGbAn9DivKE0n0esLORzm4AOI7jONkYAACbEHYRbZMpwKXAAcDideg5CHHqOxMYF0HfVuBndejZFW4AOE4P9E6tQIFYAFgEWAj5uhqMZGnrA8zf7u/NAqZX/nky8jL5GPgQCWmaEUlfJ0/uR5wCQ2e3G4yE5LWF5Y0DXq7IO4iBMAX56h5ckYWQEMM2ifl+uBr4VcT+HKfhcQPgM4YgL70VkLCm5SuyGPJi7GvUzzTEGHgP+cp4HXij8udLeNxzI3AJEtN/dMQ+R1Rk24h9VsuTwEGIsew4TiQa1QDog4QtbQhsUPlzBeSsMzTzVWQEnTttvYO8EJ8CnkBivj+IoFc1LIFkeVsVGIbscIwBbkIqtjnV80NkDvdPrUhiXkCiGKb39Bcdx3HqZXHgYKRIyRTinGlayQvAhcB+yG5EbIZW+m/pQr/ZSM72BRLoVg05+QC0pxnZDUj9fKV8rkOlNnYfAMdpcBYGjgEeR846U7/wLKQFqTJ3ErCO3VR1yVLI0UQ1uj1b+fu5kasBALLrdK5SvyLKk9iE+3WFGwCO04D0AnYF/oV8maZ+0YWW14DfEMYYWBZ5Edaiz/PAggF00ZCzAQBiBNyq1LFIMhnxuQmJGwCO0wNlSgXcDzgU8XK+HtgFOesvO8sBP0Z2OSyNgTWA/yK+CrWwCnAFcfwpykIr4vvRKEwDJqVWwnEanTIYAP0Rh6o3gAuQBbFRaW8MvIqEVa1ZYxtNwBHIMcMSdeqxPXL04jiO42RK0aMAdkEqho1MrUiGLA+cUJFXEOfHO5GogpldXLMGcDqwjUH/v0Z2EB4zaMtxnGLTjDh8jgAWRZyZhyEJp+bni7u105CcKR8DH1XkLSSfhReJMqKoBsAo4Gxgu9SKFIRRwE8qMgMp3XoXEmY4Bwnr2w3YHLtdob7AlcDawKdGbTqOkz+LIaHVa1RkdWTht8qlMgnZ4XwacTx+CglH9iRrNVJEA2A08Ecklt6pnQHAVhUJzXLAqcAPIvTlOE4aFkc+xrZAcpssG7i/IUj+lg3a/bfZyAfNg8DtyO5jVzudToUiGQALIGf8+6RWxKmJo4CrEJ8Cx3HKwerA3sCOiJ9RaqffvsBGFfkhkljqHuD/kIiwj9Opli9FcQJcC3gOX/yLSDNwDulfEI7j6FgCOBFJ4PQMUrxpLfL8bQ9EilldArwP/Af4OhIt5lQoggHwVeBepJSqU0w2QL4WHMcpFs3IQnoj8CZypLdyUo1qpy+SbvoqJNz2TMRJuuHJ3QAYDdxCvilmner5FXZOQM4XeRjJAxGaj4CbI/TjpKUf8v59Fvg3sBOSZK3oDEdClF9GapjE8IXKlpwNgAOBv9EYyXwageWAb6VWosRcghS0Wg7JXHgp8vKeq2z3TSSx1gmIZ/fCwCHKNp186Yvc3zeQZ2iVtOoEoxnxX7gDeADYMq06acjVCXAXpF56TmdLc4AJFZmMZG9rq6f+CZKjHyQx0YDKPy+ARCsMr8iwiPrmyHHIfW3p6S86ddOWEOuCyr8PQMJAl67IYkhxpz58trM2HZiFPNcTkMqObyP5I9x5qjHohRjoJ9F4x61fQcKibweOR8IKG4IcDYAtkLOaFLrNRQrfPI08BC8D71VkArLYa+iFfEGNrMiyyFnUmoilXfbdjuWAPYGrUyvSQMxAnuenUyviZMvmSEK1tRLrkZptkCOBy5GPlQlp1QlPbgbA0sB1yFd0DGYj2z+3AXcjW6azAvbXgnikvo9k5GtPX2A1xGFuE2BTymmJH4cbAI6TAwsBfwD2Ta1IRjQDBwA7I7sBf0Z2e53A9EEcmUJXIpuBFKvZGUlBmTPLAd9DnK6mk76Km5XEKGPcnlyrAfZGth9PQc7aNToeHEjHzlhCqes0pN7ECgF19GqA3bM/8CHp3wW5y33IEZoTmDMJeyOfAY4kfBnSUAzks+3zaaT/YWjkPOO56YmcDICRiJPVNcj5utWcFskAaC+vAxcCe2Eb7eMGQOcsiHwApX4HFElmAEeTl09aqdgcOV8PcfOeA/agXDdvIPLCvJZiGgMfE++YB9IaAAORc8XTkHzloea0qAZAe5mDHMkdD6yL7jfrBsAX2RKJg0/9+y+q3IA4czuG9EUyS1nfrA+QONacQx0tmA9JsnMN4Y2B+xHfhIkGbe0VYjK6ILYBsCqyiN2B5COP8XIqgwHQUSYgz/VoJHKhFtwA+Iwm5HmcS5z7VmZ5GwmHdYz4MfY36RrEwaXRaNsZuAaYit18PoD4TLR9kZ1q0ObfQ0xAF4Q2ABZG5v1C4F1lX/VKGQ2A9jIX2UE5DdlR6cmB2Q0AYRBSCjzFM1lWmQEcVMtNcDpnCWwXqpnAN2MOIGP6ABsDP0eKYtT6JfoacDqdhwYthH634UPiZRazNgD68/lt/VDHV7VI2Q2AjjIRMXQPqejTETcAZF6eJP296kymIeHVryC/oXuQjIO3IxX9nkL8QyaS787FaRT8aDl1GOBx2JX1nQjsjmxTO5+dpz6AfLEPQDzO10Fejovx2dzPQJIavYrkPngI2erqig+RcM3RCv2GI1tpHcMhc2U1JE54G+QYZED3fz06MY+6ciioMgzZddkLeRk/iYTz3oYsII3OGkgBnNShxFOBR4DnkXfLKxXp7v3Skb5IxMiKiEf+KMRHZDXSHvEej7xLD8RLD9eMxVdkm0ygeAUqis426O/bLyLpqt0BmKG8PoYcazZbPbNFwHFYyBTgTmUbY81mKz7rYeOnU4/M4fNHNSGNxUHksRN3b0UXpwZ+ic3kT0asQScuzeg9iu+MpKvWACiC/NFstnrm2IDjyEXGms1WXDZFUpPHnKsWZKfxENIuhEsjX+WvEv95+R+1O6o2LAOwiYFuAbaOrLvzGX9Ad/8mE2cLrxEMgEfNZqtnbgo4jlxkrNlsxWMz4oYFv4YsuKmPGTrShGRTvYi4CdQexXcCquLr2Ez4yZH1dj7Pzujv4UoR9GwEA6AFWMpqwrphKJIuO/V4Q8tYqwmLxIbE+/J/FvH/Se1DVg0LIevEJOLMzYPY+bWVln+jn+hnKMYDWGaGIAuP5j4eEEHPi5U6FkV+ajVh3RAibDdHGWs1YRFYnTgL3GNIpdYier4PAU4EPiL8PN1C+Qu71c3CiKOIZoJbgI1iK+50ijbM6PRAejUB2yPhRakXk1gyBYnuCMUwxOE29ThjyAzgZ9imJw7BYujrSPQkHyGpcMuQVG0IcDb6D5ee5OJYAyoa30U/uddF19rpinPR3curAuj0ZeIUlspRriPMF1oTUoci9fhiy2QkWiXHFLDzA08QbuwtwJ8op3PbRoSdu1bgJ9FGUyAsslKtHV1rpyuORHcvLfMALIQUOskhMU9KOQN7I+B3GYwrpUwCvkM+299NSC2QUON9CVg/2mjS0As4hnDpuluAHaONpgA0oz+Dient7PTMjujuZy0JQbpjL6T+Q+qFIhe5Dtmy17IAskuTejy5yH3EcVztieMJN8Zryf/ow5J1CBc6+Al5PC9ZsB76CT0qutZOd6yC7n7ORecw0xf9MURqmYf4UpwG3GzY7kTEaa+e7esFkXNfS6NqLHApMD7xfGtlBnFTL3dkM8Kkx50GfCviOHJiMOGOuJ4mbvXTbPkhuomcCywaXWunOwag33JfpM6+F0KOEFIvCPXIeKQg0v4dxm9hJHeU2UiK3BOAHRCjbRhSPGog4hi1EuI0eRwSpRMi++F3KmNsQo7xfoJkUZudwf2oR/6IGKAxGQK8ZaB7RxmHVLFsdL5PGAfBs2MOIlf+jm4S74uvslMF2qRO9cSvL0eajF/1ykwk8+GPkAJL3Z0ll9GB8R26Tgs7GNgNuABZiFLrWovcT1wnuSsCjOF54uSQKAq7YW8Az8P9AdRel6fGV9mpAm1K4GVr7G8FpJJY6pd/T/ICki3xa8iXdrVsl4Hu1vKDGsa/EvIlditxM7nVK48TxwiwSqDWXu5HdhWcz7MlElZrOdfvIUdrDUkv9D9mT/ubJ9ov8VqcZEYSZgvUQj5CStR+G8lLruG2DMZjJc9S/1b5AMQgOgt4MYOxdCVjCLuQDsPed+Im8qtqmRNrYe9Y/OeoI8iIFdFPXhnjUcvAWHT3dfUq+1mQvBaBtpLLJyKpWHtVOY5qWJVw4UkxZW5lbqwYARwKXE/8ojc9yf8It6D+zVjXe3DHtGpYD9vnbB7ixNlw7IBu4qzCxRx7tEcAa1XRR2/gDmU/FvIGcla9O+FDpbROsznI781n5TP6IC/T3yDHiznkf/h7gHF+yXhsT9PAW9F1sAW2xvjzNGAa+2+im7Sbo2vsVMtkdPd2mSr6+IWyj3rlU+BG4HuI70FMmsnD6KlXQn4Rd8aiwIGIo9yHhuOoVSxDlZuQ3CdWur2GR1LVw67Yhl4eFlf99GhriF8QX2WnCvqj/zH05CC3GWHinjuTFuQ891eVflMX9RiCfDGkWszqlbeAJQLMR7U0AxsAP0dCRWM9P61IWKNVrZLRhnpNQqJnnPrQrmHt5UMabBfmN+gmzCMA8mQpdPd1eg/tDwReV/bRk7wP/BX4BpJbIDeWAd4l3gKmlQmIz09ODAH2Bi4hzlw+hz5HQB9sn/3dlfo0Ok2I74nV/Tglrvpp+TO6yTo6vspOFWyK7r6+2UP7pynb70pmIelyd8DWeS8UyyHbt6EXLq28CawcaA4sWQt5tkJGlGjLMx9qqMsflLo4whDED8jinnxKnh8cQfgLusk6PL7KThV8G919HdNN28tjnyVuHnAlsKR+6NFZFJmvUAuWVv5H8ea1GYmvDxFdMgN5huuhL3bGyaPEz1hYZjZEPiAs7s2vI+uejAvRTdR346vsVMHp6O7rjd20fbmy7Y7yIrCJxaAT0g9JK5qDx3ubzAPOp+tMf0WgF+K8Nw3bubm8Tn2szv41RkitDKlILhUTQ/IzbO7PJGBQZN2TcD66iaolk5gTj/vQ3dffddHuKtjm5P4P5apwtj15pEJ+BQmTKgujkMJMVvMzl/oW4KeM+j+xjr6rpRnxm7mTz4fJTUQMn/UC9p2afkjJZIt71BBr29noJumX8VV2eqAXco6lua8HddG21mekvZxFMc75a6Uv4pmsLbFdj7wPHEH6KIkQDELSEFvN1UU19v9Vo35fJtyuzOJIGuHu+m8BzqCcvz2wu0/jKO8c/X9+iW6SGjaFYsasjf7h7yxL3HDscsD/hfJvSQ5EHMZihAs+hpSMLfJ2fzX0QVLlWszZLGqLvbcqS7tVHeOuhuHU9vV7BeX9DVodU34ttuKx+S66CbonvspOD/wE/Yuxs4XkCGW7bXIr5fxC7Y41gZORzHgWse+zkS+9E8kvtC808yGOjRbPYrVRTAtj42B2Xb2DroIr69DnhwH1Scli2PiNXB9b8dhoUwG/F19lpwfuRXdPu4oAeEjZbitSOKXRa0fMjyQz+iHig/NvJD79DaSE81Tk5fUx4nH+FPLV+yfECNu00kYjsyTiqKV9Hh+usj+L9M/zEEMwBKvWqdOniHFTRs5Cf89mA4vEVjwma6KfpKKFGOXAUkgVxb2QetSrIs47WoaiD9E7r5N2l8TGw30fgzE6DsAB2CzK1WThswjzvEE33G7RpOQ+IaBeKVkcibbQ3rcjYisek8HoX+whXuq9kTzPZyKe4tcgFt0OFLdgw1Bky/YVOp/Hj5HUyprc9od00XYtslsn7R5s0O4tinE5Tmfci/657OkYYHmDdm9EAwAAIABJREFUPlqRFMihuFeh11MB9UqNNsqtFfhvdK0j09WCVK1cbKzPHogHZlf9vYR8ORfJgWU01XuFzwF+S31JQu6tso+uZC6d58K2cIDatI7xOE53aDNetiLpprtD61PTCtxmMNau2MxAv3UC6peSZdDviLaQtn5GcK5AN0ETsAuXOJXqdyQeB7Yz6jcUC1N/nur7qS1GfgT6GP2uzkTfVLb7ZA3jcJxaeADds9mTY96DyvZbgV0sBtoJ/YBnDfSz/ojLCYs6Ad+JrnVELBxctjTQo970tfcBXzHo35rdEONIM6//Q7yeq8EiP//xnbQ73KDdQ6ocg+PUijY3/1+7aXsI+qiNiYRL+WtVk2M2MDKQjqnZDf38/DO61hHZCP0E1Ztas42hwBSlDg8A+yOlcFOyOPLAWPww2x6+no47+mNTa31UJ21vadDuMj3o7zj1MpTPZ7yrVY7spu2vK9ptk1AFfzbCtpzyVYH0TE1f9O/GKZQ4dLkX+gmagSx89aLxYu0oExHnwdjx0f2R3ZTJCt27kp6+oC2c9J7tou2DlO2+3oPujqPlKup7NufQfRSTtlZKK5KYy5pFCFMxsayJb85BPzcbxVI2hXPb35GwGg3nUF954AUQp7/OnM+0PA/cXJEHEIvZmv7I3J2IhPeF4FPEoHm/k/+3IFJQp5asZp3xY8T5sCMnAycp2v0bkqWuyPRC/DkWR5KMtP9zCPIMDEC+Euav/P3ByG95AcQoBNlqnVb556nIAvQxYrS2yUeVP98FxiLZF53uWRs5Lqs1Quhiuj/ffQZYvV6lgBeQEF9L+iJ5/kMU0HodcQj8JEDbKdkAqb6o4Vjkw7KU7IPeQqp3F+CnBn1XI5MRh5/jgW3RLZi9kKIa5yAv8Bj6d+Woc55B23Pp2tP1j8q2T+lyFvNjALAuYrCcCdwBvIPtVmut8j7iiPYPxEl2H2AlGiBPeY3UWgnuVcRI64oF0TvVhlgwLlDq1JP8i2JFWFVDM/pd7v+LrnVE5kesPu3Dc3aN/Q7C5uxa83K9FalpcBLiiPg1pJLauhVZH0nW8x1kMfsPYbb5e5K5wLId5m9dbBanW7u4PwCXKtv+Xjdtp2YlRL+rkSItKRf6WmUa8AiyIHy7MpaisBqyOD6D7IRMQXbrzkb3xf1Lqosiep6eE5htVUU7PckOirF0hjZ1e7VSz05u7lyLbk7eia9yXC5B/+DMQn7c1aItRtRocka7uZsPeYFatLtr17dI7dC4dzdtx2YJJCfDpcgPOvX9tJYJyP36PrCG0ZxZ0hdZ5LsztFqQs/d6CxttSddpqyciuyjVOAof242O1cgcut9hqJWd0ce0VytzEQfIMmFhPA2LrnVENsbm4XmU6rYnl8CmYEMjySRk4W+ifsenjjKO7u/Xf5TtW38F1crCwFHI13Lq+xdb3kGOjvagtpwSIRhIbeV8H6D6ENjOWBE4EDnyOwopE1tLhJB25+sBhe4d2RKbtLa1yGxk57MsrIB+TjaPrXRMmpCiJBYPzzFV9PcPo74aTQ4BjjNs77ge7tNdyva/2kP7IZgPCQm9GfkSS33PcpBZiDH3LeIXZBqAOK7VqvNNpPN1eLxKHbuSXxnp8WXkmCTFMzMd2N5oHDnwLrr5yPk404TR2Dw40+j+LG8bbIrLNKK8i91Z9STEi707tJnWNu6hfUsWB07Hxp+lzDIb+Ro/mPDbmsPQPUOnBdavK7TVBvc10GENqk8hHkrm0nmCsCJyO7q5KG0UQBt9kNAjiwdnLJ2/XOZDwk1SvwRdJPSvJ7S119evog8to4CL0CWEaVSZg7wYD0GyPlqyJuJtr9GvBYnaickCSp1b0cf/r4A4Kad+PtrkCmQnp8ho8wGUOhKgjcOxe2hu5otlbs81bN+lfnkPOZftCe0RQDXlVutlOaRSpDZcy0VkLhL6eAiwUA33oSO9kAx70430Go8+z0UtaMukt6DzXxgBvK3UIYQ8Tm1O3rlxGLrxN0RNkz7oKwS2l3Pbtb0zvvWfi+xHdVyk6GMmYVJoDkQiSGI7RjWSzEXO7Y9GXvrVxoZvBjwWQJ/b+eLHRCi2Veo6TtH3ouh3TULKTODnFHM3YHN0Y+8sEVspsSig0F5OReJuU8b8u3wm/6F69lT0c2MN/VTLXoRJg+rSvYxHtoG/zRfzUayE5MkYE1iHapyLLdhXqeftdfbbD4miSn2vq5FxSKhgLKPMgiXQjXk25UuS1CX3YvvA5Lil1YgyhdpSFvehfp+NrWvopyeGIwZF6vlzEZmEPBcxndSmEqew1JFKPestrKPNuplCnkbKHRdhYRyAfrypw2mjsSK+xRpCHgV2T9j/PtTO9tR+zm5ZXWxD7JxTXYotNxOeE5U6/rmOPjfB/nh0ErAdcT6+HkMSiuW+IzAL3TiXia9yOk4g/Q++vcxBklP8FHgjA31qkfFIZb22H8iLCXS4gPo5iuqNgPupzsGwJ5qRl3GRUvS6hJedCYs2Q+kZX2yyW3ojX9KWczQLSWcMUpAoVs2S1xC/kdRl2btCewy9QnyV09GHMA499crp7XRrRvIJXIOdt3EI+QD4EV/0CrYoUVmLPIn+R7kjcvbXVR+zkJdfX2U/IAbEDd305dK48iK1V/6rhd8p9ft5jf39WNlfR2nhizt9X0X/9VuLvIfUV1msxrkIzWvoxqWpVVFIlkfOjVP/6F+j66/K+RBntctJU6inK32PRQotdcZOEXWZgN3W1QDgG8hcP4rUI/g3kizEqo8hyC5C6nvokq98l3CcrdTtBzX0NQh90qGO8sMu+tqf+CGzs5FiW1uQx/HAE+jGs15oBUNatvXwGhI/eXlCHVqBQ+m6Nvo0pNTvdcjX56ZIONJmSC3oeguL1Mo0ZDG8CLgb0bsr7kWONEKEybVnFuJz8KZRezOAKysSgqWBW4BVArVfLy1IFsZxFXkX2VZtL9OQ+W57Ttv+eTCfpbRdEHGY6oMkyuooiyOG1Ehsi8mUjZORdOJTA7StdWibW8PfPRh5Jqw4ha4z1v0DeY4vJfx7p40+SEGwvZHaFJcj9Slei9R/R+Yor8/BiElC7C3r9lKPU00bA5D4z2ORB/8J7DLGzQGeBX6PeLzXamg8bKRHVzIPsfqLwtLkEeI3FrgeWWR2QxIOxXphtmc4kklxX+C3SHjZBNLPTy4SKixQ+647ssp+emGbFfX3Vfb7VdKny34e+X2NqlJnK7RhlhuEVjDXcIrewG1IZaqYvIRsu0wzbLM38lJfop0shnx9Ldju7wxCbnrHL72XkAf4BWSLq17ORzIvhuJo5GVWBIYh2/4rJ+j7DeCeitxN/gk/Fgc2Qna6NgbWIl3RnJS8g/yONb/BzjiH6hfxzjiKzydA64rtsYtq+AO1HT18CdmtjF0YqjMeR3S5GcklMS9gX4+iW8Q3RNKjNyTDkIUvlpU4E3m5lZVvE27uTo43DDUDCb8b0lGeQSIMVowwvtAMQjzj/0TjhUseZDB/HYm1A6DJstle/kR9H44rITuYqe9he5kAXIYcjYTwuM9+ByB3FideMZ+jIo0pFesRZt7OjzkIJc1I2dcYz9PHSCRJil2GmKyChPA+SfoXemh5Eftd0xgGQC8kQkg7/pvQnUsPRM7kU9/HruRdJKfID5Edr66cqqvFDQADlkNfW7knuZF8j0Os6I99vfrLKJajijbpSjXyAuJEqinQUlSWB36Cvr59CLHKIriF2WwJMQyAjZR9tCKhdlaOovsBnxroFFrmIjkTzkSe7VpxA8CI1YCJhLnJz9I4HtCWW3BXk8ZZrV42I2ySnzeBAymWQRSSZZFwzdS5PaYA30fCPS3qg1xmOUnEMQCOUfbRimyTW7I8EoGT8tmoReYAv6a2yDk3AAxZE7FCLW/qeKQcZqNwHzbzdhnFcgRbiHC7SJ8iUR+5ZiPLgZHAccgLMVaFzjnAX5BjxDaOM2h3OrahdDEMgGuVfYzHJuFWZ+xKsTKtXkf17z43AIwZAbyMzY38gMbLtPRf9PN2McX7yr2OMC+Du5HFzameZZAv0ocIkyhmBrLwL9dJ3wOx+Yg4zGQmhBgGgLbk7x/Uo+yeAYgj8VSlnrHk5CrH5QZAABZGXwq0ERd/0BsAF1I8X4ntsX8BzERCKos2F7kxFMl9cA7wHPXvDsxDjhqOQrb6u+P7dfbRXh5Ujrs9oQ2APuh9f7a1GGgVLAScRv7+ATORcO6ecAMgEPujm9iUmQZTok15+5X4Kqvojz4fd0cZD3w55iAaiEWQuu8XIC/Prhz3JiOhnBcC3wQWraGPBZE8H5pnYC6yWFkQ2gAYqWy/FQnJjskwpEhSDmnhu5JqajC4ARAINwDq4wF081a0he8kbH/0TyEZBJ14DEIMg2WRry6LVNuXoH8WRhvoAeENgHWU7b9tMsr6GIJst1vXL7CQe6vQP3sDoGhnuW1ot15bTbRoPIo0b8PoulBJPTyNpDV9y7BNp2c+RRK2vIE4cs4yaFNTqrqNHQ3aiMECyuvfMNGiPiYhBsAyiKHzUkJdOrJMagUsKKoBoKVIC5kljXRmfSzy9WjBM0i984+M2nPS8hiSq0DDtoTzjLdEG51imRa9Xj4BzkOSam2CRDXUUgQpBNokQVlQVAOgkRYySxpl52Q4cIRRW28hxZcmGrXn5IG2wuRgJFe7E5cHkGp/SwM/Rmo0OHXSqAZAURYypz6+j42FPgvYE4kaccrF/xm04U5a6XgfqVo5AtkV+DOyU+DUQFENAC2NagA0guHUByl8ZMGRyHaxUz7GIpkxNaxvoYijogXZFTgUcRbdGUlUNj2lUkWhqAZAIyxkIWiEedsVeRFouQWpoOaUl7uU1/sOQF7MRAoWjUYiRg5CdnqmpFQqZxrVAHDKyyEGbUwHvmfQjpM3WgNgJJKYzMmPycBfgT2QiKD1EJ+BB5HEUQ7FNQC0FOFLNgRl3wFYCgnV0/JzZIvYKTcPon+m17VQxAlKCxL18VtgY2R34PCkGmVCUQ2Asi9koSj7vO2BfozvICFHTvmZBLyubKOeMrFOWsYjoYQNjxsATpnY1aCN32GTbMYpBtp8AEuZaOE4CSiqAeDUR5kNp4WR7T0N45Fqh07j8ILyek8N7RSWRjUAGtWJsMzj3orq63R3xUVIOVmncdCmunUDwCksRTUApiqvt0oRWzS0ecG18x6SzQza+IdBG06xeFV5vRsATmEpqgGgzfg01ESL4qEtYTrZRIswaA2AR4BXLBRxCsX7yusXBXpbKOI4sSmqAaBN7LCYiRbFoh+Sv1xDrgk1FgFGKdu4ykIRp3BoCzz1oiSFYZzGo1ENgFE03o92DXQ+ADMrkiPasQHcYaGIUzimoY/6aLR3iVMSimoAvIkum1MvYB0jXYqC1kP+bRMtwrCK8vr3gRctFHEKida3xQ0Ap5AU1QCYit571yJjXJHQGgBPm2gRhtWU199N3iGOTli0qWFzfo+2KK/XRtbkinZc2nnNgpwf3J7QVvL6uokWxWAwsJ2yjZwNgFWV1//PRAunqJQ5N/w05fVl3d3Q+kPlHBFVNY1sAKwIrGmhSAHYBxiobEM73yFZWXn9cyZaOE5+eMh052jH9amJFokpsgHwsEEbRxq0UQS+rby+lXy/khcBFlS24QZAY6NdDHJOHa01ABY10SI/tOPyHYDE3IPeChtN+RN5bAesr2xjDPp46VAMV17/IfCBhSJOIemDfndMm5ckJNrcHQtRzrwpKyqvzzknStUU2QCYhb6edx/gGANdcqUJONWgnZsM2gjFEOX175po4RQVbXZMyNsA+Ah92LR2scyRlZTXa6tIZkGRDQCAfxu0cTj6MLJc2RP91z/kbQBov04+NNHCKSrapGDTyfsIAPTpjr9sokVefEV5fSmyhhbdALgJmK1sow9wPuUrlDMUOMegndfJOwJgmPJ63/5vbEYor3/PQonAaA2ALUy0yIeF0X/0aec0C4puAHwAXGfQzubAtwzayYmzsHHguYC8Y+S1DoC5pjd24jBCeX0RDICXlNdvBgywUCQTtkP/wfeyhSKpKboBAHCeUTvnoA8ny4V9EAdHLdOBvxi0ExIvxOJoGKm8vgg+JA8pr58f2NVCkUzYX3n9O8BbFoqkpgwGwMOIl7qW+YBr0XsEp2Z14GKjtq4APjZqKxTaI6CyHf04tbG28voibAU/hP53YvFBkQNLAFsq27jXQI8sKIMBADZn3SAZ5S6luPMyDPg/xJjRMg8416Cd0GgLFJU11anTM03AWso2iuAMNh14XNnGtuhTbufAUeh/8/dZKJIDRV3oOnI58KRRW3tid6wQk4HAjcDyRu39A3jGqK2QaL9stD4ETnFZDv39156vx+Ju5fVNwPEWiiRkKHCYQTv3GLSRBWUxAOYBJxi2dxjFetj7IYu/VbjOTOBEo7ZCow3BKmumM6dntCGyLRTHALjWoI19kCPGovIT9Fkfn6AkOQCgPAYAwK3Y1nQ/rSK5MxD4F7bVDf9AcZxctF78bgA0LtrfzIvoi+3E4mn0Ka97A3+imH4zqwBHG7RzhUEbTiDWAuYgYWtW8puoI6iNIcCD2I73PWyyo8ViNXTjnY77ATQq49A9O3810OEcpQ611DP5qbKvNjm0zrGmohdwP/pxtwBL1tDvo8r+NqhvuI3NydguiG0/9H4Rx1ANyyEV+qzHukPMQRgwCP2Yy5jq1OmeUeifm8MN9IhpAIwA5ir7a0WM5iI5BP4Cm3fjnTX26wZAAnojleusF8aH0acNtWIzJAmS9Rj/HHMQhkxEN+4946vsJOYo9L8Xi/PwmAYAwNXK/trkRYrhQLs98uVuMebtauzbDYBErArMwH6BfAfbs/Za6QX8HBsrvqOMpbi1vx9HN/Zfx1fZScwD6J6ZCdichcc2ANZEnKYt3hkPYxNyHIr1kYqxFmN9mtrvtxsACbGw8DuTFuAM4h8JLIv9eX+bzEJfHCMll6Mb/6PxVXbasQKwFxJ9cySwN3IsE8rZbGn0i+CVRrrENgBAtrKt3h03Af3r0CE0a2K7S7pvHTq4AZCYvxBmwWwFnkdqCISmD3AsdpZsZ3JwhHGE5Gh0459L/O3MZmAd4BAk5PSQyr+XKTKnOwYj436Fru/LWCQcdX7jvo/tps/Yv5kUBsAm2O0CtCKJcXI6DtgMmIztu76elONuACSmLzben13JPCRhTi2eobWwJZKMJ5T+rUjIX9HZCP087BVJ1yZk8Xi5Cz3GAQdR7hoHuyLRJtXem/HA1w37f6KGvjuTFuzCR1MYACDhbJbvkefJo6z6odgf/25dpy5uAGTAwujDfXqSGcDZ2L0U1gduD6xzK3Ab5Vho+iHHGJq5+GcEPQciqZqrfaF+LYJOMVkASbVdz/2Zh4TkandINqyz//bygFKH9qQyAJYEpir77ihTEeM1RZ6AIcixjPU78nqFTm4AZMKqhPGa7yjTgUuAdevQsRewO5JmMrSercAjyDZsWdD+2GYQdj6aESOjVr3uBL4UUK9YbIGNIf57pR71GiDt5VilDu1JZQCAZMYL8W65h3i7AU3AgYhTpvU4piO+V/XiBkBGrIE+XKwWeRJJvLEaXVvEA5Ft/vORbc5Yuo0hrzM7CyxifQ8JqN/BSt1uBzYNqF8o5kd2x6xCsVqBH9Spy3D028PzkBwcVqQ0AHojlQJDvGNmIx9DKyj0644m5ChpTCD9W9HXDXADIDPWBj4i3APTlUxC0hRfClyIfAmOQX4ksXV5EimKUTbWQz83zwbSrQ/i0GZx/8YgpVlzS0zVGTsAb2L/DM9G7net/Nigb8vtf0hrAACMxNZhrqPMRbbRd0N8srQsjuzAPB9Q51YkvboWNwAyZF3CetTnLO8jX0FlpAl4G/0caWuFd8Y+Bnp1lAnIdvgaAfTVsix2CWe6kpeoLfxsQWx2AL9T00z0TGoDAOAbSh2qlY+RokSHIc9tNUbscOQ3eSoSBh0iB0pHeQcpra7FDYBMCe1Zn6toa4Lnzh/Rz9Fdxjo1IbsuIe/rU8DPSJ+edVGklLbWIbNaqaVi5+8M+puOfZ2MHAwAgLOUetQjc5HKevcDNwPXIAbCHcBjxD2ybZNpiKOoBW4AZEqIHPpFkLIbAFtgM0+bG+q0m5FO1cqriE/JbohndAw2QNJIW3uV9yRTkCifnlgJm9Cwy2qdmCrIxQBoRhbgmPcvN2lBHLGtcAMgU54j/cOWQsZYTF7GNNF1fH0t8iA2oUwxvv57eqE9hxSzOgzYGJutzT5IZMLxSIrUlM90TyW7LWuDbFTjPFVDLgYAyBn9XUp9iiyWcwkFMACKWNfZgueQ0MBGYwySY6DMHAucbtDOAUiSJw3fIM/64ROB15DIk3fa/fkBUk67jU8RL/4lkLjxxZDwrg3JJwf8J0hq3yld/P+TkAqhWh4jzAv5HHQLz9vIfbNiEFIpsdGYgxwNW7ISut/Jhojx6hgT2oM0V3nMYvIyZyFgJvq5eg9dXoD5kUU19T1vBPlhF/dgM+TFbtHH6C760KLdAXAprwTfAWiUvOMdadSdj9bUCkTgQ8SRSMtiiENbvfwU+XJ2wvMdvvibXgo507bIdPkOEtXgOKWiUQ2ARqURDACQlLHzDNo5gPpy0I8CjjHo36mOFRH/hjb6I7k2qnEQrIZTkMgGxykVjWoA+A5AuXkBu9z+FwDL1HjNWdgkPXGqZ//Kn03ARdj5urwC/M2oLcfJCjcAnLLyS2wMngWRBaDa38rXKV8RnyKwG7LdfxqfGQMW/BSJV3ec0uEGQGPRKDsAIB69Fr4AIHkBqoksWASd34BTPwsh4Y4/MmzzZuA6w/YcJysa1QDQ8nqCPmcB9ybot8j8CEkAY8Ex9Fwc5ALKm2o5NE8ZtGH55f8J8F3D9hwnOxrVANDuAGyPFCO5jM/HTYdgAvBbpALZCcq2GmkHAKQQjUVOgDbOQe59ZxyEVCdzauMtYEek0uHMxLq053gkxj407lzodEVOv4dS8Qq6+Mz2JS4XB76HlGu1yoH+LvAnYDsk61obX1K2+2C9E1ZgBmJbke4TvhifuzJ2aXDHIxUjy16wai7iLDl/u3m8IQO9WoFbiXdM+INIY3Ipnlhk7XQ64VV0N2b5LtpdANgD+WK/g+pKD89FEhNdBnwfWVy6evl8Wal3IxoAIF/tlj/MyXxWMKQ/sn1t1fZ+lXYHI4ZlGetW3ErnVQwPyEC3dxB/glisH2gcLsWW53GCoTUAlquhr8WBtRHP8AORc+TdkbjlUdRW0lRrAFjXMi8Sl2D7A52C7MhcaNjmHV3ovgliIH5iPIbY8gSwVRdjBIm4sMrcV4/Mqcx1TJqAFw10z1GuQ2pFzAvQ9lTEkHwig3GGEO1xr9MNr6O7OcvGVxmAr9SgY2dyf3yVs2EB5LzZ8kdqkXK4TWbw+aOlzugP7IIYA5ONxxJSHgD2pDqfowcS6mkZQVALu9SgY5GkrXjSwsjO6C+BfwPjqM3Qm4bssv0dccbdlM/ybJyfwTit5S0i1dqwSJPZiLQm6ld7LplK7xyYguzA3AH0Mmqzn1E7INkLX+3h78xEzslvqPS9NbAzEqbYk/EQm9lIKt6zqa0K5e2IoRuby7F1GK2FG4Az6bqmQdH5AEnM1T45Vy9gUaTI1CBgAJ/thk5BjkY/QPyhJkXTND0zEGNpWmpFysaKyBn7bei3GUdG1r2NjWvQsTOZBPwe2YZt1Ex1J5Lewu8oL1PbUVBnLArsxWcLboht155kBmJgHY3kRKiHjRLoPQZxFk1JE/AzZOFL/TxaSYjyyR0p0w7A20QoANQoDEAWutOQ1LCWN2pEvGF8jk2q1K8amcZnL+slYw4iMc2IEZj6x94mcwlz7jwU2Rk4AvFTeBh7H4LJwN3AGchXS3uP/nrphXwBxpr/txDjKRdWRXYjinTE05W4AVCdvIwYfxa/n5ooW0a8ZZFFfyvE8zvUhI5AQstisylwX6C2XwBuAu5EEg6VOf3pcOBR0vlytOdXyI8/FosgZ7JLdfhzEeRIcFCHv98bmIjko/iwIu8h0QlvIC8wa25HjjdCMxEpGfxChL5qpQ9yb4YYtTcEmdPtgdWN2uyJLwGPBO7jfODwwH2A+CDcjHw0fWrUZgvwPvLbcuog5Fd+d7J0jMF1wmY16KiRicj57WjsXkC5sRJyJJLS8n+Mz+d5cIRTCD/3U5BkXmVmVSSh0R2IT0bs57uMOwBzEUfV44F1I4zP6cAKwFHALciZY4oXd9kNgPYyB9l1OJ54Xw6x2Jo0L8ZWZDu+lnDSRsI6b0NHmY4cj5SN+YCdkCOft0nzXLeXMhoAHeUNZL53Qu/H43TCAOSFcC76+H0r2SzoiLtmyxp0DCVvIlkKdyS945QF+yNbcbHncXSMwRWU4YSb99nIs1sW2n/lW2UitZJGMADay3Q+86taKuSgy87ywJHIV/500t/YjpKq4tv3atAxhsxA7tH3SBcZYcHhxJ23a+IMq9C8j/28twDfiDmIAOT2ld+dNJoB0FFeR6JytsKP+rqlP5+d5T9P+hvXk3yCZC2LzfV16pvigS9amOGPiTNHT/NFRzvni9yO7bzPo5jV/ZqAtYCfAP8lbabEWmWLAPPRkYsSjq8WmYhEd+yL5/gH5PzzCMSzMsev/J7kePsp6ZaB2BWciSGTgWuBb1J/THhsfkjYOXmfdP4jReMs7OZ9HrKjWBQWQDInXoIkwkn9W65X9rWemE7IpYBULTIXqctyAmLcNQTtv/LHkP4maOUTYDHTGeqewwKNI5Y8j9z7jcm7DPWRhPEJmIYUfnGq4/vYzPtcxAjNnWWRs+Mcz/LrlTNMZ6hz2kJRiywTkDTHeyFFwErDIMQKvB55AaaeaGu53G6quqU3kiwi9XitZDzwVySNrWU6XSt2xfZ5nUb3RXCcL3I0+nmfi1QYzJFmJK/HuUgFwtS/yRDyrNlsdc4ypMl4GVJmIonKjiCYKE7YAAAf+klEQVSvBFU1sQ7ygk8VphdTDjGas+74UcLxhZZJyLPSVl43FzZEcpFrxzeVOGehZUNrAMxCqm7mxkLI1m/uDnxWEjLXwk8zGF9ImYtk2hxNnh9KX6AtU13qiYsps5Bt7VCsSDF9JOqRh5Gzz1wyVI5Cnz7Xv/zrQ2sA/DG+yt2yOKJTI3wUtZc7LSavE4ZiY6AXRd4HTiKN83mPrIKEg6WepFQyFfiaeha/yNJI6czU44stY4iTCrYaxqEbizv91YfWADg7vsqdMh/i+1LGI9Bq5dvqWfwif8lgXCnkI+A4JD9OcvoBJ1MepxWNzME2zGgk+SQ+SiX/JK6jZWeMQzcGNwDqowwGwHbAWNL/jlLLXGA/5Vy255cZjCm1vEHij6SVgGdIPxHaB9PaMr8ZWFkxr03ImU/qPPW5yCTSOnKN60SnWsQNgPoosgHQH0nUk/q3o5XXgH8btTUH8X3orZjXwdh9+U+nGDlnupN5wMXILlNU9kMqIqWegHqkzQN9b6TQzX4B+pgLXIWc/1b7wA9E0tJah0h+hFiKv0GS0KSe/3rlYtJse42rQ9f24gZAfRTVAFgBqRyX+vdSj8wAbkXmflRlPP2QMDWrPl4FDqW2s+wlkERIlmf+l1baHolkMi1qPppWxJCp66OzVmerJmTL/+f1dJaIFqT0683Iw/0EMmltNCEZtkI58k2ptP88kilvSkUWQAyQ5YG1K/2HKCbxE+QMso2lEH+FHZDaAtGtRwVPInq/H7HPcUi4Ub0sg9Scd2rjaOAPiuvPqbQRky8DN1KsTG9vIP5btwD3IItgR36NvEcsmYNUw3wcMQrGIyFwzch7cAnEmPoSUoTMOnfIZsh7uT0DkXfi1yqi+d3HZioScn9TqA56IZmpUls71ch44G/A1xFv0Z5YhzQFYULLBLpf4PsD2yIvy9cz0LcaGYtERsRinFJf3wGoj6LtAOxCMb4gZyBx5t+n+t/RCGRXM7XuVvI81X38roZkfL2PYqRgnkMYh0uakW3z1APsSuYCDwE/Q2o012Mt/iaDcVhLrU6JKyHpcO8iXZncauQDJPIkBuOUuroBUB9FMgB2JO/fyxtI0RxNBc8y+DS0yZ51jH8I8kH5d/IPPzTf+cqx4tIE5BxnH6r7yu+J3ogRkXpcVnI3unj6wcAeyK5PiMpsWnkXqScRmnFKPd0AqI+iGABfJb/Y/plIMaUfIEa9BQtRDsfkMejzjDQjicJORY4wcstGOA/DnYAfZDCgVuQr/2HgRCS7VIh88ssAH2cwVq18im153iZkZ+XniD9FLsclbyC140MyTqmjGwD1UQQDYEXyWRTHIomGdiKcX49FeuaUMhf4ivmsSKjywUjYsjZxmJW0IMdSKrYh7dnPB8iWyzeI51izLcXPa3Cw+ax8noWRUMWrSf8CvBtdaFFPjFPq5wZAfeRuACwIvKTUUSMzkcJBx6ALO66F3sAjAccUWn5nPyVfoC+yK3QmaZ+PVsQYqfuodFHgw8gKtyAP2M+RymmpqsbtRXGdXn4bYD66ozfiUftb4Dml7vVKyKpj45S6uQFQH7kbAFcr9atHxgF/QopopYreGUkxd0mfJE0+/eWAoxDHy5k16GslrwDz16p0E3YJIHqSicA1SFGd1Fnf2nMg+Z3t9CTXkL7U7jLIvbyGeNthLUj4TgjGKXVzA6A+cjYADlDqVq3MAR5APNHXJZ8aGZuSZjGrV94jj9/hACQ3zNlIaHCs8V9Yq6LfCqzQa8ApwAakX7C641CKsxNwB2HyCGgYgMTTng+8SdjxjyNMLe1xSr1yePEUkVwNgEUIe+z1CZLtbhfq+HKLyNcpRmjcp0iYd46sieRXeICwflXzgO2rVWoBJI7eWom5yHn+puRjyVbDTuTj2NGV/JP8y0U2I2djlxPOazrEGd84pU5uANRHrgZAqFwojyG7jkVKzLUXeftLfYwkZyoCI5GP4lA7A69R5RpxZoDO70WsnaKyIvAs6R/ojjIP+BV576J0xiJIXgnrI5ZZSPYwS8YpdXIDoD5yNADWw/5L7X3gmxTro6g9m5BnXPzLwKoBxx2KXsBhyNG49Zz8uKfOF8X262wGcpxQBvojjm65HAm8h6TFLTIbYl9Q6mpjHccp9XEDoD5yNAD+o9Spo1wODAqgZ2yWRJKHpX4ntsk1yE52kRkKXITtvEyhh5w5Zxh29i5yxl821kFyZqd6uOcCF2CT/CgH5geux25+WrBNFTxOqY8bAPWRmwGwDnY7VnOBHxnrl5pmwn25VitvYxD7nhnfwfaYpcs6PoOxq/D3BlLMoczsANxPvIe7BbgOKYxRNpqR83urufqLoW7aGgkx6xaUiePQzbt1aOgVSn3a/473MtYtJ4YixcemEO/dOAFJYV5vmuPc2RSYjM1cTaQLP5PvGHbQSC+9DZEwi1CewROAs2iMOb0AmzmbTm3lRrtDWzM8ROaxRuAkdPP+K0NdhmIX9nakoV45syCSRTZUCfJ5SDW/b1Esx8l6+Sp2OwGdHstbZHiaQ+O+8Noq652FPPT1hsjMqVx/BrA10CfmIBLTG7v8E4cZ6TRGqcfORno0Guehm/efGupypFKXNtGUNy4yqyE7Oneii6j6CNkFPQzbVOdFYTQ2x1D3tzXY5nm6DHLWqeU07OtGF5UBwBrAKOQceHHEKu6HOKhMQRb7jxFP4LcQz9VnEOfJRmVB4AX0SaEeQWqJa7mZGmJoO+EgJOLBqY0b0BlPhyBOVBY8gP7D5mVgLWQnoZFpRrLjrQ4shbwbhyC+QAMQ/4hpSH37Sci5/isVeSuBvrlxCfJO0dAKLI8c1QNwBHqr4hXkBjqOlr3RP48tSLihlr8o9QiZprjMaBNH7WSkx0LoI3/mES5TpdNYDEWOhbXvx6PaN3qLQYNl87500nIr+mfymwZ6nKzU4UEDHRqNxdHfe6u8I6MNdLnKSBfHAZtn8ra2xprRexi+RvGS0Th5szn6h/wyAz32Veowk/yzNObGnujmvAU7j/ALlbq0YnMU5Tht9EafMXAG0KcZWAl90oRzkW0ux7HiXsQfQsP6Bnq8pLy+H1LIxakebfrWN5FIEAs2VF7/OPCwhSKOU2EuUhVSQ38qIeXaylbzkHMyx7HmcPTPpta47YMsJho9fq/UoZFoAsaim2+rbJD90Re8aZSwPycuw9H7pny3GX3u9GeBD5VtOE5n3KG8vglYWdnGHOApZRv7Idt2Ts9sAYxQtvGYgR4gemjv290GejhORyYCTyrbWLkZfTylP+BOKF5FUkprGGGgx33K6xcGtjHQoxEYbdDGPQZtgP7d+AES0uo4IbhXef2IZiQWU8MTyusdpzseUF4/wkCHGw3aONigjbIzBNhD2cY72L2TLN6NrRaKOE4naN+NI5vRV6OaoLzecbrjbeX1wwx0eBQYr2xjN4pdEjsGxyAJYTTciN2iO1h5vfaZcZzuUL8bm9H/4D5QXu843aH1L7HIEz4PSVGsoQk40UCXsjKMDslJ6uQmgzba0D47/m50QqJ+NzYjnq4aJimvd5zuyMEAAJtjgN3xXYCuOAb9F/en2J3/gz6zqb8bnZBoDcz5mtEn8GlRXu843TFbeX0vEy0kImGiso0mpE59U09/scFYHvi+QTtXIxXTrPB3o5Mz6nejZ+9znOqYCfzZoJ3NgG8btFMWmpCkJhaZ+841aMNxGoZm9F8j7uXqhCSn5/N8JC+AltOBJQzaKQPfBrYyaOde9JkjO5LTs+c45vgOgJM7Ob2E3wP+adDOAshXb6MfBYwAfmfU1nlG7bQnp2fPccxxA8DJndxewucYtbMT8COjtopIf8SYWtCgrbeAGwza6Uhuz57jtEf9fFocAThOI/EwcJdRW79CUt82IucB6xi1dQqSF90afzc6pcZiB8CtXCckOX6FHYtN9ctewJXA0gZtFYlDsMuM+DTwN6O2rPF3o5M1fgTg5E6OBsBT2C06iwB3IvUCGoGdEWdKK44jXCnyHJ89x2nD5AjAcXIm15fwCUjiGQtWQDINarNy5s7mSKy+VWXE/6CvGNkduT57jmOChwE6uZPrOewE4AzD9tZHnOK0mTlzZT3EUc9qfLMJ70SZ67PnOCb4DoBTdkIaqL9FzqCt2Aa4FX1K3NzYBDnmsBzXz8m/1K5/HDkh8SMAp/TkvEM1C9gPyRJoxWZIlMFwwzZTsj1wG5L7wIqHsN196Yqcnz3HUeNHAE7u5P58Pg/8zLjN9ZCiNssYtxub0cC/0BfVac/USrsx8uzn/uw5jgrfAXBypwgv4bOAu43bXA14nGLmCegFnAZcCvQ1bvsY4HXjNrvCfQCcUuMGgOPomQd8E321wI4MQ7bPDzVuNyRDgVuA4wO0fTVwcYB2Q+E7AE5IssgE6A+5E5KiPJ9vA7thW44WoA9wAXANMMS4bWu+BDwGbB2g7ceBg4j7vinKs+c4deE7AE7uFOkl/ACyExCiz72QBESbBmhbS2/gZOB+YNkA7b8H7AJMD9B2dxTp2XOcmnEDwMmdor2ErwJ+HajtpRFfg9PJJ2nQBsD/gJOQs39rpgE7Au8GaLsnivbsOY2FhwE6ToacCFwbqO1eSC2CF4DdA/VRDUORksYPA2sH6qMF2B94MlD7jtPQuA+AkztFfD5bgQMRB75QLIVkDrwVu6p61dAPOAp4Cfgu4XYRW4ADkDDCVBTx2XOcqvEdACd3ivoSngHsiizQIdkWGIPsOKwcsJ/eSAW/V4CzgYUC9tWCGFBXBuyjGor67DmNgR8BOKWnyC/hmYjz2o2B+2kC9gSeQ4rj7IRdDPvCSEjfa0gIXujSxS3At4DLA/dTDUV+9hynR/wIwHHCMhvYG6n2F5pmYCvE4HgRyVC4Uh3tDED8C64E3kKS+sTISjgPWfwvi9CX4zQ8VmU5HScUZTBQZwF7AC8DIyL1uSLwi4o8j0QPPFqRd/h8/YKFgFWAjSqyNTBfJD3b8yl5Lf5lePac8qJ+Pt0AcHKnLC/h2cCURH2vWpEj2/23qUhc/TDChO+VgbI8e47TKb3xh9zJG38+wzA/+eQSyBV/9pxS406AjuM4jtOAuAHg5I5/hTmp8GfPyRkPA3RKj7+EnVT4s+eUGg8DdHLHn08nFf7sOaXGdwCc3LFKaOM4jlMm/AjAcXrAv8KcevEdAKfU+BGAkzv+fDqp8GfPKTW+A+Dkjr+EnVT4s+fkjB8BOKXHX8Kf8TCSLz9H3gJ+nloJx3Gqx48AHKc4fBcYBZyDpPHNgeeAQxG9zk2sizX+bnRKje8AOLnjL+HP8zpwNFJU6GTggwQ6tCLFhXYA1gD+jBQ8Khv+7Dmlxg0AxykmHwKnAEsC2wN/AyYH7vPVSp/LAV8FbsYXOccpLBbFgBwnJJ8or59kokW+zAFurch3gW2APZEFegll27OB/wG3A9cj2/2NhLZ648cmWjhO55iUA3YL3smZsYmvLxKzgJsqArA8sBGwJrJVvwywNDCgk2vHI458rwJPAU8Aj5CPr0EKtM/OOAslHCckHyNGQL0yJL7KTgMxAJhGfc/mHGBofJW75Cl0v7U1jPSYD5mXxZHfr9VR4ILoxhf6CKNWVqP+sTSS4emkYRC639snHgXg5M4MxMmsHv6Bb8N2xjRkXt5DjkhyDS1MzXPAXXVee46lIo4TiknorIgF46vsNBjDke3pWp7LD9CfgVuTyw5AKMq2AwAy57XuQD0F9EuhrNNQmOwAOE7uTAR2rfxZDZ8AuwPvBtPIaRSeAQ6g+jDHccAuNfx9x0nKZHRWxALxVXYalGWB++j+eXwEWDmVgj3gOwDF2wFo48vA83Sv/z+R3SrHicFgdL+3Kb3j6+w4dfMGsBmwJbAXsBawMLIz8Azwf0g4XGsqBZ3S8hASTbELshu1EmLwTECMzquBx5Jp5zh1MgWdFTE4vsqOUygGAjsiTne+A9C1zAQOBhaLrbjjFBDfAXCcTFkW2Koi2wPzp1WnEPQDLq788wtIPoM7kWOfOamUcpxMMYng+wSdFTFIqYTjlIHewMbAacAYdL+pRt0B6Eo+Aq4BDkFyFziOI/53mt/VZHADwHHqZRFgNLI4aY/S3ACoTloQA+s0xODySCanUXEDwHEi0gtYF6nCNwZJoBN6wXMDoHv5EDHARuNZSZ3GQvt7mwRuADhOdywGHARciz5kViubBB6rlhQGQHuZg/gL/Jj8jSXH0WJiAHyqbMSdm5wy0Yx85R8PPED8r/zu5GcBx23B2qSfo/YyAfg7EjLq+UqcsuEGgOMYMBzYD7gCySmQeuHqSnIvx3sE6eeoK5kF3AEcg8TwO07RGYLuN/ExuAHgNB5NwHrAicDDiGNZ6gWqWtkswHxYcT3p56daeR04DwnR7Kw8suPkjokBMFXZyHyhR+k4BswH7ARcCLxD+gWoXrnRemKMGARMJ/381CMzkN2B48k3jbTjdMQNAMfphjWQl3pbIpnUC42FtCA+CrlxIOnnxkpeBM5Ekjj1tZwkxzFkKLrn/CNwA8ApDwORl/bZwJukX0hCyUPos4BZ8yTp5yWETEN2B44GljabLcfRY2IA1FrruqMMDD1Kx+mGFYEfIC/pmaRfMGLJaIvJM2Jb0s9HLHkK+A0Skump1J2UuAHgNCQbAKcjjlypF4RUMglYQTuRBvQCnib9fKSQj4F/ADsjdQwcJyZuADgNw6JIBr43SP/iz0WeJX0UTs6hfzFlMnAJUqLacWIwDN0zOxHcAHDyZk0kmcss0r/kc5Rrka/wFKxBcT3/Q8p9wC7k56fhlAsTA0D7A/YYWicEywGXU6wY/Z5kLpJd8ATgVsN2LyO+EbAw8IqB7q3Av4F/oXdIzk0eBbasd4IdpwfcAHBKx0DgDGA26V/gFvIBsoOxD3Jm18aKxmO8BUkNGoOh2J37zwKWqLTbD9gaOAt42aj9HORmYGTt0+w43TIc3XP5IbgB4OTD1hT/jL8F+B/ir7DB/2vv3mL1qKoAjv/PKS03laut5SIgAqIhAa/EognegmC8ReODRjCoUQxB4gPRB0NiEGO8QtQIRoUHFBVUVGxUiAFRbgGJ2pgIchGEqhEovSEp9WG3Usvp6dlnr5k1853/L5kXkjndM6y9vzVr79nD7J+r/Wrwv/0XYMXst7jZMcQ9+W+mzJvvyOHAmZTkZkPgv5lxrKW8rZI1XaPJE5IAtHas3bq+Sk28JcAFDOvDOzXHv4HLKZvhLK247mW0b8W9/bGJklgsr2jHXCym7KMfWabfxNx33tsDOAX4CuNOEq/jqYqH1MIEQKN3KOWJOXtgrj2i3gf/aEftWwdcSPtncfcETgf+3EEbv9PQrqOBjwHXML4Foqsp1S6pxbNpi8N/gAmA8qxg2F/f2/ZYA1wJfIDYJ7hpyo9Yl22/g7JvwhuBg3fSnsWU9QnvoyzCfKSjNj0KHFB3q3bomcDbgYsZz3ceNlGmN6T5CkkAWndPcwMMzcdbGP4rZKsoCxJfS7d7wh9M2dinr+taQ9nv/hbKDorXArdSNlbq65sJZ4XcuaeboryL/3HgesqbF9lxNNvxGXxdUPNjAqBRei/DHJjXAz8DzqD/Vdvvbmz7mI7b6G8x3D7Au4BLKKX37Guf6fgGJgGqZwKg0XkHw/rxv5MyVz6E78J/jfz70fWxATgu6oZVmqa8mXEu5R39Ie0xcWF3l60JtZS2mFsNJgDqz8nkL9jaSCl7n02Z6x6SxXS/HiD7+HDY3Wq3lFKN+i7lTY7se3N+t5erCROSALQOyH4vW3PxQsrcc8bAeh/wdcq6g+y983dmL8p8fPaPURfHRYH3Kdoi4ATg05RPG2e9knpax9epyWECoFHYh7JJTV+D6BPAr4FzaH8NLsP+lA/9ZP9gRx4rGdfncw8E3g9cQb+J60bg+B6uT+O3jLZYewhMANStKcpe710PnA9TFnq9k/62xO3SfsCN5P9wRxzXMO6Phi2h7On/OeBuur9fD1D+/0uzCUkAWvcjX9z1VWrUPkR3A+WTwK+AtzKZiegz6Cd56vJYybh//Lc3RXlCv4T29VOzHd/r64I0WiYAGrQj6O4Lb1eTt5q8T9PAeYxzm+SLGFfZv9ZyytbEXX246j39XYpG6Dm0xdeDYAKg7nSxov0e4KQer2EoTqZ02Owf9bkcG4CPdHMbBukoyh7/0ffxn5T1M9JMQhKA1p2/JjnD1/y9jfgB8RKGv4q/S/sBl5H/Az/bcQfli4ELzRTl2wTR1YAL+rwIjYoJgAZpN8q2slGD4BPAB3u9gmF7NeVVtewf+22PNZSvBS708WAFZYe1yNh/Ua9XoLEwAdAgnUHcALiOUv7W/5umvPGQnQispayOX9bt5Y7KEcR+stgFgZrJctri6u/Qvi1rX3t6axwWE/eq1Eb8bOrOTAFvAC6n21Xp2x93AZ+g7EeupzuEsgFVxL3eBLyg3+ZrBEwANDinEjPoPUl5wtXc7UfZvOZKutm85k7gy8CJ+PGauTiKuK88fqvntmv4TAA0ODcTM+B9qu+GT5gllPfVz6QsnryVsqp8Lvf+CeBeym6KX6R8qfD5vbZ+cpxEzMevNgD79tx2DdsBtMXUA2ACoDjHEPPjfz3GVVf2AA4HXgK8EnjdluOllG2TD8J1PdHOJ6ZfnNl3wzVoIQlA6ycxp7u+So3GF2gf5NYBh/XdcKlDS4j5tsPtfTdcg2YCoMGYAv5G+yD3yb4bLvXgBGJ2czyy74ZrsA6kLZbuBxMAxTiO9sHtQWD3vhsu9eTHtPeRs3tvtYaqOQGYpn017+bG8zUZ3hTwNz5PWewkTaLzAv7GKQF/Q/qf1rKUrwMJyorxljhaCzyr70ZLPfsNbf1kI7Br763WEB1EQAVAarWIsqq8xfcp765Lk+ybjefvChwb0RAteJudAlCEo2n/SM/lEQ2RBu4HlH0WWrwsoiGSFQBFaH36X0eZQpAm3RrKPhctXhzREMkEQBGe13j+bylzm9JCcG3j+YeHtEJj11y9NwFQhNaNe24OaYU0Drc0nn9oRCOkadpeu1of1RCN2iGN568KaYU0Dn9oPP9Aylc3tbA92Xr+NFu2A5yn+xsboMmwf+P5fw1phTQOD9E25bUI2DuoLRqvf9G2CH/1NG2Lr1rnsjQZ9mg8/6GQVkjjsJn2mG9960bj9zhwV8P5q6Ypnwqdr0sbztXkaB2M1oW0QhqP1pjfM6QVGrsfRpx7BfW7CPnetrZaQ9uOVO4AqIXmJtr6zMv7b7IGaDllF9Xa+Pk927wFuDfwp4qT/4iDtp7yKG2D2V79N1lK9Tva+szx/TdZA3U6dbGzjhn2ktgXWDmHk68G9unyajQ6D9M2mO3bf5OlVDfQ1mdW9N9kDdg5zO3Lvo8CJ832h94M/ITyeuDWk9YDVxHzxTdNnq2rUed7tL5FII3NdbT1mVf132QN3GuA29hxzPwIOGLbE3aZ4Y9cteWYApZt+W+rt/wBaSat76O6IZUWGvuMol1LKe0fB5wIPJfypsDdwM+Be7c/YaYEYKvN+HqW5qZ1MFsU0gppPOwz6srtW46dMotUhE2N5xuHWmjsM0pnECmC5Uypjn1G6QwiRWh9mrGcqYXGPqN0JgCK4NOMVMc+o3QGkSK4oEmqY59ROhMARXBBk1THPqN0BpEiWM6U6thnlM4gUgTLmVId+4zSmQAoguVMqY59RukMIkWwnCnVsc8onUGkCL7TLNVxCkDpTAAUwacZqY5TAEpnECmCCYBUxz6jdAaRIjgFINVxCkDpTAAUwacZqY5TAEpnECmCTzNSHfuM0pkAKIJPM1Idq2ZKZxApgoOZVMekWekMIkWwnCnVsc8onQmAIvg0I9WxzyidQaQITgFIdewzSmcQKYL7AEh1nAJQOhMARfBpRqrjFIDSGUSK4NOMVMc+o3QmAIrg04xUx6qZ0hlEiuBgJtUxaVY6g0gRLGdKdTY3nu/YrWYGkSL4NCPVsc8onUGkCE4BSHWsmimdA68iOJhJdUyalc4gUgTLmVId+4zSGUSK4NOMVMeqmdI58CqCWwFLdUyalc4gUgQHM6mOSbPSOfAqguVMqY5Js9IZRIrggiapjn1G6QwiRfBpRqpj1UzpHHgVwcFMqmPSrHQGkSJYzpTq2GeUziBSBJ9mpDpWzZTOgVcRHMykOibNSmcQKYLlTKmO+wAonQOvIlgBkOpYAVA6g0gRWgezqZBWSONhAqB0BpEiWAGQ6jgFoHQmAIrgGgCpjhUApTOIFMHBTKpjn1E6g0gRnAKQ6jgFoHQmAIrgFIBUxwqA0hlEiuBgJtWxzyidQaQIljOlOvYZpTMBUASfZqQ69hmlM4gUwUWAUh0rAEpnAqAILgKU6lgBUDqDSBEczKQ69hmlM4gUwSkAqY5TAEpnAqAITgFIdawAKJ1BpAgOZlId+4zSGUSK4BSAVMcpAKUzAVAEpwCkOlYAlM4gUgQHM6mOVTOlc+BVBMuZUh2rZkpnECmCFQCpjn1G6QwiRbCcKdWxzyidCYAiWM6U6thnlM4gUgTLmVId+4zSGUSKYDlTqmOfUToTAEWwnCnVsc8onUGkCJYzpTr2GaUziBTBcqZUx70zlM4EQBEsZ0p1rAAonUGkCFYApDr2GaUzAVAEKwBSHfuM0hlEimA5U6pjn1E6g0gRXNAk1bHPKJ0JgCI81nj+2pBWSOOxnrYkoLXPSSYACnE/bSXN+6IaIo3EJuCBhvPtM2pmAqAIjwE3NZz/i6iGSCPyy4Zz7TOSBuM0YPM8jgeBPftvrpTuFZTKWW2feRw4LKG9kjSjaeBG6gezUzMaKw3Et6nvM+dnNFSSZnMAcA9zH8i+lNJKaTh2B25g7n3mp8AuKS2VpJ1YCqxk9kFsLXBWVgOlgdkNuJiyMHBHfeY/wGfxx1/SCLweuJRSEXgceAS4BTgXWJ7WKmm4jgUuBFZRkuQ1wB2UH/4jE9ulCfVfKyatTcUDzPMAAAAASUVORK5CYII="/>
                          </defs>
                          </svg>
                          
                      </div>
            <div class="text-wrapper-37">{api_data['g']['population']:,}</div>
            </div>
            </div>
            <div class="group-19">
            <div class="overlap-16">
            <div class="frame-52">
            <div class="frame-53"><div class="text-wrapper-38">S.No.</div></div>
            <div class="frame-54"><div class="text-wrapper-39">Name</div></div>
            <div class="overall-PDI-score-wrapper">
            <div class="text-wrapper-40">Overall PDI Score</div>
            
            </div>
            <div class="frame-55"><div class="text-wrapper-40">T1</div></div>
            <div class="frame-56"><div class="text-wrapper-40">T2</div></div>
            <div class="frame-57"><div class="text-wrapper-40">T3</div></div>
            <div class="frame-55"><div class="text-wrapper-40">T4</div></div>
            <div class="frame-56"><div class="text-wrapper-40">T5</div></div>
            <div class="frame-55"><div class="text-wrapper-40">T6</div></div>
            <div class="frame-56"><div class="text-wrapper-40">T7</div></div>
            <div class="frame-55"><div class="text-wrapper-40">T8</div></div>
            <div class="frame-58"><div class="text-wrapper-40">T9</div></div>
            <div class="frame-59"><div class="text-2">1</div></div>
            <div class="frame-60">
            <div class="frame-61">
              <div class="frame-62"><div class="text-wrapper-41">P</div></div>
            </div>
            </div>
            <div class="frame-63overall">
            <div class="text-wrapper-42">{api_data['matrix'][0]['pdi_score']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][0]['gp_g'][:2]}</div>
            </div>
            <div class="frame-64">
            <div class="text-wrapper-43">{api_data['matrix'][0]['t1']}</div>
            <div class="text-wrapper-43">{api_data['pdi_s'][1]['gp_g'][:2]}</div>
            </div>
            <div class="frame-65">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t2']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][2]['gp_g'][:2]}</div>
            </div>
            <div class="frame-66">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t3']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][3]['gp_g'][:2]}</div>
            </div>
            <div class="frame-67">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t4']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][4]['gp_g'][:2]}</div>
            </div>
            <div class="frame-68">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t5']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][5]['gp_g'][:2]}</div>
            </div>
            <div class="frame-69">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t6']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][6]['gp_g'][:2]}</div>
            </div>
            <div class="frame-68">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t7']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][7]['gp_g'][:2]}</div>
            </div>
            <div class="frame-69">
            <div class="text-wrapper-42">{api_data['matrix'][0]['t8']}</div>
            <div class="text-wrapper-42">{api_data['pdi_s'][8]['gp_g'][:2]}</div>
            </div>
            <div class="frame-70">
            <div class="text-wrapper-43">{api_data['matrix'][0]['t9']}</div>
            <div class="text-wrapper-43">{api_data['pdi_s'][9]['gp_g'][:2]}</div>
            </div>
            <div class="frame-71"><div class="text-2">2</div></div>
            <div class="frame-72">
            <div class="frame-73">
              <div class="frame-61">
                <div class="frame-62"><div class="text-wrapper-44">BP</div></div>
              </div>
            </div>
            <svg class="openmoji-crown" width="13" height="14" viewBox="0 0 13 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M0.722229 9.82104H12.2778V11.1331H0.722229V9.82104Z" fill="white"/>
              <path d="M6.49927 4.2931C6.99786 4.2931 7.40205 3.88892 7.40205 3.39033C7.40205 2.89174 6.99786 2.48755 6.49927 2.48755C6.00068 2.48755 5.5965 2.89174 5.5965 3.39033C5.5965 3.88892 6.00068 4.2931 6.49927 4.2931Z" fill="white"/>
              <path d="M0.722229 9.82104H12.2778V11.1331H0.722229V9.82104Z" fill="#F1B31C"/>
              <path d="M1.26389 2.48608C1.50332 2.48608 1.73294 2.5812 1.90225 2.7505C2.07155 2.91981 2.16666 3.14943 2.16666 3.38886C2.16666 3.62829 2.07155 3.85792 1.90225 4.02722C1.73294 4.19653 1.50332 4.29164 1.26389 4.29164M11.7361 4.29164C11.4967 4.29164 11.2671 4.19653 11.0977 4.02722C10.9284 3.85792 10.8333 3.62829 10.8333 3.38886C10.8333 3.14943 10.9284 2.91981 11.0977 2.7505C11.2671 2.5812 11.4967 2.48608 11.7361 2.48608" fill="#FCEA2B"/>
              <path d="M11.7302 3.65879C11.7302 5.29824 10.4011 6.62749 8.76146 6.62749H8.70964C7.07001 6.62749 6.64354 5.29842 6.64354 3.65861H6.26907C6.26907 5.29842 5.84278 6.62749 4.20315 6.62749H4.23276C3.77751 6.62785 3.32828 6.52336 2.91992 6.32212C2.51156 6.12088 2.15502 5.8283 1.87796 5.46706C1.47878 4.9488 1.26282 4.31277 1.26389 3.65861V2.48608V9.82097H11.7361V2.48608" fill="#FCEA2B"/>
              <path d="M6.49927 4.2931C6.99786 4.2931 7.40205 3.88892 7.40205 3.39033C7.40205 2.89174 6.99786 2.48755 6.49927 2.48755C6.00068 2.48755 5.5965 2.89174 5.5965 3.39033C5.5965 3.88892 6.00068 4.2931 6.49927 4.2931Z" fill="#FCEA2B"/>
              <path d="M1.2639 2.48608V9.82097H11.7361V2.48608M0.722229 9.82097H12.2778V11.1331H0.722229V9.82097Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M1.2639 2.48608C1.50333 2.48608 1.73296 2.5812 1.90226 2.7505C2.07156 2.91981 2.16668 3.14943 2.16668 3.38886C2.16668 3.62829 2.07156 3.85792 1.90226 4.02722C1.73296 4.19653 1.50333 4.29164 1.2639 4.29164" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4.23276 6.62744C3.77751 6.6278 3.32828 6.52331 2.91992 6.32207C2.51156 6.12084 2.15502 5.82825 1.87796 5.46701C1.47878 4.94876 1.26282 4.31273 1.26389 3.65857M11.7302 3.65875C11.7302 5.29819 10.4011 6.62744 8.76146 6.62744" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6.49929 4.2931C6.99788 4.2931 7.40207 3.88892 7.40207 3.39033C7.40207 2.89174 6.99788 2.48755 6.49929 2.48755C6.0007 2.48755 5.59651 2.89174 5.59651 3.39033C5.59651 3.88892 6.0007 4.2931 6.49929 4.2931Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11.7361 4.29164C11.4967 4.29164 11.2671 4.19653 11.0978 4.02722C10.9285 3.85792 10.8333 3.62829 10.8333 3.38886C10.8333 3.14943 10.9285 2.91981 11.0978 2.7505C11.2671 2.5812 11.4967 2.48608 11.7361 2.48608M1.2639 2.48608C1.50333 2.48608 1.73295 2.5812 1.90226 2.7505C2.07156 2.91981 2.16667 3.14943 2.16667 3.38886C2.16667 3.62829 2.07156 3.85792 1.90226 4.02722C1.73295 4.19653 1.50333 4.29164 1.2639 4.29164M0.722229 9.82097H12.2778V11.1331H0.722229V9.82097Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11.7361 4.29164C11.4967 4.29164 11.2671 4.19653 11.0978 4.02722C10.9285 3.85792 10.8333 3.62829 10.8333 3.38886C10.8333 3.14943 10.9285 2.91981 11.0978 2.7505C11.2671 2.5812 11.4967 2.48608 11.7361 2.48608" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6.24668 4.26889C6.14051 5.61583 5.63351 6.62749 4.20315 6.62749H4.23276C3.77751 6.62785 3.32828 6.52336 2.91992 6.32212C2.51156 6.12088 2.15502 5.8283 1.87796 5.46706C1.47878 4.9488 1.26282 4.31277 1.26389 3.65861V2.48608V9.82097H11.7361V2.48608" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11.7302 3.65881C11.7302 5.29826 10.4011 6.62751 8.76146 6.62751H8.70964C7.28217 6.62751 6.77409 5.62001 6.66666 4.2774" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6.49929 4.2931C6.99788 4.2931 7.40207 3.88892 7.40207 3.39033C7.40207 2.89174 6.99788 2.48755 6.49929 2.48755C6.0007 2.48755 5.59651 2.89174 5.59651 3.39033C5.59651 3.88892 6.0007 4.2931 6.49929 4.2931Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              
            <!-- <img class="openmoji-crown" src="https://c.animaapp.com/Qr0MpKdr/img/openmoji-crown.svg" /> -->
            </div>
            <div class="frame-74">
            {image_src_map[l1[0]]}
            
            
             
            <div class="text-wrapper-43">{api_data['matrix'][1]['pdi_score']}</div>
            <div class="text-wrapper-451">{api_data['pdi_s'][0]['bgpn'] } </div>
            </div>
            <div class="frame-75">
            {image_src_map[l1[1]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t1']}</div>
            </div>
            <div class="frame-76">
            {image_src_map[l1[2]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t2']}</div>
            </div>
            <div class="frame-77">
            {image_src_map[l1[3]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t3']}</div>
            </div>
            <div class="frame-75">
            {image_src_map[l1[4]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t4']}</div>
            </div>
            <div class="frame-76">
            {image_src_map[l1[5]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t5']}</div>
            </div>
            <div class="frame-75">
            {image_src_map[l1[6]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t6']}</div>
            </div>
            <div class="frame-76">
            {image_src_map[l1[7]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t7']}</div>
            </div>
            <div class="frame-75">
            {image_src_map[l1[8]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t8']}</div>
            </div>
            <div class="frame-78">
            {image_src_map[l1[9]]}
            <div class="text-wrapper-43">{api_data['matrix'][1]['t9']}</div>
            </div>
            <div class="frame-79"><div class="text-2">3</div></div>
            <div class="frame-80">
            <div class="frame-61">
              <div class="frame-62"><div class="text-wrapper-41">B</div></div>
            </div>
            </div>
            <div class="frame-81">
            <div class="frame-82">
              {image_src_map[l2[0]]}
              <!-- <img class="icon" src="https://c.animaapp.com/Qr0MpKdr/img/icon@3x.png" /> -->
            </div>
            <div class="text-wrapper-43">{api_data['matrix'][2]['pdi_score']}</div>
            </div>
            <div class="frame-83">
            {image_src_map[l2[1]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t1']}</div>
            </div>
            <div class="frame-84">
            {image_src_map[l2[2]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t2']}</div>
            </div>
            <div class="frame-85">
            {image_src_map[l2[3]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t3']}</div>
            </div>
            <div class="frame-83">
            {image_src_map[l2[4]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t4']}</div>
            </div>
            <div class="frame-84">
            {image_src_map[l2[5]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t5']}</div>
            </div>
            <div class="frame-83">
            <div class="frame-82">
              {image_src_map[l2[6]]}
              <!-- <img class="icon" src="https://c.animaapp.com/Qr0MpKdr/img/icon-2@3x.png" /> -->
            </div>
            <div class="text-wrapper-43">{api_data['matrix'][2]['t6']}</div>
            </div>
            <div class="frame-84">
            {image_src_map[l2[7]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t7']}</div>
            </div>
            <div class="frame-83">
            {image_src_map[l2[8]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t8']}</div>
            </div>
            <div class="frame-86">
            {image_src_map[l2[9]]}
            <div class="text-wrapper-43">{api_data['matrix'][2]['t9']}</div>
            </div>
            <div class="frame-87"><div class="text-2">4</div></div>
            <div class="frame-88">
            <div class="frame-61">
              <div class="frame-62"><div class="text-wrapper-46">D</div></div>
            </div>
            </div>
            <div class="frame-89">
            {image_src_map[l3[0]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['pdi_score']}</div>
            </div>
            <div class="frame-90">
            {image_src_map[l3[1]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t1']}</div>
            </div>
            <div class="frame-91">
            {image_src_map[l3[2]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t2']}</div>
            </div>
            <div class="frame-92">
            {image_src_map[l3[3]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t3']}</div>
            </div>
            <div class="frame-90">
            {image_src_map[l3[4]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t4']}</div>
            </div>
            <div class="frame-91">
            {image_src_map[l3[5]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t5']}</div>
            </div>
            <div class="frame-90">
            {image_src_map[l3[6]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t6']}</div>
            </div>
            <div class="frame-91">
            {image_src_map[l3[7]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t7']}</div>
            </div>
            <div class="frame-90">
            {image_src_map[l3[8]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t8']}</div>
            </div>
            <div class="frame-93">
            {image_src_map[l3[9]]}
            <div class="text-wrapper-43">{api_data['matrix'][3]['t9']}</div> 
            </div>
            <div class="frame-94"><div class="text-2">5</div></div>
            <div class="frame-80">
            <div class="frame-61">
              <div class="frame-62"><div class="text-wrapper-41">S</div></div>
            </div>
            </div>
            <div class="frame-81">
                {image_src_map[l4[0]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['pdi_score']}</div>
                </div>
                <div class="frame-83">
                {image_src_map[l4[1]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t1']}</div>
                </div>
                <div class="frame-84">
                {image_src_map[l4[2]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t2']}</div>
                </div>
                <div class="frame-85">
                {image_src_map[l4[3]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t3']}</div>
                </div>
                <div class="frame-83">
                {image_src_map[l4[4]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t4']}</div>
                </div>
                <div class="frame-84">
                {image_src_map[l4[5]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t5']}</div>
                </div>
                <div class="frame-83">
                {image_src_map[l4[6]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t6']}</div>
                </div>
                <div class="frame-84">
                {image_src_map[l4[7]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t7']}</div>
                </div>
                <div class="frame-83">
                  {image_src_map[l4[8]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t8']}</div>
                </div>
                <div class="frame-95">
                {image_src_map[l4[9]]}
                <div class="text-wrapper-43">{api_data['matrix'][4]['t9']}</div>
                </div>
                </div>
                <div class="frame-96">
                <div class="frame-43">
                <div class="frame-82">
                  <div class="frame-97">
                    <div class="frame-61">
                      <div class="frame-62"><div class="text-wrapper-44">BP</div></div>
                    </div>
                  </div>
                  <svg class="openmoji-crown-2" width="13" height="14" viewBox="0 0 13 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M0.722229 9.82104H12.2778V11.1331H0.722229V9.82104Z" fill="white"/>
                    <path d="M6.49927 4.2931C6.99786 4.2931 7.40205 3.88892 7.40205 3.39033C7.40205 2.89174 6.99786 2.48755 6.49927 2.48755C6.00068 2.48755 5.5965 2.89174 5.5965 3.39033C5.5965 3.88892 6.00068 4.2931 6.49927 4.2931Z" fill="white"/>
                    <path d="M0.722229 9.82104H12.2778V11.1331H0.722229V9.82104Z" fill="#F1B31C"/>
                    <path d="M1.26389 2.48608C1.50332 2.48608 1.73294 2.5812 1.90225 2.7505C2.07155 2.91981 2.16666 3.14943 2.16666 3.38886C2.16666 3.62829 2.07155 3.85792 1.90225 4.02722C1.73294 4.19653 1.50332 4.29164 1.26389 4.29164M11.7361 4.29164C11.4967 4.29164 11.2671 4.19653 11.0977 4.02722C10.9284 3.85792 10.8333 3.62829 10.8333 3.38886C10.8333 3.14943 10.9284 2.91981 11.0977 2.7505C11.2671 2.5812 11.4967 2.48608 11.7361 2.48608" fill="#FCEA2B"/>
                    <path d="M11.7302 3.65879C11.7302 5.29824 10.4011 6.62749 8.76146 6.62749H8.70964C7.07001 6.62749 6.64354 5.29842 6.64354 3.65861H6.26907C6.26907 5.29842 5.84278 6.62749 4.20315 6.62749H4.23276C3.77751 6.62785 3.32828 6.52336 2.91992 6.32212C2.51156 6.12088 2.15502 5.8283 1.87796 5.46706C1.47878 4.9488 1.26282 4.31277 1.26389 3.65861V2.48608V9.82097H11.7361V2.48608" fill="#FCEA2B"/>
                    <path d="M6.49927 4.2931C6.99786 4.2931 7.40205 3.88892 7.40205 3.39033C7.40205 2.89174 6.99786 2.48755 6.49927 2.48755C6.00068 2.48755 5.5965 2.89174 5.5965 3.39033C5.5965 3.88892 6.00068 4.2931 6.49927 4.2931Z" fill="#FCEA2B"/>
                    <path d="M1.2639 2.48608V9.82097H11.7361V2.48608M0.722229 9.82097H12.2778V11.1331H0.722229V9.82097Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M1.2639 2.48608C1.50333 2.48608 1.73296 2.5812 1.90226 2.7505C2.07156 2.91981 2.16668 3.14943 2.16668 3.38886C2.16668 3.62829 2.07156 3.85792 1.90226 4.02722C1.73296 4.19653 1.50333 4.29164 1.2639 4.29164" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M4.23276 6.62744C3.77751 6.6278 3.32828 6.52331 2.91992 6.32207C2.51156 6.12084 2.15502 5.82825 1.87796 5.46701C1.47878 4.94876 1.26282 4.31273 1.26389 3.65857M11.7302 3.65875C11.7302 5.29819 10.4011 6.62744 8.76146 6.62744" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M6.49929 4.2931C6.99788 4.2931 7.40207 3.88892 7.40207 3.39033C7.40207 2.89174 6.99788 2.48755 6.49929 2.48755C6.0007 2.48755 5.59651 2.89174 5.59651 3.39033C5.59651 3.88892 6.0007 4.2931 6.49929 4.2931Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M11.7361 4.29164C11.4967 4.29164 11.2671 4.19653 11.0978 4.02722C10.9285 3.85792 10.8333 3.62829 10.8333 3.38886C10.8333 3.14943 10.9285 2.91981 11.0978 2.7505C11.2671 2.5812 11.4967 2.48608 11.7361 2.48608M1.2639 2.48608C1.50333 2.48608 1.73295 2.5812 1.90226 2.7505C2.07156 2.91981 2.16667 3.14943 2.16667 3.38886C2.16667 3.62829 2.07156 3.85792 1.90226 4.02722C1.73295 4.19653 1.50333 4.29164 1.2639 4.29164M0.722229 9.82097H12.2778V11.1331H0.722229V9.82097Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M11.7361 4.29164C11.4967 4.29164 11.2671 4.19653 11.0978 4.02722C10.9285 3.85792 10.8333 3.62829 10.8333 3.38886C10.8333 3.14943 10.9285 2.91981 11.0978 2.7505C11.2671 2.5812 11.4967 2.48608 11.7361 2.48608" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M6.24668 4.26889C6.14051 5.61583 5.63351 6.62749 4.20315 6.62749H4.23276C3.77751 6.62785 3.32828 6.52336 2.91992 6.32212C2.51156 6.12088 2.15502 5.8283 1.87796 5.46706C1.47878 4.9488 1.26282 4.31277 1.26389 3.65861V2.48608V9.82097H11.7361V2.48608" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M11.7302 3.65881C11.7302 5.29826 10.4011 6.62751 8.76146 6.62751H8.70964C7.28217 6.62751 6.77409 5.62001 6.66666 4.2774" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M6.49929 4.2931C6.99788 4.2931 7.40207 3.88892 7.40207 3.39033C7.40207 2.89174 6.99788 2.48755 6.49929 2.48755C6.0007 2.48755 5.59651 2.89174 5.59651 3.39033C5.59651 3.88892 6.0007 4.2931 6.49929 4.2931Z" stroke="black" stroke-width="0.2" stroke-miterlimit="10" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    
                  <!-- <img class="openmoji-crown-2" src="https://c.animaapp.com/Qr0MpKdr/img/openmoji-crown-1.svg" /> -->
                  <div class="text-wrapper-47">Best Panchayat</div>
                </div>
                <div class="frame-82">
                  <div class="frame-61">
                    <div class="frame-62"><div class="text-wrapper-41">P</div></div>
                  </div>
                  <div class="text-wrapper-47">My Panchayat</div>
                </div>
                <div class="frame-82">
                  <div class="frame-61">
                    <div class="frame-62"><div class="text-wrapper-41">B</div></div>
                  </div>
                  <div class="text-wrapper-47">Block</div>
                </div>
                <div class="frame-82">
                  <div class="frame-61">
                    <div class="frame-62"><div class="text-wrapper-46">D</div></div>
                  </div>
                  <div class="text-wrapper-47">District</div>
                </div>
                <div class="frame-82">
                  <div class="frame-61">
                    <div class="frame-62"><div class="text-wrapper-41">S</div></div>
                  </div>
                  <div class="text-wrapper-47">State</div>
                </div>
                </div>
                <div class="frame-98">
                <div class="frame-99">
                  <p class="div-4">
                    <span class="text-wrapper-48">State:</span> <span class="text-wrapper-4"> {api_data['g']['state_name_en']}</span>
                  </p>
                  <p class="div-4">
                    <span class="text-wrapper-48">District: </span> <span class="text-wrapper-4">{api_data['g']['d_name_en']}</span>
                  </p>
                  <p class="div-4">
                    <span class="text-wrapper-48">Block:</span> <span class="text-wrapper-4"> {api_data['g']['b_name_en']}</span>
                  </p>
                </div>
                <div class="text-wrapper-48">Gram Panchayat: &nbsp; &nbsp;<span class="text-wrapper-48gp">{api_data['g']['gp_name_en']} </span> </div>
                </div>
                </div>
                
                <div class="rectangle-18"></div>
                <div class="rectangle-19"></div>
                <p class="text-wrapper-50">Performance of My Panchayat, Best Panchayat, Block, District and State</p>
                </div>
                </div>
                          


                    </div>
                </div>
            </div>
            
        </body>
        </html>
        
        
        
        """
        
        
        
        
        
    #     options = {
    #     'page-size': 'A4',  # This sets the page size to standard A4
    # }
        options = {
    'page-width': '310',  # A3 width in millimeters
    'page-height': '420mm',  # A3 height in millimeters
}


        # Convert HTML to PDF
        pdf_output_path = "/tmp/output.pdf"
        pdfkit.from_string(html_content, pdf_output_path,configuration=PDF_CONFIG,options=options)

        # Return the generated PDF as a response
        # with open(pdf_output_path, "rb") as pdf_file:
        #     pdf_data = pdf_file.read()

        # Clean up and close database connection
        # cursor.close()
        # connection.close()
        # os.remove(pdf_output_path)
        return FileResponse(pdf_output_path,media_type="application/pdf",filename="report.pdf")

        # return {"pdf": pdf_data.hex()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
