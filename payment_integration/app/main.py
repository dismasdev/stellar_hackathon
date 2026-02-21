from fastapi import FastAPI
from .routes import payments

app = FastAPI()
app.include_router(payments.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Payment Integration API"}

