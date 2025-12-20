from fastapi import FastAPI
from app.services.seo_engine import analyze_seo

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to SEO Checker API"}

@app.get("/analyze")
async def get_seo_report(url: str):
    report = await analyze_seo(url)
    return report