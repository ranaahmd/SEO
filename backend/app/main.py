from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.seo_engine import analyze_seo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح للفرونت إند بالوصول
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to SEO Checker API"}

@app.get("/analyze")
async def get_seo_report(url: str):
    report = await analyze_seo(url)
    return report