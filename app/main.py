from fastapi import FastAPI
app = FastAPI()

@app.get("/healthz")
def get_status():
    return {"status":"ok"}