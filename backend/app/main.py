from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse
import httpx
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
import os

app = FastAPI()

# --- إضافة إعدادات CORS للسماح للـ Frontend بالوصول ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح لجميع المواقع بالاتصال (مناسب للتطوير)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def analyze_seo(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code != 200:
                return {"error": f"Failed to fetch site: {response.status_code}"}

            soup = BeautifulSoup(response.text, "lxml")
            title_tag = soup.title.string if soup.title else "No title found"
            desc_tag = soup.find("meta", attrs={"name": "description"})
            description = desc_tag["content"] if desc_tag else "No description found"

            return {
                "url": url,
                "title": title_tag,
                "title_length": len(title_tag),
                "description": description,
                "description_length": len(description),
                "status": "Success"
            }
        except Exception as e:
            return {"error": str(e)}

@app.get("/analyze")
async def get_analysis(url: str):
    return await analyze_seo(url)

@app.get("/download-pdf")
async def download_pdf(url: str, title: str, description: str):
    file_path = "seo_report.pdf"
    c = canvas.Canvas(file_path)
    c.drawString(100, 750, "SEO Analysis Report")
    c.drawString(100, 720, f"URL: {url}")
    c.save()
    return FileResponse(file_path, filename="SEO_Report.pdf")