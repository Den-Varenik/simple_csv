from fastapi import FastAPI
from uvicorn import run

from app.config.settings import SECRET_KEY
from app.views import categories, users, dataset

app = FastAPI()
app.state.secret_key = SECRET_KEY

app.include_router(categories.router)
app.include_router(users.router)
app.include_router(dataset.router)


@app.get("/")
async def root():
    return {"message": "Hello FastApi!"}


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)
