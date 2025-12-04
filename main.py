"""
April Agent - FastAPI Server
============================

Multi-tenant ADK agent server with user credential injection.

Endpoints:
- POST /chat - Send message to April agent (JSON response)
- POST /run_sse - Send message to April agent (SSE streaming)
- POST /sessions - Create new session with user credentials
- GET /sessions/{session_id} - Get session info
- GET /health - Health check

Multi-Tenancy Flow:
1. Client creates session with user_id via POST /sessions
2. Server looks up user credentials and stores in session state
3. Client sends messages via POST /chat or /run_sse
4. Agent's header_provider reads credentials from state
5. MCP tools use user-specific authentication

Environment Variables Required:
- GOOGLE_API_KEY or GOOGLE_GENAI_API_KEY - Gemini API key
- GHL_MCP_URL - GoHighLevel MCP server URL (optional, has default)
- PIPEDREAM_MCP_URL - Pipedream MCP server URL (optional, has default)
- PIPEDREAM_API_KEY - Pipedream master API key

For development, also set:
- GHL_PIT_TOKEN - Default GHL token for all users
- GHL_LOCATION_ID - Default GHL location for all users
- PIPEDREAM_USER_ID - Default Pipedream user for all users
"""

import os
import uuid
import json
from pathlib import Path
from typing import Optional, List, AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.genai import types

from agent import root_agent
from config import get_user_credentials, validate_user_credentials

# Load .env from this package's directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


# =============================================================================
# CONFIGURATION
# =============================================================================

APP_NAME = "april_agent"
PORT = int(os.environ.get("PORT", 8001))

# Database URL for persistent sessions (optional)
SESSION_DB_URL = os.environ.get("APRIL_SESSION_DB_URL")

# CORS origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    # Add your production frontend URLs here
]


# =============================================================================
# SESSION SERVICE
# =============================================================================

if SESSION_DB_URL:
    session_service = DatabaseSessionService(db_url=SESSION_DB_URL)
    print(f"✅ Using DatabaseSessionService (PostgreSQL)")
else:
    session_service = InMemorySessionService()
    print("⚠️  Using InMemorySessionService (non-persistent)")


# =============================================================================
# RUNNER
# =============================================================================

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class CreateSessionRequest(BaseModel):
    """Request to create a new session with user credentials."""
    user_id: str
    session_id: Optional[str] = None  # Optional custom session ID


class CreateSessionResponse(BaseModel):
    """Response after creating a session."""
    session_id: str
    user_id: str
    credentials_loaded: bool
    message: str


class ChatRequest(BaseModel):
    """Request to send a message to the agent."""
    message: str
    user_id: str
    session_id: str


class ToolCallInfo(BaseModel):
    """Information about a tool call."""
    name: str
    status: str  # "calling" or "complete"


class ChatResponse(BaseModel):
    """Response from the agent."""
    response: str
    session_id: str
    events_count: int
    tool_calls: List[ToolCallInfo] = []


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agent: str
    session_service: str


# =============================================================================
# FASTAPI APP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    print(f"🚀 April Agent starting on port {PORT}")
    print(f"   Agent: {root_agent.name}")
    print(f"   Model: {root_agent.model}")
    yield
    print("👋 April Agent shutting down")


app = FastAPI(
    title="April Agent API",
    description="Multi-tenant Executive Assistant powered by Google ADK",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent=root_agent.name,
        session_service="database" if SESSION_DB_URL else "in-memory",
    )


@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new session with user credentials loaded into state.
    
    This is the multi-tenancy entry point:
    1. Look up user credentials from database
    2. Create session with credentials in state
    3. Return session_id for subsequent chat requests
    """
    user_id = request.user_id
    session_id = request.session_id or str(uuid.uuid4())
    
    # Look up user credentials
    credentials = get_user_credentials(user_id)
    
    if not validate_user_credentials(credentials):
        # Still create session, but without credentials
        # Agent will handle missing credentials gracefully
        initial_state = {
            "user:id": user_id,
            "user:credentials_loaded": False,
        }
        credentials_loaded = False
        message = "Session created but credentials not found. User needs to connect their accounts."
    else:
        # Store credentials in user-scoped state
        initial_state = {
            "user:id": user_id,
            "user:credentials_loaded": True,
            "user:ghl_pit_token": credentials["ghl_pit_token"],
            "user:ghl_location_id": credentials["ghl_location_id"],
            "user:pipedream_user_id": credentials["pipedream_user_id"],
        }
        credentials_loaded = True
        message = "Session created with credentials loaded."
    
    # Create the session
    try:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=initial_state,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )
    
    return CreateSessionResponse(
        session_id=session_id,
        user_id=user_id,
        credentials_loaded=credentials_loaded,
        message=message,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to April agent.
    
    Requires an existing session created via POST /sessions.
    The session contains user credentials that the agent uses
    for MCP tool authentication.
    """
    user_id = request.user_id
    session_id = request.session_id
    message_text = request.message
    
    # Verify session exists
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found. Create one first via POST /sessions"
        )
    
    # Create user message content
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=message_text)]
    )
    
    # Run the agent
    response_text = ""
    events_count = 0
    tool_calls = []
    seen_tools = set()
    
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            events_count += 1
            
            # Capture tool calls from function_call events
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Check for function calls
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_name = part.function_call.name
                        if tool_name and tool_name not in seen_tools:
                            seen_tools.add(tool_name)
                            tool_calls.append(ToolCallInfo(
                                name=tool_name,
                                status="complete"
                            ))
                    
                    # Check for function responses (also indicates tool was called)
                    if hasattr(part, 'function_response') and part.function_response:
                        tool_name = part.function_response.name
                        if tool_name and tool_name not in seen_tools:
                            seen_tools.add(tool_name)
                            tool_calls.append(ToolCallInfo(
                                name=tool_name,
                                status="complete"
                            ))
            
            # Collect final response text
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}"
        )
    
    if not response_text:
        response_text = "I couldn't generate a response. Please try again."
    
    return ChatResponse(
        response=response_text,
        session_id=session_id,
        events_count=events_count,
        tool_calls=tool_calls,
    )


# =============================================================================
# SSE STREAMING ENDPOINT - REAL-TIME EVENTS
# =============================================================================

class SSERequest(BaseModel):
    """Request for SSE streaming endpoint."""
    message: str
    user_id: str
    session_id: str


def serialize_event_for_sse(event) -> dict:
    """Convert an ADK event to a JSON-serializable dict for SSE streaming."""
    result = {
        "author": getattr(event, "author", "agent"),
        "partial": getattr(event, "partial", False),
        "is_final": event.is_final_response() if hasattr(event, "is_final_response") else False,
    }
    
    # Extract content parts
    if event.content and event.content.parts:
        parts = []
        for part in event.content.parts:
            part_dict = {}
            
            # Handle function calls
            if hasattr(part, 'function_call') and part.function_call:
                fc = part.function_call
                part_dict["functionCall"] = {
                    "name": fc.name,
                    "args": dict(fc.args) if hasattr(fc.args, "__iter__") and not isinstance(fc.args, str) else fc.args
                }
            
            # Handle function responses
            elif hasattr(part, 'function_response') and part.function_response:
                fr = part.function_response
                # Safely serialize the response
                response_data = fr.response
                if hasattr(response_data, "model_dump"):
                    response_data = response_data.model_dump()
                elif hasattr(response_data, "__dict__"):
                    response_data = response_data.__dict__
                
                part_dict["functionResponse"] = {
                    "name": fr.name,
                    "response": response_data
                }
            
            # Handle text
            elif hasattr(part, 'text') and part.text:
                part_dict["text"] = part.text
            
            if part_dict:
                parts.append(part_dict)
        
        result["content"] = {"parts": parts}
    
    return result


async def generate_sse_events(user_id: str, session_id: str, message: str) -> AsyncGenerator[str, None]:
    """Generate SSE events as the agent processes the request."""
    
    # Create user message content
    user_message = types.Content(
        role="user",
        parts=[types.Part(text=message)]
    )
    
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            try:
                event_data = serialize_event_for_sse(event)
                yield f"data: {json.dumps(event_data)}\n\n"
            except Exception as e:
                # Log but don't crash on serialization errors
                print(f"Warning: Could not serialize event: {e}")
                continue
                
    except Exception as e:
        error_data = {
            "error": True,
            "message": str(e),
            "content": {"parts": [{"text": f"Error: {str(e)}"}]}
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@app.post("/run_sse")
async def run_sse(request: SSERequest):
    """
    SSE streaming endpoint for real-time agent events.
    
    Streams events as they happen:
    - function_call: When the agent calls a tool
    - function_response: When a tool returns results  
    - text/text_partial: Agent's response text (streaming)
    
    This provides a much better UX than waiting for the full response.
    """
    user_id = request.user_id
    session_id = request.session_id
    message = request.message
    
    # Verify session exists
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Create one first via POST /sessions"
        )
    
    return StreamingResponse(
        generate_sse_events(user_id, session_id, message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@app.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    user_id: str = Query(..., description="User ID for the session"),
):
    """Get session information."""
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Don't expose sensitive credentials in response
    safe_state = {
        k: v for k, v in session.state.items()
        if not k.endswith("_token") and not k.endswith("_key")
    }
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "state": safe_state,
        "events_count": len(session.events),
        "last_update": session.last_update_time,
    }


@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Query(..., description="User ID for the session"),
):
    """Delete a session."""
    try:
        await session_service.delete_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        return {"status": "deleted", "session_id": session_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

