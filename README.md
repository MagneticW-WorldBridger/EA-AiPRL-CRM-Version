# 🚀 April Agent - Executive Assistant

<div align="center">

**INTERNAL USE ONLY - AiPRL EMPLOYEES**

*The Revolutionary AI Executive Assistant powered by Google ADK & GoHighLevel*

**Version 1.0.0** | Last Updated: December 2024

</div>

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#-architecture)
3. [All 21 GHL Tools](#-all-21-ghl-tools)
4. [Frontend Features](#-frontend-features)
5. [UX Design Philosophy](#-ux-design-philosophy)
6. [Setup & Installation](#-setup--installation)
7. [Configuration](#-configuration)
8. [API Reference](#-api-reference)
9. [Multi-Tenancy](#-multi-tenancy)
10. [Deployment](#-deployment)
11. [Troubleshooting](#-troubleshooting)
12. [Future Roadmap](#-future-roadmap)

---

## 🎯 Overview

**April** is AiPRL's flagship AI Executive Assistant, designed to revolutionize how busy professionals interact with their GoHighLevel CRM. Built on Google's Agent Development Kit (ADK), April provides:

- **Complete GHL Integration** - All 21 MCP tools available
- **Multi-Tenant Architecture** - Serve multiple clients from single deployment
- **Tactile Minimalism UI** - Beautiful, depth-based interface design
- **Real-Time Activity Feed** - Fun, commercial verbiage for every tool call
- **Proactive Assistance** - Agent suggests next steps after every task

### Key Differentiators

| Feature | Traditional Chatbots | April |
|---------|---------------------|-------|
| CRM Access | Limited or none | Full 21-tool GHL integration |
| Response Style | Generic | Context-aware with proactive suggestions |
| Visual Feedback | Basic loading spinner | Animated activity feed with progress |
| Multi-tenancy | Usually single-user | Built-in credential isolation |
| Design | Flat, generic | Tactile minimalism with depth |

---

## 🏗 Architecture

```
april_agent/
├── __init__.py           # ADK agent discovery
├── agent.py              # April LlmAgent definition (Gemini 2.0 Flash)
├── ghl_tools.py          # All 21 GoHighLevel HTTP tools (JSON-RPC 2.0)
├── main.py               # FastAPI server with session management
├── config.py             # User credential mock database
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (git-ignored)
│
└── frontend/
    ├── package.json      # React + Vite + TailwindCSS
    ├── vite.config.js    # Dev server with API proxy
    ├── index.html        # Entry point
    │
    └── src/
        ├── main.jsx
        ├── App.jsx                    # Main layout
        ├── index.css                  # Tactile Minimalism styles
        │
        ├── components/
        │   ├── ChatMessage.jsx        # Message bubbles with tool badges
        │   ├── ChatInput.jsx          # Input with categorized suggestions
        │   └── EventFeed.jsx          # Real-time activity display
        │
        └── hooks/
            └── useAprilChat.js        # Chat state & API calls
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **AI Framework** | Google ADK | Agent orchestration, tool management |
| **LLM** | Gemini 2.0 Flash | Fast, intelligent reasoning |
| **Backend** | FastAPI + Uvicorn | High-performance async API |
| **Session** | In-Memory / PostgreSQL | Conversation persistence |
| **CRM** | GoHighLevel MCP | JSON-RPC 2.0 over HTTP+SSE |
| **Frontend** | React 19 + Vite 7 | Modern SPA framework |
| **Styling** | TailwindCSS 4 | Utility-first CSS |
| **Fonts** | Outfit + Fraunces | Display & body typography |

---

## 🛠 All 21 GHL Tools

April implements **every tool** from GoHighLevel's MCP server:

### 📅 Calendar Tools (2)

| Tool | Function | Use Case |
|------|----------|----------|
| `ghl_get_calendar_events` | Get events by date range | "What meetings do I have this week?" |
| `ghl_get_appointment_notes` | Retrieve appointment notes | "Get notes from my last meeting" |

### 👥 Contact Tools (8)

| Tool | Function | Use Case |
|------|----------|----------|
| `ghl_get_contact` | Get single contact by ID | "Show me John's details" |
| `ghl_get_contacts` | Search contacts | "Find contacts named Sarah" |
| `ghl_create_contact` | Create new contact | "Add John Doe to CRM" |
| `ghl_update_contact` | Update existing contact | "Change John's phone number" |
| `ghl_upsert_contact` | Create or update (smart sync) | "Sync this contact" |
| `ghl_add_tags` | Add tags to contact | "Tag John as VIP" |
| `ghl_remove_tags` | Remove tags from contact | "Remove VIP tag from John" |
| `ghl_get_contact_tasks` | Get tasks for contact | "Show John's pending tasks" |

### 💬 Conversation Tools (3)

| Tool | Function | Use Case |
|------|----------|----------|
| `ghl_search_conversations` | Find message threads | "Show unread conversations" |
| `ghl_get_messages` | Get full message history | "Get messages with John" |
| `ghl_send_message` | Send SMS or Email | "Text John: I'll be 10 min late" |

### 🎯 Opportunity Tools (4)

| Tool | Function | Use Case |
|------|----------|----------|
| `ghl_get_pipelines` | List all pipelines & stages | "Show me my pipelines" |
| `ghl_search_opportunities` | Search deals | "Find open deals over $5000" |
| `ghl_get_opportunity` | Get single deal details | "Show the Acme deal" |
| `ghl_update_opportunity` | Update deal status/stage | "Mark deal as won" |

### 📍 Location Tools (2)

| Tool | Function | Use Case |
|------|----------|----------|
| `ghl_get_location` | Get business info | "What location am I connected to?" |
| `ghl_get_custom_fields` | List custom fields | "Show custom field definitions" |

### 💳 Payment Tools (2)

| Tool | Function | Use Case |
|------|----------|----------|
| `ghl_get_order` | Get order details | "Show order #12345" |
| `ghl_list_transactions` | List payment history | "Show transactions this month" |

---

## 🎨 Frontend Features

### Tactile Minimalism Design System

Based on the principle: **"Depth is Logic - Light tells users what they can touch"**

#### Design Rules Applied

1. **Light Source Consistency** - Fixed at 12:00 (top highlights, bottom shadows)
2. **Monochromatic Layering** - 0.1 lightness increments for depth
3. **Squishy Click Effect** - Elements depress on click (inset shadow)
4. **Soft Shadows** - Teal-tinted, never pure black
5. **Noise Texture** - 2% opacity grain for tactile feel

#### Color Palette

```css
--brand-teal: #0d9488;      /* Primary - Trust */
--brand-coral: #f97316;     /* Accent - Energy */
--brand-violet: #8b5cf6;    /* Secondary - AI */
--brand-slate: #1e293b;     /* Dark text/elements */
```

### Real-Time Activity Feed

Each of the 21 tools has custom **commercial verbiage**:

| Tool | Calling State | Complete State |
|------|---------------|----------------|
| Calendar | "📅 Checking your schedule..." | "✨ Calendar loaded!" |
| Contacts | "🔍 Searching your contacts..." | "📇 Found matches!" |
| Pipelines | "🎯 Loading your pipelines..." | "📊 Pipeline overview ready!" |
| Send Message | "📤 Sending your message..." | "✈️ Message sent!" |
| Opportunities | "💰 Searching deals..." | "🎯 Opportunities found!" |

### Smart Suggestions

Categorized into 6 groups for easy discovery:

- 🚀 **Quick Actions** - Common tasks
- 👥 **Contacts & CRM** - Contact management
- 📅 **Calendar** - Schedule management
- 💰 **Deals & Pipeline** - Sales operations
- 💬 **Messages** - Communication
- 💳 **Payments** - Financial operations

---

## 🧠 UX Design Philosophy

### Gestalt Principles Applied

| Principle | Application in April |
|-----------|---------------------|
| **Proximity** | Related tool badges grouped under messages |
| **Similarity** | Consistent bubble styles for user/agent |
| **Closure** | Rounded corners guide eye to content |
| **Continuity** | Message flow guides conversation |
| **Figure-Ground** | Clear contrast between messages and background |
| **Symmetry** | Balanced header and footer layout |

### Psychological Response Optimization

1. **Reduce Anxiety** - Activity feed shows progress during waits
2. **Build Trust** - Consistent, predictable interactions
3. **Delight Users** - Fun verbiage and micro-animations
4. **Guide Action** - Proactive suggestions after every response

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- GoHighLevel account with API access

### Backend Setup

```bash
cd april_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Frontend Setup

```bash
cd april_agent/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Run Both

**Terminal 1 - Backend:**
```bash
cd april_agent
source venv/bin/activate
uvicorn april_agent.main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd april_agent/frontend
npm run dev
```

Access at: `http://localhost:5174`

---

## 🔧 Configuration

### Environment Variables

Create `april_agent/.env`:

```env
# Required: Google AI
GOOGLE_API_KEY=your_gemini_api_key

# Required: GoHighLevel
GHL_PIT_TOKEN=pit-xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
GHL_LOCATION_ID=xxxxxxxxxxxxxxxxxxxxxx

# Optional: Database (for persistent sessions)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Optional: Pipedream (future)
PIPEDREAM_API_KEY=your_pipedream_key
PIPEDREAM_USER_ID=your_pipedream_user_id
```

### GHL Private Integration Token (PIT) Scopes

Ensure your PIT has these scopes enabled:

- ✅ View/Edit Contacts
- ✅ View/Edit Conversations  
- ✅ View/Edit Conversation Messages
- ✅ View/Edit Opportunities
- ✅ View Calendars & Calendar Events
- ✅ View Locations
- ✅ View Payment Orders & Transactions
- ✅ View Custom Fields

---

## 📡 API Reference

### Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "april_agent",
  "session_service": "in-memory"
}
```

#### `POST /sessions`
Create a new session with user credentials loaded.

**Request:**
```json
{
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "session_id": "uuid-xxx-xxx",
  "user_id": "user_123",
  "credentials_loaded": true,
  "message": "Session created with credentials loaded."
}
```

#### `POST /chat`
Send a message and get a response.

**Request:**
```json
{
  "user_id": "user_123",
  "session_id": "uuid-xxx-xxx",
  "message": "What location am I connected to?"
}
```

**Response:**
```json
{
  "response": "Your location is **AiPRL Assist** in Charlotte, NC...",
  "session_id": "uuid-xxx-xxx",
  "events_count": 3
}
```

---

## 👥 Multi-Tenancy

April is designed for multi-tenant SaaS deployment:

### How It Works

1. **User requests session** → `/sessions` endpoint
2. **Server looks up user credentials** → `config.py` mock database
3. **Credentials stored in session state** with `user:` prefix:
   - `user:ghl_pit_token`
   - `user:ghl_location_id`
4. **Tools read from ToolContext.state** → Per-request isolation
5. **Each API call uses correct credentials** → Complete tenant isolation

### Adding New Users

In `config.py`:

```python
USERS_DB = {
    "user_123": {
        "ghl_pit_token": "pit-xxxxx...",
        "ghl_location_id": "xxxxxxxxxxxx",
    },
    "user_456": {
        "ghl_pit_token": "pit-yyyyy...",
        "ghl_location_id": "yyyyyyyyyyyy",
    },
}
```

### Production Recommendation

Replace `config.py` mock database with:
- PostgreSQL with encrypted credentials
- AWS Secrets Manager / GCP Secret Manager
- HashiCorp Vault

---

## 🚀 Deployment

### Railway (Recommended)

**Backend:**
```bash
cd april_agent
railway up
```

Uses `railway.json` and `nixpacks.toml` for configuration.

**Frontend:**
```bash
cd april_agent/frontend
railway up
```

### Environment Variables on Railway

Set these in Railway dashboard:
- `GOOGLE_API_KEY`
- `GHL_PIT_TOKEN`
- `GHL_LOCATION_ID`
- `DATABASE_URL` (if using PostgreSQL)
- `PORT` (automatically set by Railway)

### Docker (Alternative)

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "april_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔍 Troubleshooting

### Common Issues

#### "GHL credentials not configured"
- Ensure `.env` has `GHL_PIT_TOKEN` and `GHL_LOCATION_ID`
- Check `config.py` has your user_id mapped

#### "Token does not have access to this location"
- Verify PIT scopes in GHL Settings → Private Integrations
- Ensure location ID matches the PIT's authorized location

#### "Connection refused on port 8001"
- Start backend: `uvicorn april_agent.main:app --port 8001`
- Check no other process using port 8001

#### "Frontend can't reach API"
- Check `vite.config.js` proxy settings
- Ensure backend is running before frontend

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🔮 Future Roadmap

### Phase 2: Pipedream Integration
- Gmail email sending via Pipedream MCP
- Asana task management
- Google Calendar sync

### Phase 3: Advanced Features
- Voice interface (Vapi integration)
- Webhook receivers for real-time updates
- Custom workflow builder

### Phase 4: Enterprise
- SSO authentication
- Role-based access control
- Audit logging
- White-label customization

---

## 📞 Support

**For AiPRL Employees Only**

- **Slack:** #april-agent-support
- **Email:** engineering@aiprlassist.com
- **Docs:** This README + inline code comments

---

<div align="center">

**Built with ❤️ by AiPRL Engineering**

*Revolutionizing the Executive Assistant Experience*

</div>
