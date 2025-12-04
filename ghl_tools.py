"""
GoHighLevel Direct API Tools - ALL 21 MCP TOOLS
================================================

Complete implementation of all GHL MCP tools:
1. calendars_get-calendar-events
2. calendars_get-appointment-notes
3. contacts_get-all-tasks
4. contacts_add-tags
5. contacts_remove-tags
6. contacts_get-contact
7. contacts_update-contact
8. contacts_upsert-contact
9. contacts_create-contact
10. contacts_get-contacts
11. conversations_search-conversation
12. conversations_get-messages
13. conversations_send-a-new-message
14. locations_get-location
15. locations_get-custom-fields
16. opportunities_search-opportunity
17. opportunities_get-pipelines
18. opportunities_get-opportunity
19. opportunities_update-opportunity
20. payments_get-order-by-id
21. payments_list-transactions
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from google.adk.tools import ToolContext

# GHL MCP API endpoint
GHL_API_URL = "https://services.leadconnectorhq.com/mcp/"


async def _call_ghl_api(
    tool_context: ToolContext,
    tool_name: str,
    input_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Internal helper to call GHL MCP API with JSON-RPC 2.0 format.
    """
    state = tool_context.state
    
    pit_token = state.get("user:ghl_pit_token")
    location_id = state.get("user:ghl_location_id")
    
    if not pit_token or not location_id:
        return {
            "status": "error",
            "message": "🔐 GHL not connected. Please link your GoHighLevel account first."
        }
    
    headers = {
        "Authorization": f"Bearer {pit_token}",
        "locationId": location_id,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    
    # JSON-RPC 2.0 format
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": input_data
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GHL_API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                text = response.text
                # Parse SSE response
                if text.startswith("event:"):
                    for line in text.split("\n"):
                        if line.startswith("data:"):
                            json_str = line[5:].strip()
                            try:
                                data = json.loads(json_str)
                                if "result" in data and "content" in data["result"]:
                                    content = data["result"]["content"]
                                    if content and len(content) > 0:
                                        text_content = content[0].get("text", "")
                                        try:
                                            inner_data = json.loads(text_content)
                                            if "content" in inner_data:
                                                inner_content = inner_data["content"]
                                                if inner_content and len(inner_content) > 0:
                                                    final_text = inner_content[0].get("text", "")
                                                    final_data = json.loads(final_text)
                                                    return {"status": "success", "data": final_data.get("data", final_data)}
                                        except json.JSONDecodeError:
                                            pass
                                        return {"status": "success", "data": text_content}
                                return {"status": "success", "data": data}
                            except json.JSONDecodeError:
                                pass
                    return {"status": "success", "raw": text}
                else:
                    return {"status": "success", "data": response.json()}
            elif response.status_code == 401:
                return {"status": "error", "message": "🔒 GHL authentication expired. Please reconnect."}
            elif response.status_code == 403:
                return {"status": "error", "message": "⛔ Permission denied. Check your GHL integration scopes."}
            else:
                return {"status": "error", "message": f"GHL returned {response.status_code}", "details": response.text[:300]}
                
    except httpx.TimeoutException:
        return {"status": "error", "message": "⏱️ GHL took too long. Try again!"}
    except Exception as e:
        return {"status": "error", "message": f"Connection error: {str(e)}"}


# =============================================================================
# 📅 CALENDAR TOOLS (2)
# =============================================================================

async def ghl_get_calendar_events(
    start_date: str,
    end_date: str,
    calendar_id: Optional[str] = None,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Get calendar events from GoHighLevel for a date range.
    
    Use this to check schedules, upcoming meetings, and appointments.
    Provide userId, calendarId, or groupId to filter results.
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        calendar_id: Optional specific calendar ID
        user_id: Optional user ID to filter by
        group_id: Optional group ID to filter by
        
    Returns:
        List of calendar events with times, titles, and attendees
    """
    input_data = {"startDate": start_date, "endDate": end_date}
    if calendar_id:
        input_data["calendarId"] = calendar_id
    if user_id:
        input_data["userId"] = user_id
    if group_id:
        input_data["groupId"] = group_id
    
    return await _call_ghl_api(tool_context, "calendars_get-calendar-events", input_data)


async def ghl_get_appointment_notes(
    appointment_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get notes for a specific appointment in GoHighLevel.
    
    Use this to retrieve meeting notes, discussion points, or follow-up items.
    
    Args:
        appointment_id: The appointment/event ID
        
    Returns:
        Notes attached to the appointment
    """
    return await _call_ghl_api(tool_context, "calendars_get-appointment-notes", {"appointmentId": appointment_id})


# =============================================================================
# 👥 CONTACT TOOLS (8)
# =============================================================================

async def ghl_get_contact(
    contact_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get full contact details from GoHighLevel.
    
    Retrieves name, email, phone, tags, custom fields, and more.
    
    Args:
        contact_id: The GHL contact ID
        
    Returns:
        Complete contact profile with all fields
    """
    return await _call_ghl_api(tool_context, "contacts_get-contact", {"contactId": contact_id})


async def ghl_get_contacts(
    query: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    limit: int = 20,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search and list contacts in GoHighLevel CRM.
    
    USE THIS TOOL when user asks to find/search contacts by name!
    
    Examples:
    - "Find John" → use query="John"
    - "Search for Sarah Smith" → use first_name="Sarah", last_name="Smith"
    - "Find contacts with email @gmail" → use email="gmail"
    
    Args:
        query: General search term - searches across name, email, phone
        email: Search by email address (partial match works)
        phone: Search by phone number
        first_name: Search by first name specifically
        last_name: Search by last name specifically
        limit: Max results to return (default 20)
        
    Returns:
        List of matching contacts with name, email, phone, tags
    """
    input_data = {"limit": limit}
    if query:
        input_data["query"] = query
    if email:
        input_data["email"] = email
    if phone:
        input_data["phone"] = phone
    if first_name:
        input_data["firstName"] = first_name
    if last_name:
        input_data["lastName"] = last_name
    
    return await _call_ghl_api(tool_context, "contacts_get-contacts", input_data)


async def ghl_create_contact(
    first_name: str,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company_name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Create a new contact in GoHighLevel.
    
    Add a new lead or contact to your CRM.
    
    Args:
        first_name: Contact's first name (required)
        last_name: Contact's last name
        email: Contact's email address
        phone: Contact's phone number
        company_name: Company/business name
        tags: List of tags to apply
        
    Returns:
        Created contact with ID
    """
    input_data = {"firstName": first_name}
    if last_name:
        input_data["lastName"] = last_name
    if email:
        input_data["email"] = email
    if phone:
        input_data["phone"] = phone
    if company_name:
        input_data["companyName"] = company_name
    if tags:
        input_data["tags"] = tags
    
    return await _call_ghl_api(tool_context, "contacts_create-contact", input_data)


async def ghl_update_contact(
    contact_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company_name: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Update an existing contact in GoHighLevel.
    
    Modify contact details like name, email, phone, or company.
    
    Args:
        contact_id: The contact ID to update (required)
        first_name: New first name
        last_name: New last name
        email: New email address
        phone: New phone number
        company_name: New company name
        
    Returns:
        Updated contact details
    """
    input_data = {"contactId": contact_id}
    if first_name:
        input_data["firstName"] = first_name
    if last_name:
        input_data["lastName"] = last_name
    if email:
        input_data["email"] = email
    if phone:
        input_data["phone"] = phone
    if company_name:
        input_data["companyName"] = company_name
    
    return await _call_ghl_api(tool_context, "contacts_update-contact", input_data)


async def ghl_upsert_contact(
    email: Optional[str] = None,
    phone: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company_name: Optional[str] = None,
    tags: Optional[List[str]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Create or update a contact in GoHighLevel (upsert).
    
    If contact exists (by email/phone), updates it. Otherwise creates new.
    Perfect for syncing contacts from external sources.
    
    Args:
        email: Contact's email (used for matching)
        phone: Contact's phone (used for matching)
        first_name: Contact's first name
        last_name: Contact's last name
        company_name: Company name
        tags: Tags to apply
        
    Returns:
        Contact details (created or updated)
    """
    input_data = {}
    if email:
        input_data["email"] = email
    if phone:
        input_data["phone"] = phone
    if first_name:
        input_data["firstName"] = first_name
    if last_name:
        input_data["lastName"] = last_name
    if company_name:
        input_data["companyName"] = company_name
    if tags:
        input_data["tags"] = tags
    
    return await _call_ghl_api(tool_context, "contacts_upsert-contact", input_data)


async def ghl_add_tags(
    contact_id: str,
    tags: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Add tags to a contact in GoHighLevel.
    
    Tags help organize and segment contacts for campaigns and workflows.
    
    Args:
        contact_id: The contact ID
        tags: List of tag names to add
        
    Returns:
        Confirmation of tags added
    """
    return await _call_ghl_api(tool_context, "contacts_add-tags", {"contactId": contact_id, "tags": tags})


async def ghl_remove_tags(
    contact_id: str,
    tags: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Remove tags from a contact in GoHighLevel.
    
    Args:
        contact_id: The contact ID
        tags: List of tag names to remove
        
    Returns:
        Confirmation of tags removed
    """
    return await _call_ghl_api(tool_context, "contacts_remove-tags", {"contactId": contact_id, "tags": tags})


async def ghl_get_contact_tasks(
    contact_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get all tasks for a contact in GoHighLevel.
    
    Retrieves to-dos, follow-ups, and action items linked to a contact.
    
    Args:
        contact_id: The contact ID
        
    Returns:
        List of tasks with due dates and status
    """
    return await _call_ghl_api(tool_context, "contacts_get-all-tasks", {"contactId": contact_id})


# =============================================================================
# 💬 CONVERSATION TOOLS (3)
# =============================================================================

async def ghl_search_conversations(
    contact_id: Optional[str] = None,
    query: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search conversations in GoHighLevel.
    
    Find SMS, email, and other message threads.
    
    Args:
        contact_id: Filter by contact ID
        query: Search text
        status: Filter by status (all, read, unread)
        limit: Max results
        
    Returns:
        List of conversation threads
    """
    input_data = {"limit": limit}
    if contact_id:
        input_data["contactId"] = contact_id
    if query:
        input_data["query"] = query
    if status:
        input_data["status"] = status
    
    return await _call_ghl_api(tool_context, "conversations_search-conversation", input_data)


async def ghl_get_messages(
    conversation_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get messages from a conversation thread in GoHighLevel.
    
    Retrieves the full message history for a conversation.
    
    Args:
        conversation_id: The conversation ID
        
    Returns:
        List of messages with timestamps and content
    """
    return await _call_ghl_api(tool_context, "conversations_get-messages", {"conversationId": conversation_id})


async def ghl_send_message(
    contact_id: str,
    message: str,
    message_type: str = "SMS",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Send a message to a contact via GoHighLevel.
    
    Send SMS texts or emails directly to contacts.
    
    Args:
        contact_id: The contact ID to message
        message: The message content
        message_type: "SMS" for text or "Email" for email
        
    Returns:
        Confirmation of message sent
    """
    return await _call_ghl_api(
        tool_context,
        "conversations_send-a-new-message",
        {"contactId": contact_id, "message": message, "type": message_type}
    )


# =============================================================================
# 🎯 OPPORTUNITY/PIPELINE TOOLS (4)
# =============================================================================

async def ghl_get_pipelines(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get all sales pipelines from GoHighLevel.
    
    Retrieves pipeline names, stages, and structure for your deals.
    
    Returns:
        List of pipelines with their stages
    """
    return await _call_ghl_api(tool_context, "opportunities_get-pipelines", {})


async def ghl_search_opportunities(
    pipeline_id: Optional[str] = None,
    stage_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    status: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 20,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Search opportunities (deals) in GoHighLevel.
    
    Find deals by pipeline, stage, contact, or status.
    
    Args:
        pipeline_id: Filter by pipeline
        stage_id: Filter by stage
        contact_id: Filter by contact
        status: open, won, lost, abandoned
        query: Search text
        limit: Max results
        
    Returns:
        List of matching opportunities
    """
    input_data = {"limit": limit}
    if pipeline_id:
        input_data["pipelineId"] = pipeline_id
    if stage_id:
        input_data["stageId"] = stage_id
    if contact_id:
        input_data["contactId"] = contact_id
    if status:
        input_data["status"] = status
    if query:
        input_data["query"] = query
    
    return await _call_ghl_api(tool_context, "opportunities_search-opportunity", input_data)


async def ghl_get_opportunity(
    opportunity_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get full opportunity (deal) details from GoHighLevel.
    
    Retrieves deal value, stage, contact, and all custom fields.
    
    Args:
        opportunity_id: The opportunity ID
        
    Returns:
        Complete opportunity details
    """
    return await _call_ghl_api(tool_context, "opportunities_get-opportunity", {"opportunityId": opportunity_id})


async def ghl_update_opportunity(
    opportunity_id: str,
    stage_id: Optional[str] = None,
    status: Optional[str] = None,
    monetary_value: Optional[float] = None,
    name: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Update an opportunity (deal) in GoHighLevel.
    
    Move deals through stages, update values, or change status.
    
    Args:
        opportunity_id: The opportunity ID (required)
        stage_id: Move to this stage
        status: Set status (open, won, lost, abandoned)
        monetary_value: Update deal value
        name: Update opportunity name
        
    Returns:
        Updated opportunity details
    """
    input_data = {"opportunityId": opportunity_id}
    if stage_id:
        input_data["stageId"] = stage_id
    if status:
        input_data["status"] = status
    if monetary_value is not None:
        input_data["monetaryValue"] = monetary_value
    if name:
        input_data["name"] = name
    
    return await _call_ghl_api(tool_context, "opportunities_update-opportunity", input_data)


# =============================================================================
# 📍 LOCATION TOOLS (2)
# =============================================================================

async def ghl_get_location(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get current location details from GoHighLevel.
    
    Returns business info for the connected sub-account.
    
    Returns:
        Location name, address, phone, website, timezone
    """
    location_id = tool_context.state.get("user:ghl_location_id")
    return await _call_ghl_api(tool_context, "locations_get-location", {"locationId": location_id})


async def ghl_get_custom_fields(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get custom field definitions from GoHighLevel.
    
    Retrieves all custom fields configured for contacts and opportunities.
    
    Returns:
        List of custom fields with names, types, and options
    """
    return await _call_ghl_api(tool_context, "locations_get-custom-fields", {})


# =============================================================================
# 💳 PAYMENT TOOLS (2)
# =============================================================================

async def ghl_get_order(
    order_id: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Get order details from GoHighLevel.
    
    Retrieves payment order information including items, amounts, and status.
    
    Args:
        order_id: The order ID
        
    Returns:
        Order details with line items and payment status
    """
    return await _call_ghl_api(tool_context, "payments_get-order-by-id", {"orderId": order_id})


async def ghl_list_transactions(
    contact_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    List payment transactions from GoHighLevel.
    
    Retrieves transaction history with amounts and statuses.
    
    Args:
        contact_id: Filter by contact
        start_date: Filter from date (YYYY-MM-DD)
        end_date: Filter to date (YYYY-MM-DD)
        limit: Max results
        
    Returns:
        Paginated list of transactions
    """
    input_data = {"limit": limit}
    if contact_id:
        input_data["contactId"] = contact_id
    if start_date:
        input_data["startDate"] = start_date
    if end_date:
        input_data["endDate"] = end_date
    
    return await _call_ghl_api(tool_context, "payments_list-transactions", input_data)


# =============================================================================
# EXPORT ALL 21 TOOLS
# =============================================================================

GHL_TOOLS = [
    # Calendar (2)
    ghl_get_calendar_events,
    ghl_get_appointment_notes,
    # Contacts (8)
    ghl_get_contact,
    ghl_get_contacts,
    ghl_create_contact,
    ghl_update_contact,
    ghl_upsert_contact,
    ghl_add_tags,
    ghl_remove_tags,
    ghl_get_contact_tasks,
    # Conversations (3)
    ghl_search_conversations,
    ghl_get_messages,
    ghl_send_message,
    # Opportunities (4)
    ghl_get_pipelines,
    ghl_search_opportunities,
    ghl_get_opportunity,
    ghl_update_opportunity,
    # Location (2)
    ghl_get_location,
    ghl_get_custom_fields,
    # Payments (2)
    ghl_get_order,
    ghl_list_transactions,
]
