# decision engine
# decides to which provider it's best to route payment
# based on stats and fraud score



from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}