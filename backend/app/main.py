from fastapi import FastAPI

app = FastAPI(title="Hostel Booking API", version="0.1.0")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
