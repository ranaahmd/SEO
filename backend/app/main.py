from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/analyze")
async def analyze_seo(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient() as client:
        try:
            # إضافة http إذا لم تكن موجودة
            if not url.startswith('http'):
                url = 'https://' + url
                
            response = await client.get(url, headers=headers, timeout=15.0, follow_redirects=True)
            soup = BeautifulSoup(response.text, "lxml")
            
            title = soup.title.string.strip() if soup.title else "No Title Found"
            
            desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            description = desc_tag["content"].strip() if desc_tag else "No Meta Description found for this site."

            # حساب درجة تقديرية بسيطة
            score = 0
            if len(title) > 10: score += 50
            if desc_tag: score += 50

            return {
                "title": title,
                "description": description,
                "score": score,
                "status": "Success"
            }
        except Exception as e:
            return {"error": str(e), "title": "Error", "description": "Could not analyze", "score": 0}

@app.get("/download-pdf")
async def download_pdf(
    url: str = Query(...), 
    title: str = Query("N/A"), 
    description: str = Query("N/A"), 
    score: str = Query("0")
):
    file_path = "seo_report.pdf"
    c = canvas.Canvas(file_path)
    
    # تنسيق الـ PDF
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, 750, "SEO Analysis Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"URL: {url}")
    c.drawString(100, 680, f"Score: {score}/100")
    c.drawString(100, 660, f"Title: {title[:50]}...")
    
    # كتابة الوصف مع مراعاة الطول
    c.drawString(100, 640, "Description:")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, 625, f"{description[:100]}...")
    
    c.save()
    return FileResponse(file_path, filename="SEO_Report.pdf")