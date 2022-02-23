import asyncio
from fastapi import FastAPI

app = FastAPI()


@app.get("/success", status_code=200)
async def success():
    return {"message": "responded with success."}



@app.get("/failure", status_code=400)
async def failure():
    return {"message": "responded with failure."}