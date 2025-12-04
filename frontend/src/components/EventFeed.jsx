/**
 * EventFeed - LIVE STREAMING Activity Display
 * Shows REAL tool calls as they happen - not fake thinking!
 * 
 * Each GHL tool gets its own fun commercial verbiage
 */
import { 
  Zap, Check, Users, Calendar, MessageSquare, Target, MapPin, 
  CreditCard, Search, Tag, FileText, Sparkles, Rocket, Coffee,
  Bell, Mail, Phone, Briefcase, Star, Clock, Loader2
} from 'lucide-react'

// 🎯 FUN COMMERCIAL VERBIAGE FOR EACH TOOL
const TOOL_MESSAGES = {
  // Calendar Tools
  'ghl_get_calendar_events': {
    calling: "📅 Checking your schedule...",
    complete: "✨ Calendar loaded!",
    icon: Calendar,
    color: 'coral'
  },
  'ghl_get_appointment_notes': {
    calling: "📝 Grabbing meeting notes...",
    complete: "📋 Notes ready!",
    icon: FileText,
    color: 'violet'
  },
  
  // Contact Tools  
  'ghl_get_contact': {
    calling: "🔍 Pulling up that contact...",
    complete: "👤 Got 'em!",
    icon: Users,
    color: 'teal'
  },
  'ghl_get_contacts': {
    calling: "🔎 Searching your contacts...",
    complete: "📇 Found matches!",
    icon: Search,
    color: 'teal'
  },
  'ghl_create_contact': {
    calling: "✨ Creating new contact...",
    complete: "🎉 Contact added to CRM!",
    icon: Users,
    color: 'green'
  },
  'ghl_update_contact': {
    calling: "✏️ Updating contact info...",
    complete: "✅ Contact updated!",
    icon: Users,
    color: 'blue'
  },
  'ghl_upsert_contact': {
    calling: "🔄 Syncing contact...",
    complete: "✅ Contact synced!",
    icon: Users,
    color: 'blue'
  },
  'ghl_add_tags': {
    calling: "🏷️ Adding tags...",
    complete: "🏷️ Tags applied!",
    icon: Tag,
    color: 'violet'
  },
  'ghl_remove_tags': {
    calling: "🏷️ Removing tags...",
    complete: "✂️ Tags removed!",
    icon: Tag,
    color: 'coral'
  },
  'ghl_get_contact_tasks': {
    calling: "📋 Fetching tasks...",
    complete: "✅ Tasks loaded!",
    icon: FileText,
    color: 'teal'
  },
  
  // Conversation Tools
  'ghl_search_conversations': {
    calling: "💬 Searching messages...",
    complete: "📨 Conversations found!",
    icon: MessageSquare,
    color: 'blue'
  },
  'ghl_get_messages': {
    calling: "📥 Loading message history...",
    complete: "💬 Messages ready!",
    icon: Mail,
    color: 'blue'
  },
  'ghl_send_message': {
    calling: "📤 Sending your message...",
    complete: "✈️ Message sent!",
    icon: Phone,
    color: 'green'
  },
  
  // Opportunity Tools
  'ghl_get_pipelines': {
    calling: "🎯 Loading your pipelines...",
    complete: "📊 Pipeline overview ready!",
    icon: Target,
    color: 'coral'
  },
  'ghl_search_opportunities': {
    calling: "💰 Searching deals...",
    complete: "🎯 Opportunities found!",
    icon: Briefcase,
    color: 'coral'
  },
  'ghl_get_opportunity': {
    calling: "📈 Pulling deal details...",
    complete: "💼 Deal info loaded!",
    icon: Target,
    color: 'coral'
  },
  'ghl_update_opportunity': {
    calling: "📝 Updating deal...",
    complete: "🚀 Deal updated!",
    icon: Star,
    color: 'gold'
  },
  
  // Location Tools
  'ghl_get_location': {
    calling: "📍 Getting location info...",
    complete: "🏢 Location loaded!",
    icon: MapPin,
    color: 'teal'
  },
  'ghl_get_custom_fields': {
    calling: "⚙️ Loading custom fields...",
    complete: "🔧 Fields ready!",
    icon: FileText,
    color: 'violet'
  },
  
  // Payment Tools
  'ghl_get_order': {
    calling: "🧾 Fetching order details...",
    complete: "💳 Order loaded!",
    icon: CreditCard,
    color: 'green'
  },
  'ghl_list_transactions': {
    calling: "💸 Loading transactions...",
    complete: "📊 Transactions ready!",
    icon: CreditCard,
    color: 'green'
  },
  
  // Fallback
  'default': {
    calling: "⚡ Working on it...",
    complete: "✨ Done!",
    icon: Sparkles,
    color: 'coral'
  }
}

// Get config for a tool
const getToolConfig = (name) => {
  if (!name) return TOOL_MESSAGES['default']
  return TOOL_MESSAGES[name] || TOOL_MESSAGES['default']
}

// Color classes
const colorClasses = {
  coral: 'event-coral',
  teal: 'event-teal',
  green: 'event-green',
  blue: 'event-blue',
  violet: 'event-violet',
  gold: 'event-gold'
}

function EventBadge({ event, isLatest }) {
  const isCalling = event.type === 'function_call'
  const config = getToolConfig(event.name)
  const Icon = config.icon
  const colorClass = colorClasses[config.color] || 'event-coral'
  
  return (
    <div className={`event-item ${isLatest ? 'event-item-latest' : ''}`}>
      <div className={`event-badge ${isCalling ? 'event-calling' : 'event-complete'} ${colorClass}`}>
        <span className="event-icon">
          {isCalling ? <Icon className="w-4 h-4" /> : <Check className="w-4 h-4" />}
        </span>
        <span className="event-name">
          {isCalling ? config.calling : config.complete}
        </span>
        {isCalling && isLatest && <span className="event-spinner" />}
      </div>
    </div>
  )
}

function ThinkingIndicator() {
  return (
    <div className="thinking-indicator">
      <div className="thinking-avatar">
        <Coffee className="w-5 h-5" />
      </div>
      <div className="thinking-content">
        <div className="thinking-dots">
          <div className="thinking-dot" />
          <div className="thinking-dot" />
          <div className="thinking-dot" />
        </div>
        <span className="thinking-text">April is analyzing your request...</span>
      </div>
    </div>
  )
}

function StreamingPreview({ text }) {
  if (!text) return null
  
  const preview = text.length > 200 ? text.slice(0, 200) + '...' : text
  
  return (
    <div className="streaming-preview">
      <div className="streaming-cursor" />
      <span className="streaming-text">{preview}</span>
    </div>
  )
}

// Chain progress indicator
function ChainProgress({ total, current }) {
  if (total <= 1) return null
  
  return (
    <div className="chain-progress">
      <div className="chain-bar">
        <div 
          className="chain-fill" 
          style={{ width: `${(current / total) * 100}%` }}
        />
      </div>
      <span className="chain-text">Step {current} of {total}</span>
    </div>
  )
}

export function EventFeed({ events, isStreaming, streamingText }) {
  const uniqueEvents = events.slice(-8)
  const completedCount = uniqueEvents.filter(e => e.type === 'function_response').length
  const totalCount = Math.max(uniqueEvents.length, 1)
  const lastEvent = uniqueEvents[uniqueEvents.length - 1]
  const isWaitingForTool = lastEvent?.type === 'function_call'
  
  return (
    <div className="event-feed animate-fade-in">
      <div className="event-feed-header">
        <div className="event-feed-indicator" />
        <span>Live Activity</span>
        <div className="event-feed-badge">
          <Rocket className="w-3 h-3" />
          <span>AI Powered</span>
        </div>
      </div>
      
      <div className="event-feed-content">
        {/* Show thinking indicator when no events yet */}
        {uniqueEvents.length === 0 && isStreaming && (
          <ThinkingIndicator />
        )}
        
        {/* Chain progress bar for multi-tool operations */}
        {uniqueEvents.length > 1 && (
          <ChainProgress total={totalCount} current={completedCount + 1} />
        )}
        
        {/* Render each tool call/response as it happens */}
        {uniqueEvents.map((event, idx) => (
          <EventBadge 
            key={event.id || idx} 
            event={event} 
            isLatest={idx === uniqueEvents.length - 1 && isWaitingForTool}
          />
        ))}
        
        {/* Show "crafting response" when tools are done but still streaming */}
        {isStreaming && uniqueEvents.length > 0 && !isWaitingForTool && !streamingText && (
          <div className="event-item">
            <div className="event-badge event-calling event-violet">
              <span className="event-icon">
                <Sparkles className="w-4 h-4" />
              </span>
              <span className="event-name">✨ Crafting your response...</span>
              <span className="event-spinner" />
            </div>
          </div>
        )}
        
        {/* Show streaming text preview */}
        <StreamingPreview text={streamingText} />
      </div>
    </div>
  )
}

export default EventFeed
