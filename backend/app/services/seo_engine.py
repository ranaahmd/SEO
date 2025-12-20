import httpx
from bs4 import BeautifulSoup

async def analyze_seo(url: str):
    async with httpx.AsyncClient() as client:
        # 1. محاولة الدخول للموقع
        response = await client.get(url)
        if response.status_code != 200:
            return {"error": "Could not fetch the website"}

        # 2. تحليل محتوى الصفحة
        soup = BeautifulSoup(response.text, "lxml")
        
        # 3. استخراج الـ Title
        title_tag = soup.title.string if soup.title else "No title found"
        
        # 4. استخراج الـ Meta Description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag["content"] if desc_tag else "No description found"

        # 5. بناء التقرير البسيط
        return {
            "url": url,
            "title": title_tag,
            "title_length": len(title_tag),
            "description": description,
            "description_length": len(description),
            "status": "Success"
        }