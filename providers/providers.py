# mock external processors
# add file for each mock
# should have different timeouts and fail rates


from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}