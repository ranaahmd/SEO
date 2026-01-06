from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time
import os

app = FastAPI()

# إعدادات CORS للسماح بالوصول من المتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def perform_analysis(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    if not url.startswith('http'):
        url = 'https://' + url

    async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
        start_time = time.time()
        try:
            response = await client.get(url, headers=headers)
            load_time = round(time.time() - start_time, 2)
        except Exception as e:
            return {"error": f"Failed to connect: {str(e)}"}

        soup = BeautifulSoup(response.text, "lxml")
        
        # 1. جمع البيانات الخام
        title = soup.title.string.strip() if soup.title else None
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = desc_tag["content"].strip() if desc_tag else None
        h1_tags = [h.text.strip() for h in soup.find_all("h1")]
        images = soup.find_all("img")
        images_missing_alt = [img.get('src', 'unknown') for img in images if not img.get('alt')]
        links_count = len(soup.find_all("a"))

        # 2. نظام التقييم والنصائح
        total_score = 0
        details = []
        recommendations = []

        # تقييم العنوان (20 درجة)
        if title:
            if 10 <= len(title) <= 60:
                total_score += 20
                details.append(("Title Tag", "Perfect Length", "20/20"))
            else:
                total_score += 10
                details.append(("Title Tag", f"Length Issue ({len(title)})", "10/20"))
                recommendations.append(f"Optimize Title: Current length is {len(title)}. Aim for 50-60 chars.")
        else:
            details.append(("Title Tag", "Missing", "0/20"))
            recommendations.append("Critical: Add a Title tag to improve search visibility.")

        # تقييم الوصف (20 درجة)
        if description:
            total_score += 20
            details.append(("Meta Description", "Found", "20/20"))
        else:
            details.append(("Meta Description", "Missing", "0/20"))
            recommendations.append("Add Meta Description: This helps users understand your page in search results.")

        # تقييم عناوين H1 (15 درجة)
        if len(h1_tags) == 1:
            total_score += 15
            details.append(("H1 Header", "Correct (1 found)", "15/15"))
        elif len(h1_tags) == 0:
            details.append(("H1 Header", "Missing", "0/15"))
            recommendations.append("Add H1 Tag: Your page needs one main heading (H1) for structure.")
        else:
            total_score += 5
            details.append(("H1 Header", f"Multiple ({len(h1_tags)})", "5/15"))
            recommendations.append("Fix H1: Use only ONE H1 tag per page. Use H2-H3 for subheadings.")

        # تقييم الصور (15 درجة)
        if images and not images_missing_alt:
            total_score += 15
            details.append(("Image Alt Text", "All images have Alt", "15/15"))
        elif not images:
             total_score += 15
             details.append(("Image Alt Text", "No images to analyze", "15/15"))
        else:
            total_score += 5
            details.append(("Image Alt Text", f"{len(images_missing_alt)} missing Alt", "5/15"))
            recommendations.append(f"Add Alt Text: {len(images_missing_alt)} images are missing descriptions for SEO and accessibility.")

        # تقييم السرعة (15 درجة)
        if load_time < 2.0:
            total_score += 15
            details.append(("Page Speed", f"Fast ({load_time}s)", "15/15"))
        else:
            total_score += 7
            details.append(("Page Speed", f"Slow ({load_time}s)", "7/15"))
            recommendations.append("Improve Speed: Page takes over 2s to load. Optimize images or scripts.")

        # تقييم الروابط (15 درجة)
        if links_count > 0:
            total_score += 15
            details.append(("Internal Links", f"Found {links_count}", "15/15"))
        else:
            details.append(("Internal Links", "No links found", "0/15"))
            recommendations.append("Build Links: Add internal or external links to help crawlers find your content.")

        return {
            "url": url,
            "score": total_score,
            "details": details,
            "recommendations": recommendations,
            "title": title or "N/A",
            "description": description or "N/A"
        }

@app.get("/analyze")
async def analyze_seo(url: str):
    return await perform_analysis(url)

@app.get("/download-pdf")
async def download_pdf(url: str):
    data = await perform_analysis(url)
    if "error" in data: return data
    
    file_path = "SEO_Action_Plan.pdf"
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # --- Header ---
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.1, 0.3, 0.6)
    c.drawString(50, height - 50, "SEO Analysis & Action Report")
    
    # --- URL & Score ---
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, height - 80, f"Analyzed URL: {url}")
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 110, f"Total Score: {data['score']}/100")
    c.line(50, height - 120, width - 50, height - 120)

    # --- Results Table ---
    y = height - 150
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Test Item")
    c.drawString(250, y, "Finding")
    c.drawString(450, y, "Score")
    
    y -= 20
    c.setFont("Helvetica", 10)
    for item, status, score in data['details']:
        c.drawString(50, y, item)
        c.drawString(250, y, status)
        c.drawString(450, y, score)
        y -= 20

    # --- Recommendations Section ---
    y -= 30
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0.8, 0.1, 0.1)
    c.drawString(50, y, "How to Improve Your Score:")
    c.line(50, y-5, 260, y-5)
    
    y -= 30
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)
    
    if not data['recommendations']:
        c.drawString(50, y, "No major issues found. Great job!")
    else:
        for rec in data['recommendations']:
            if y < 50: # إنشاء صفحة جديدة إذا انتهت المساحة
                c.showPage()
                y = height - 50
            c.drawString(50, y, f"- {rec}")
            y -= 25

    c.save()
    return FileResponse(file_path, filename="SEO_Report.pdf")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)