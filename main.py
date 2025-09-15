from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import data


app = FastAPI()

# CORS for your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://black-forest-0125ad50f.1.azurestaticapps.net"],  # TODO: limit in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
