"""
VrMpc AI Copilot Server (FastAPI + Groq / Llama 3)
Designed for VR Racing Hands-First - Meta VR Start Competition
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VrMpcCopilot")

app = FastAPI(
    title="VrMpc AI Tactical Copilot",
    description="Asynchronous ultra-low-latency Copilot Backend for Meta Quest VR Racing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Pydantic models matching Unreal Engine structs (tolerant defaults)
class VehicleTelemetry(BaseModel):
    SpeedKmh: float = Field(0.0, description="Current vehicle forward speed in km/h")
    DistanceToRivalAhead: float = Field(-1.0, description="Meters to rival ahead (-1 if none)")
    DistanceToRivalBehind: float = Field(-1.0, description="Meters to rival behind (-1 if none)")
    NitroPercentage: float = Field(100.0, description="Remaining nitro [0-100]")
    CurrentGear: int = Field(1, description="Current gearbox gear")
    TrackSector: str = Field("Sector_1", description="Current track sector name")
    LateralGForce: float = Field(0.0, description="Lateral G-Force")

class ImmediateAlert(BaseModel):
    EventType: str = Field("ALERT", description="Event identifier")
    EventDetails: str = Field("", description="Detailed info")
    SpeedKmh: float = Field(0.0, description="Current vehicle speed in km/h")

class CopilotTacticalOrder(BaseModel):
    AdviceMessage: str = Field("¡Písale a fondo!", description="Radio voice message (max 12 words)")
    TacticalAction: str = Field("FULL_THROTTLE", description="Tactic: USE_NITRO, DEFEND_LEFT, DRIFT_ENTRY, OVERTAKE_RIGHT, BRAKE_NOW, FULL_THROTTLE")
    SuggestedSpeed: float = Field(140.0, description="Target corner/sector speed in km/h")
    CopilotMood: str = Field("CALM", description="CALM, URGENT, AGGRESSIVE")
    VoiceCueId: int = Field(0, description="Mapped sound cue ID for radio playback")


SYSTEM_PROMPT = """
Eres 'Viper', un copiloto táctico veterano de carreras ilegales callejeras estilo Need for Speed.
Tu piloto está conduciendo en VR en Meta Quest 3 a más de 180 km/h.
REGLAS OBLIGATORIAS:
1. Sé ULTRA CONCISO: MÁXIMO de 8 a 12 palabras. Si hablas de más, el piloto chocará.
2. Usa lenguaje apasionado, callejero y enérgico en español ('¡Písale!', '¡Mete el nitro!', '¡Cierra la curva!', '¡Te comen por la izquierda!').
3. Elige la acción táctica adecuada según la telemetría:
   - Si NitroPercentage > 60 y SpeedKmh < 120 en recta: TacticalAction = 'USE_NITRO', VoiceCueId = 1.
   - Si DistanceToRivalBehind > 0 y DistanceToRivalBehind < 15: TacticalAction = 'DEFEND_LEFT' o 'DEFEND_RIGHT', VoiceCueId = 2.
   - Si DistanceToRivalAhead > 0 y DistanceToRivalAhead < 20: TacticalAction = 'OVERTAKE_RIGHT', VoiceCueId = 3.
   - Si la velocidad es excesiva para el sector o curva: TacticalAction = 'BRAKE_NOW', VoiceCueId = 4.
   - Si el derrape o salida de curva es bueno: TacticalAction = 'FULL_THROTTLE', VoiceCueId = 5.
4. Responde EXCLUSIVAMENTE con un objeto JSON válido con los campos exactos:
   AdviceMessage (string), TacticalAction (string), SuggestedSpeed (float), CopilotMood (string: CALM|URGENT|AGGRESSIVE), VoiceCueId (int).
"""

def generate_heuristic_fallback(telemetry: VehicleTelemetry) -> CopilotTacticalOrder:
    """Ultra-fast zero-latency heuristic fallback when offline or API key missing"""
    if telemetry.DistanceToRivalBehind > 0 and telemetry.DistanceToRivalBehind < 12.0:
        return CopilotTacticalOrder(
            AdviceMessage="¡Te comen la retaguardia! ¡Bloquea la izquierda ya!",
            TacticalAction="DEFEND_LEFT",
            SuggestedSpeed=max(telemetry.SpeedKmh, 140.0),
            CopilotMood="URGENT",
            VoiceCueId=2
        )
    elif telemetry.DistanceToRivalAhead > 0 and telemetry.DistanceToRivalAhead < 25.0:
        return CopilotTacticalOrder(
            AdviceMessage="¡Lo tienes a tiro! ¡Toma el rebufo y rebásalo!",
            TacticalAction="OVERTAKE_RIGHT",
            SuggestedSpeed=telemetry.SpeedKmh + 20.0,
            CopilotMood="AGGRESSIVE",
            VoiceCueId=3
        )
    elif telemetry.NitroPercentage > 50.0 and telemetry.SpeedKmh < 130.0:
        return CopilotTacticalOrder(
            AdviceMessage="¡Recta libre! ¡Descarga el Nitro ahora mismo!",
            TacticalAction="USE_NITRO",
            SuggestedSpeed=190.0,
            CopilotMood="AGGRESSIVE",
            VoiceCueId=1
        )
    elif telemetry.SpeedKmh > 190.0 and "Curva" in telemetry.TrackSector:
        return CopilotTacticalOrder(
            AdviceMessage="¡Frena, frena! ¡Entra con derrape controlado!",
            TacticalAction="BRAKE_NOW",
            SuggestedSpeed=110.0,
            CopilotMood="URGENT",
            VoiceCueId=4
        )
    else:
        return CopilotTacticalOrder(
            AdviceMessage="¡Buen ritmo! Mantén la trazada limpia en este sector.",
            TacticalAction="FULL_THROTTLE",
            SuggestedSpeed=telemetry.SpeedKmh + 10.0,
            CopilotMood="CALM",
            VoiceCueId=5
        )

def call_groq_llm(telemetry_data: dict) -> Optional[CopilotTacticalOrder]:
    """Call Groq API using requests (OpenAI-compatible)"""
    if not GROQ_API_KEY:
        return None

    import requests

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    user_content = (
        f"Telemetría actual del coche:\n"
        f"- Velocidad: {telemetry_data.get('SpeedKmh', 0):.1f} km/h\n"
        f"- Distancia rival adelante: {telemetry_data.get('DistanceToRivalAhead', -1):.1f} m\n"
        f"- Distancia rival atrás: {telemetry_data.get('DistanceToRivalBehind', -1):.1f} m\n"
        f"- Nivel de Nitro: {telemetry_data.get('NitroPercentage', 100):.0f}%\n"
        f"- Marcha: {telemetry_data.get('CurrentGear', 1)}\n"
        f"- Sector: {telemetry_data.get('TrackSector', 'Sector_1')}\n"
        f"- G-Lateral: {telemetry_data.get('LateralGForce', 0):.2f} G\n"
        f"Dame la orden táctica inmediata en JSON."
    )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.4,
        "max_tokens": 120,
        "response_format": {"type": "json_object"}
    }

    try:
        t0 = time.time()
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=2.0)
        dt = (time.time() - t0) * 1000.0

        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            logger.info(f"Groq LLM responded in {dt:.1f}ms: {parsed.get('AdviceMessage')}")
            return CopilotTacticalOrder(
                AdviceMessage=parsed.get("AdviceMessage", "¡Acelera a fondo!"),
                TacticalAction=parsed.get("TacticalAction", "FULL_THROTTLE"),
                SuggestedSpeed=float(parsed.get("SuggestedSpeed", telemetry_data.get("SpeedKmh", 120.0))),
                CopilotMood=parsed.get("CopilotMood", "AGGRESSIVE"),
                VoiceCueId=int(parsed.get("VoiceCueId", 1))
            )
        else:
            logger.warning(f"Groq API error {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        logger.warning(f"Failed to query Groq LLM: {e}")
        return None


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "groq_configured": bool(GROQ_API_KEY),
        "model": GROQ_MODEL
    }

@app.post("/api/v1/copilot/tactics")
async def get_copilot_tactics(payload: Dict[str, Any] = Body(default={})):
    """
    Receives vehicle telemetry from Unreal Engine UCarAIAgentComponent or Blueprint.
    Tolerates any casing (PascalCase, camelCase, snake_case) and missing parameters,
    returning HTTP 200 with both UStruct-compatible fields and tactical directives.
    """
    t_start = time.time()

    # Tolerant parameter extraction
    def get_float(keys, default_val=0.0):
        for k in keys:
            if k in payload and payload[k] is not None:
                try:
                    return float(payload[k])
                except (ValueError, TypeError):
                    pass
        return default_val

    def get_int(keys, default_val=1):
        for k in keys:
            if k in payload and payload[k] is not None:
                try:
                    return int(payload[k])
                except (ValueError, TypeError):
                    pass
        return default_val

    def get_str(keys, default_val=""):
        for k in keys:
            if k in payload and payload[k] is not None:
                return str(payload[k])
        return default_val

    speed = get_float(["SpeedKmh", "speed_kmh", "Speed", "speed", "velocity"], 0.0)
    dist_ahead = get_float(["DistanceToRivalAhead", "distance_to_rival_ahead", "distance_ahead", "distance_to_leader"], -1.0)
    dist_behind = get_float(["DistanceToRivalBehind", "distance_to_rival_behind", "distance_to_pursuer", "distance_behind", "pursuer_distance"], -1.0)
    nitro = get_float(["NitroPercentage", "nitro_percentage", "Nitro", "nitro"], 100.0)
    gear = get_int(["CurrentGear", "current_gear", "Gear", "gear"], 1)
    sector = get_str(["TrackSector", "track_sector", "Sector", "sector"], "Sector_1")
    lateral_g = get_float(["LateralGForce", "lateral_g_force", "LateralG", "lateral_g"], 0.0)

    telemetry = VehicleTelemetry(
        SpeedKmh=speed,
        DistanceToRivalAhead=dist_ahead,
        DistanceToRivalBehind=dist_behind,
        NitroPercentage=nitro,
        CurrentGear=gear,
        TrackSector=sector,
        LateralGForce=lateral_g
    )

    # Attempt LLM inference
    order = call_groq_llm(telemetry.model_dump())

    # Fallback to local heuristic engine if LLM is offline or timed out
    if not order:
        order = generate_heuristic_fallback(telemetry)

    elapsed_ms = (time.time() - t_start) * 1000.0
    logger.info(f"[/tactics] {speed:.0f} km/h | DistBehind: {dist_behind:.1f}m | Order: '{order.AdviceMessage}' ({order.TacticalAction}) in {elapsed_ms:.1f}ms")

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            # Direct UStruct compatibility for FJsonObjectConverter::JsonObjectStringToUStruct
            "AdviceMessage": order.AdviceMessage,
            "TacticalAction": order.TacticalAction,
            "SuggestedSpeed": order.SuggestedSpeed,
            "CopilotMood": order.CopilotMood,
            "VoiceCueId": order.VoiceCueId,
            # Snake_case compatibility
            "advice_message": order.AdviceMessage,
            "tactical_action": order.TacticalAction,
            "suggested_speed": order.SuggestedSpeed,
            "copilot_mood": order.CopilotMood,
            "voice_cue_id": order.VoiceCueId,
            # Structured directives dictionary
            "directives": {
                "action": order.TacticalAction,
                "message": order.AdviceMessage,
                "suggested_speed": order.SuggestedSpeed,
                "mood": order.CopilotMood,
                "voice_cue_id": order.VoiceCueId
            }
        }
    )

@app.post("/api/v1/copilot/tactics/alert")
async def handle_immediate_alert(payload: Dict[str, Any] = Body(default={})):
    """
    High-priority immediate event handler (tolerant to any casing).
    """
    event_type = str(payload.get("EventType") or payload.get("event_type") or payload.get("event") or "ALERT")
    event_details = str(payload.get("EventDetails") or payload.get("event_details") or payload.get("details") or "")
    try:
        speed = float(payload.get("SpeedKmh") or payload.get("speed_kmh") or payload.get("speed") or 0.0)
    except (ValueError, TypeError):
        speed = 0.0

    logger.info(f"[/alert] Event: {event_type} - {event_details}")

    if "CRASH" in event_type.upper():
        order = CopilotTacticalOrder(
            AdviceMessage="¡Cuidado con los escombros! ¡Esquiva por la derecha!",
            TacticalAction="DEFEND_RIGHT",
            SuggestedSpeed=max(speed - 30.0, 60.0),
            CopilotMood="URGENT",
            VoiceCueId=4
        )
    elif "FINAL_LAP" in event_type.upper():
        order = CopilotTacticalOrder(
            AdviceMessage="¡Última vuelta! ¡Gasta todo el Nitro y no sueltes la punta!",
            TacticalAction="USE_NITRO",
            SuggestedSpeed=210.0,
            CopilotMood="AGGRESSIVE",
            VoiceCueId=1
        )
    else:
        order = CopilotTacticalOrder(
            AdviceMessage="¡Alerta de carrera! ¡Mantén el control!",
            TacticalAction="FULL_THROTTLE",
            SuggestedSpeed=speed,
            CopilotMood="URGENT",
            VoiceCueId=5
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "AdviceMessage": order.AdviceMessage,
            "TacticalAction": order.TacticalAction,
            "SuggestedSpeed": order.SuggestedSpeed,
            "CopilotMood": order.CopilotMood,
            "VoiceCueId": order.VoiceCueId,
            "directives": {
                "action": order.TacticalAction,
                "message": order.AdviceMessage,
                "suggested_speed": order.SuggestedSpeed,
                "mood": order.CopilotMood,
                "voice_cue_id": order.VoiceCueId
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("copilot_server:app", host="0.0.0.0", port=port, reload=True)

