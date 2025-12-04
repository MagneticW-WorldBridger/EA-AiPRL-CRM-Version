# 🚀 April Agent - Executive Assistant

<div align="center">

**INTERNAL USE ONLY - AiPRL EMPLOYEES**

*The Revolutionary AI Executive Assistant powered by Google ADK + GoHighLevel MCP*

**Version 2.0.0** | December 2024 | **🎉 MAJOR RELEASE**

[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-purple)](https://railway.app)
[![Google ADK](https://img.shields.io/badge/Powered%20by-Google%20ADK-blue)](https://google.github.io/adk-docs/)
[![GoHighLevel](https://img.shields.io/badge/CRM-GoHighLevel-orange)](https://gohighlevel.com)

</div>

---

## 🎯 What is April?

**April** is AiPRL's flagship AI Executive Assistant that connects directly to GoHighLevel CRM. She can manage contacts, check calendars, send messages, track deals, and more - all through natural conversation.

> **"Hey April, what meetings do I have this week?"**  
> *→ April checks the date, queries your calendar, and tells you instantly.*

> **"Find Derek Dicks"**  
> *→ April searches your CRM and shows contact details with email and phone.*

> **"Show my open deals"**  
> *→ April queries your pipeline and lists opportunities with values.*

---

## 🏆 V2.0 Achievement Unlocked: Proper MCP Integration!

### What We Built

We successfully integrated GoHighLevel's **non-standard MCP server** with Google's Agent Development Kit. This was NOT trivial - GHL's MCP uses a **hybrid protocol** that doesn't follow the standard:

| Standard MCP | GHL's MCP (Hybrid) |
|--------------|-------------------|
| WebSocket or SSE connection | HTTP POST requests |
| Streaming responses | SSE event stream in response body |
| Session initialization | No session - stateless calls |
| Standard tool schemas | JSON Schema with custom naming |

### Our Solution: Custom `GHLTool` Class

We created a proper ADK `BaseToolset` implementation that:

1. ✅ **Handles the hybrid protocol** - JSON-RPC 2.0 POST → SSE response parsing
2. ✅ **Exposes 36 tools** to the LLM with proper parameter schemas
3. ✅ **Auto-converts timestamps** to strings (GHL API requirement)
4. ✅ **Follows ADK patterns** - Mirrors `McpTool` from the official SDK
5. ✅ **Zero config needed** - Just set env vars and it works!

```python
# It's this simple now!
from ghl_toolset import GHLToolset

ghl_toolset = GHLToolset()  # Reads from env vars
agent = Agent(tools=[ghl_toolset, ...])
```

---

## 📊 All 36 GHL Tools (Yes, 36!)

April now has access to **every tool** GoHighLevel's MCP server provides:

### 📅 Calendar (2 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_calendars_get_calendar_events` | Get meetings by date range |
| `ghl_calendars_get_appointment_notes` | Get notes from appointments |

### 👥 Contacts (8 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_contacts_get_contacts` | Search contacts by name/email/phone |
| `ghl_contacts_get_contact` | Get single contact details |
| `ghl_contacts_create_contact` | Add new contact |
| `ghl_contacts_update_contact` | Update contact info |
| `ghl_contacts_upsert_contact` | Create or update (smart sync) |
| `ghl_contacts_add_tags` | Add tags to contact |
| `ghl_contacts_remove_tags` | Remove tags |
| `ghl_contacts_get_all_tasks` | Get contact's tasks |

### 💬 Conversations (3 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_conversations_search_conversation` | Find message threads |
| `ghl_conversations_get_messages` | Get message history |
| `ghl_conversations_send_a_new_message` | Send SMS/Email/WhatsApp |

### 💰 Opportunities (4 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_opportunities_get_pipelines` | List all pipelines & stages |
| `ghl_opportunities_search_opportunity` | Search deals |
| `ghl_opportunities_get_opportunity` | Get deal details |
| `ghl_opportunities_update_opportunity` | Update deal stage/value |

### 📍 Location (2 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_locations_get_location` | Get business info |
| `ghl_locations_get_custom_fields` | List custom field definitions |

### 💳 Payments (2 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_payments_get_order_by_id` | Get order details |
| `ghl_payments_list_transactions` | List payment history |

### 📧 Emails (2 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_emails_fetch_template` | Get email templates |
| `ghl_emails_create_template` | Create new template |

### 📝 Blogs (7 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_blogs_get_blogs` | List all blogs |
| `ghl_blogs_get_blog_post` | Get blog posts |
| `ghl_blogs_create_blog_post` | Create new post |
| `ghl_blogs_update_blog_post` | Update existing post |
| `ghl_blogs_check_url_slug_exists` | Check URL availability |
| `ghl_blogs_get_all_blog_authors_by_location` | List authors |
| `ghl_blogs_get_all_categories_by_location` | List categories |

### 📱 Social Media (6 tools)
| Tool | What It Does |
|------|-------------|
| `ghl_socialmediaposting_get_account` | Get connected accounts |
| `ghl_socialmediaposting_get_posts` | List scheduled posts |
| `ghl_socialmediaposting_get_post` | Get single post |
| `ghl_socialmediaposting_create_post` | Schedule new post |
| `ghl_socialmediaposting_edit_post` | Edit scheduled post |
| `ghl_socialmediaposting_get_social_media_statistics` | Get analytics |

### ⏰ Special Tools
| Tool | What It Does |
|------|-------------|
| `get_current_datetime` | Get today's date + week timestamps for calendar queries |

---

## 🎨 Beautiful UI with Live Activity Feed

The frontend shows **real-time feedback** as April works:

| When April Calls... | User Sees |
|---------------------|-----------|
| `get_current_datetime` | 🕐 **Time Check** (violet badge) |
| `ghl_calendars_get_calendar_events` | 📅 **Calendar Check** (coral badge) |
| `ghl_contacts_get_contacts` | 🔍 **Contact Search** (teal badge) |
| `ghl_opportunities_search_opportunity` | 💰 **Deal Search** (coral badge) |
| `ghl_conversations_send_a_new_message` | 📤 **Message Sent** (green badge) |

**Live activity messages:**
- "📅 Checking your schedule..." → "✨ Calendar loaded!"
- "🔍 Searching your contacts..." → "📇 Found matches!"
- "💰 Searching deals..." → "🎯 Opportunities found!"

---

## 🏗 Architecture

```
april_agent/
├── agent.py              # April LlmAgent (Gemini 2.0 Flash)
├── ghl_toolset.py        # 🆕 Custom GHLToolset (BaseToolset implementation)
├── main.py               # FastAPI server with SSE streaming
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
│
└── frontend/
    ├── src/
    │   ├── App.jsx                    # Main layout
    │   ├── components/
    │   │   ├── ChatMessage.jsx        # Message bubbles with tool badges
    │   │   ├── ChatInput.jsx          # Input with suggestions
    │   │   └── EventFeed.jsx          # 🆕 Live activity display (36 tools!)
    │   └── hooks/
    │       └── useAprilChat.js        # SSE streaming hook
    └── ...
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| **AI Framework** | Google ADK (Agent Development Kit) |
| **LLM** | Gemini 2.0 Flash |
| **CRM Integration** | GoHighLevel MCP (custom `GHLToolset`) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | React 19 + Vite 7 |
| **Styling** | Custom CSS (Tactile Minimalism) |
| **Deployment** | Railway (auto-deploy on git push) |

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
cd april_agent

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Configure Environment

Create `april_agent/.env`:

```env
# Google AI
GOOGLE_API_KEY=your_gemini_api_key

# GoHighLevel
GHL_PIT_TOKEN=pit-xxxxx-xxxx-xxxx-xxxx
GHL_LOCATION_ID=xxxxxxxxxxxxxxxxxxxxxx
GHL_CALENDAR_ID=xxxxxxxxxxxxxxxxxxxxxx

# Optional: Database
DATABASE_URL=postgresql://...
```

### 3. Run

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python main.py
# → Running on http://localhost:8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# → Running on http://localhost:5174
```

### 4. Test

Open `http://localhost:5174` and try:
- "What meetings do I have this week?"
- "Find John"
- "Show my open deals"

---

## 🔧 Configuration

### Required GHL PIT Scopes

Your Private Integration Token needs these scopes:

- ✅ View/Edit Contacts
- ✅ View/Edit Conversations
- ✅ View/Edit Conversation Messages
- ✅ View/Edit Opportunities
- ✅ View Calendars & Calendar Events
- ✅ View Locations
- ✅ View Payment Orders & Transactions
- ✅ View Custom Fields
- ✅ View/Edit Blogs (optional)
- ✅ View/Edit Social Media (optional)

### Calendar ID

Get your calendar ID from GHL:
1. Go to Settings → Calendars
2. Click on your calendar
3. Copy the ID from the URL

Add to `.env`:
```env
GHL_CALENDAR_ID=eGuHvbnvwrIhkgqOjl23
```

---

## 🚀 Deployment

### Railway (We Use This!)

The project auto-deploys when you push to `main`:

```bash
git add -A
git commit -m "Your changes"
git push origin main
# → Railway auto-deploys backend and frontend!
```

### Environment Variables on Railway

Set these in Railway dashboard:
- `GOOGLE_API_KEY`
- `GHL_PIT_TOKEN`
- `GHL_LOCATION_ID`
- `GHL_CALENDAR_ID`
- `PORT` (automatically set)

---

## 🔍 How It Works: The Technical Magic

### The Problem We Solved

GHL's MCP server is non-standard. It doesn't use WebSockets or proper SSE streaming. Instead:

1. You POST a JSON-RPC 2.0 request
2. It returns an SSE event stream in the HTTP response body
3. You parse nested JSON from the event data

### Our Solution

```python
class GHLTool(BaseTool):
    """Custom ADK tool that handles GHL's hybrid protocol."""
    
    def _get_declaration(self) -> types.FunctionDeclaration:
        # Convert GHL's JSON Schema to Gemini's format
        # This is what tells the LLM the exact parameters!
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=_json_schema_to_gemini_schema(self._tool_config.input_schema),
        )
    
    async def run_async(self, args, tool_context):
        # Call GHL MCP with proper protocol handling
        return await _call_ghl_mcp(
            tool_name=self._tool_config.name,
            arguments=args,  # Auto-converts timestamps to strings!
            ...
        )
```

### Why This Matters

Before this fix, the LLM didn't know what parameters were available. It would ask users for "milliseconds" and "IDs". Now it just works:

| Before | After |
|--------|-------|
| "I need the start time in milliseconds" | *Automatically calls `get_current_datetime` first* |
| "Please provide the calendar ID" | *Uses configured `GHL_CALENDAR_ID`* |
| Random parameter guessing | Proper schema → correct calls every time |

---

## 🎯 Smart Behaviors

### Date Awareness

April always knows what day it is:

```
User: "Check my calendar this week"

April's thought process:
1. Call get_current_datetime → Gets Dec 01-07, 2025 timestamps
2. Call ghl_calendars_get_calendar_events with those timestamps
3. Format response: "📅 This week you have: ..."
```

### Action-Oriented

April doesn't ask for permission - she just does it:

| User Says | April Does |
|-----------|------------|
| "Find Derek" | Immediately searches contacts |
| "Check calendar" | Gets date → Queries calendar → Shows results |
| "Add Sarah, sarah@test.com" | Creates contact → Confirms "✅ Added!" |

### Tool Chaining

April naturally chains multiple tools:

```
User: "What's my schedule and any deals closing this week?"

April:
1. get_current_datetime → Get week range
2. ghl_calendars_get_calendar_events → Get meetings
3. ghl_opportunities_search_opportunity → Get deals
4. Combines results in one beautiful response
```

---

## 📞 Support

**For AiPRL Employees Only**

- **Slack:** #april-agent-support
- **Email:** engineering@aiprlassist.com
- **Issues:** Create in GitHub repo

---

## 🗺 Roadmap

### ✅ Completed (V2.0)
- [x] Proper ADK toolset integration
- [x] 36 GHL tools with correct schemas
- [x] Real-time date awareness
- [x] Beautiful live activity UI
- [x] Auto-deploy on Railway

### 🔜 Coming Soon
- [ ] Pipedream MCP integration (Gmail, Asana)
- [ ] Voice interface (Vapi)
- [ ] Webhook receivers for real-time updates
- [ ] Multi-user authentication

### 🔮 Future
- [ ] Custom workflow builder
- [ ] White-label theming
- [ ] Enterprise SSO

---

<div align="center">

## 🙏 Credits

This massive integration was a **team effort** and a **technical achievement**.

We turned GoHighLevel's non-standard MCP into a beautiful, working ADK toolset.

**Built with ❤️ by AiPRL Engineering**

*"Just ask April - she'll handle it."*

---

**Version 2.0.0** | December 2024

</div>
