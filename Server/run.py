import os
import uvicorn

if __name__ == "__main__":
    # Render binds the port via the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, log_level="info")
