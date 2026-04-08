from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Process data
def process_data(data):
    result = []

    for student in data:
        # Sort history by date properly
        history = sorted(
            student["history"],
            key=lambda x: x["date"]
        )

        total = sum(entry["latest"] for entry in history)

        latest = history[-1]["latest"] if history else 0
        previous = total - latest

        result.append({
            "name": student["name"],
            "previous": previous,
            "latest": latest,
            "total": total
        })

    # 🔥 CRITICAL: Sort ONLY by total
    result = sorted(result, key=lambda x: x["total"], reverse=True)

    return result

@app.get("/")
def home(request: Request):
    with open("data.json") as f:
        data = json.load(f)

    leaderboard = process_data(data)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "leaderboard": leaderboard
    })

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)