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
        print("hi")
        # api_data = json.dumps(api_data)
        # api_data = json.load(api_data)
        print(api_data)
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
                    </div>
                </div>
            </div>
            
        </body>
        </html>
        
        
        
        """
        
        
        
        
        
        options = {
        'page-size': 'A4',  # This sets the page size to standard A4
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
