from fastapi import FastAPI
from routers.scraping import router as scraping_router

app = FastAPI()
app.include_router(scraping_router, prefix="/api/v1/scraping")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)