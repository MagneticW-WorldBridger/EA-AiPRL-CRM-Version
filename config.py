"""
User Credential Storage for April Agent
========================================

This module handles retrieval of user-specific API credentials.
In production, this should connect to Firestore or your database.

Each user has:
- ghl_pit_token: GoHighLevel Private Integration Token
- ghl_location_id: GoHighLevel Location ID
- pipedream_user_id: Pipedream Connect external user ID

The credentials are stored per user_id and retrieved at runtime
to inject into MCP server headers.
"""

import os
from pathlib import Path
from typing import Optional, TypedDict
from dotenv import load_dotenv

# Load .env from this package's directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class UserCredentials(TypedDict):
    """Type definition for user credentials."""
    ghl_pit_token: str
    ghl_location_id: str
    pipedream_user_id: str


# =============================================================================
# PRODUCTION: Replace this with Firestore/Database lookup
# =============================================================================

def get_user_credentials(user_id: str) -> Optional[UserCredentials]:
    """
    Retrieve user-specific credentials for MCP server authentication.
    
    In production, this should:
    1. Query Firestore: db.collection('users').doc(user_id).get()
    2. Return the credentials from the document
    3. Handle missing users gracefully
    
    Args:
        user_id: The unique identifier for the user/tenant
        
    Returns:
        UserCredentials dict or None if user not found
    """
    # For now, check environment variables for a single default user
    # In production: replace with database lookup
    
    ghl_pit = os.getenv("GHL_PIT_TOKEN")
    ghl_location = os.getenv("GHL_LOCATION_ID")
    pipedream_user = os.getenv("PIPEDREAM_USER_ID")
    
    # If env vars are set, return them for any user_id (dev mode)
    if ghl_pit and ghl_location and pipedream_user:
        return UserCredentials(
            ghl_pit_token=ghl_pit,
            ghl_location_id=ghl_location,
            pipedream_user_id=pipedream_user,
        )
    
    # In production, you would do:
    # from google.cloud import firestore
    # db = firestore.Client()
    # doc = db.collection('april_users').document(user_id).get()
    # if doc.exists:
    #     data = doc.to_dict()
    #     return UserCredentials(
    #         ghl_pit_token=data['ghl_pit_token'],
    #         ghl_location_id=data['ghl_location_id'],
    #         pipedream_user_id=data['pipedream_user_id'],
    #     )
    
    return None


def validate_user_credentials(creds: Optional[UserCredentials]) -> bool:
    """Check if credentials are complete and valid."""
    if not creds:
        return False
    return all([
        creds.get("ghl_pit_token"),
        creds.get("ghl_location_id"),
        creds.get("pipedream_user_id"),
    ])


# =============================================================================
# MCP Server URLs
# =============================================================================

# GoHighLevel MCP Server
GHL_MCP_URL = os.getenv(
    "GHL_MCP_URL",
    "https://services.leadconnectorhq.com/mcp/"
)

# Pipedream MCP Server (SSE endpoint)
PIPEDREAM_MCP_URL = os.getenv(
    "PIPEDREAM_MCP_URL",
    "https://mcp.pipedream.com/sse"
)

# Pipedream API Key (master key for the Pipedream account)
PIPEDREAM_API_KEY = os.getenv("PIPEDREAM_API_KEY")

