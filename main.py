from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from .database.database import init_db
from .routers import loan_cases, auth
from .utils.logger import logger
import uvicorn

app = FastAPI(title="Credit Underwriter API", version="1.0.0")

# Initialize database
@app.on_event("startup")
def on_startup():
    try:
        init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.critical(f"Application startup failed: {str(e)}")
        raise

# Include routers
app.include_router(auth.router)
app.include_router(loan_cases.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the CSA",
        "version": "1.0.0"
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)