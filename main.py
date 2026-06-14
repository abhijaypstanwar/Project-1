import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",   # points to the `app` object inside app/main.py
        host="0.0.0.0",
        port=8000,
        reload=True,      # auto-restarts server when you save any file
    )