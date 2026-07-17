"""
FIFA World Cup 2026 Nexus AI - FastAPI Application Server
Provides REST APIs, Security Middleware, and WebSocket Telemetry for Fan Companion & Stadium Ops Command.
"""

import asyncio
import json
import random
import html
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.stadium_data import STADIUMS, INCIDENTS_MOCK
from backend.ai_engine import ai_engine

app = FastAPI(
    title="FIFA World Cup 2026 Nexus AI Server",
    description="GenAI Stadium Operations & Fan Experience Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security Middleware - Headers & Protection
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Enable CORS (Configured securely)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static directory for frontend assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Structured Pydantic Models for Robust Type Safety & Validation
class FanQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User question or prompt")
    stadium_id: Optional[str] = Field("metlife", description="Target stadium ID")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="Optional user metadata")

class OperationalIncidentRequest(BaseModel):
    description: str = Field(..., min_length=5, max_length=2000, description="Natural language incident report")
    stadium_id: Optional[str] = Field("metlife", description="Stadium location ID")

class VolunteerBriefingRequest(BaseModel):
    stadium_id: str = Field("metlife", description="Stadium ID")
    role: str = Field("Gate & Accessibility Concierge", description="Staff role for briefing")

class APIResponseModel(BaseModel):
    status: str
    data: Optional[Any] = None

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# REST Endpoints
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("static/index.html")

@app.get("/api/stadiums")
async def get_stadiums():
    return {"status": "success", "stadiums": list(STADIUMS.values())}

@app.get("/api/stadium/{stadium_id}")
async def get_stadium_detail(stadium_id: str):
    clean_id = html.escape(stadium_id)
    if clean_id not in STADIUMS:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return {"status": "success", "stadium": STADIUMS[clean_id]}

@app.post("/api/fan/chat")
async def fan_chat_endpoint(req: FanQueryRequest):
    clean_query = html.escape(req.query.strip())
    clean_stadium = html.escape(req.stadium_id or "metlife")
    
    result = ai_engine.process_fan_query(
        query=clean_query,
        stadium_id=clean_stadium,
        user_context=req.user_context
    )
    return {"status": "success", "data": result}

@app.post("/api/ops/incident")
async def create_incident(req: OperationalIncidentRequest):
    clean_desc = html.escape(req.description.strip())
    clean_stadium = html.escape(req.stadium_id or "metlife")

    result = ai_engine.process_operational_incident(
        description=clean_desc,
        stadium_id=clean_stadium
    )
    INCIDENTS_MOCK.insert(0, result)
    
    # Broadcast incident update via WebSocket stream
    await manager.broadcast({
        "type": "NEW_INCIDENT",
        "incident": result
    })
    
    return {"status": "success", "data": result}

@app.get("/api/ops/incidents")
async def get_incidents():
    return {"status": "success", "incidents": INCIDENTS_MOCK}

@app.post("/api/ops/briefing")
async def generate_volunteer_briefing(req: VolunteerBriefingRequest):
    stadium_id = html.escape(req.stadium_id)
    stadium = STADIUMS.get(stadium_id, STADIUMS["metlife"])
    role = html.escape(req.role)
    
    briefing = (
        f"GenAI Daily Volunteer Briefing - FIFA World Cup 2026\n"
        f"Venue: {stadium['name']} | Shift Role: {role}\n"
        f"Expected Attendance: {stadium['capacity']:,} Fans\n\n"
        f"1. Key Gate Priorities: Gate C experiencing heavy load. Guide mobility-assisted fans to Gate A elevator.\n"
        f"2. Multilingual Support: Use mobile app translation for Spanish, French, and Arabic guest assistance.\n"
        f"3. Eco Transit Incentive: Inform departing fans about 150 Eco-Reward Points on Meadowlands Rail Line.\n"
        f"4. Emergency Contact: Command Center Hotline #9090 or submit incident in Nexus App."
    )
    return {"status": "success", "briefing": briefing}

@app.post("/api/vision/parse")
async def parse_vision(image_type: str = Form(...), file: Optional[UploadFile] = File(None)):
    clean_type = html.escape(image_type)
    filename = file.filename if file else "sample_scan.jpg"
    result = ai_engine.parse_vision_item(filename=filename, image_type=clean_type)
    return {"status": "success", "data": result}

# Real-time WebSocket Telemetry Endpoint
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(8)
            metlife = STADIUMS["metlife"]
            for g in metlife["gates"]:
                g["queue_time_min"] = max(2, g["queue_time_min"] + random.choice([-1, 0, 1]))
                g["crowd_density"] = min(99, max(15, g["crowd_density"] + random.choice([-2, -1, 1, 2])))
            
            await websocket.send_json({
                "type": "TELEMETRY_UPDATE",
                "stadium_id": "metlife",
                "gates": metlife["gates"]
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
