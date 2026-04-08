from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import json
import os

app = FastAPI()

# ✅ Absolute path fix (important for Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ✅ Process data safely
def process_data(data):
    result = []

    for student in data:
        history = student.get("history", [])

        # Sort history by date
        history = sorted(history, key=lambda x: x.get("date", ""))

        total = sum(entry.get("latest", 0) for entry in history)

        latest = history[-1].get("latest", 0) if history else 0
        previous = total - latest

        result.append({
            "name": student.get("name", ""),
            "previous": previous,
            "latest": latest,
            "total": total
        })

    # ✅ Sort ONLY by total
    result = sorted(result, key=lambda x: x["total"], reverse=True)

    return result


@app.get("/")
def home(request: Request):
    try:
        with open(os.path.join(BASE_DIR, "data.json")) as f:
            data = json.load(f)

        leaderboard = process_data(data)

        # ✅ PRE-COMPUTE TOP 3
        top1 = leaderboard[0] if len(leaderboard) > 0 else None
        top2 = leaderboard[1] if len(leaderboard) > 1 else None
        top3 = leaderboard[2] if len(leaderboard) > 2 else None

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "leaderboard": leaderboard,
                "top1": top1,
                "top2": top2,
                "top3": top3
            }
        )

    except Exception as e:
        return {"error": str(e)}

# ✅ Required for Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)