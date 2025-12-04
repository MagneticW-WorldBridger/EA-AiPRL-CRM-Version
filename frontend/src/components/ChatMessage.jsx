/**
 * ChatMessage - REVOLUTIONARY Message Display
 * Shows friendly tool badges with commercial verbiage
 */
import { User, Bot, Sparkles, Users, Calendar, MessageSquare, Target, MapPin, CreditCard, Tag, FileText, Phone, Briefcase, Settings } from 'lucide-react'

// 🎯 FRIENDLY TOOL NAMES WITH EMOJIS
const TOOL_CONFIG = {
  // Calendar
  'ghl_get_calendar_events': { label: '📅 Calendar Check', icon: Calendar, color: 'coral' },
  'ghl_get_appointment_notes': { label: '📝 Meeting Notes', icon: FileText, color: 'violet' },
  
  // Contacts
  'ghl_get_contact': { label: '👤 Contact Lookup', icon: Users, color: 'teal' },
  'ghl_get_contacts': { label: '🔍 Contact Search', icon: Users, color: 'teal' },
  'ghl_create_contact': { label: '✨ New Contact', icon: Users, color: 'green' },
  'ghl_update_contact': { label: '✏️ Contact Update', icon: Users, color: 'blue' },
  'ghl_upsert_contact': { label: '🔄 Contact Sync', icon: Users, color: 'blue' },
  'ghl_add_tags': { label: '🏷️ Added Tags', icon: Tag, color: 'violet' },
  'ghl_remove_tags': { label: '✂️ Tags Removed', icon: Tag, color: 'coral' },
  'ghl_get_contact_tasks': { label: '✅ Task List', icon: FileText, color: 'teal' },
  
  // Conversations
  'ghl_search_conversations': { label: '💬 Message Search', icon: MessageSquare, color: 'blue' },
  'ghl_get_messages': { label: '📥 Messages', icon: MessageSquare, color: 'blue' },
  'ghl_send_message': { label: '📤 Message Sent', icon: Phone, color: 'green' },
  
  // Opportunities
  'ghl_get_pipelines': { label: '🎯 Pipelines', icon: Target, color: 'coral' },
  'ghl_search_opportunities': { label: '💰 Deal Search', icon: Briefcase, color: 'coral' },
  'ghl_get_opportunity': { label: '📈 Deal Details', icon: Target, color: 'coral' },
  'ghl_update_opportunity': { label: '🚀 Deal Updated', icon: Target, color: 'gold' },
  
  // Location
  'ghl_get_location': { label: '📍 Location Info', icon: MapPin, color: 'teal' },
  'ghl_get_custom_fields': { label: '⚙️ Custom Fields', icon: Settings, color: 'violet' },
  
  // Payments
  'ghl_get_order': { label: '🧾 Order Details', icon: CreditCard, color: 'green' },
  'ghl_list_transactions': { label: '💳 Transactions', icon: CreditCard, color: 'green' },
  
  // Fallback
  'default': { label: '⚡ Processed', icon: Sparkles, color: 'teal' }
}

const getToolConfig = (name) => {
  if (!name) return TOOL_CONFIG['default']
  return TOOL_CONFIG[name] || TOOL_CONFIG['default']
}

const colorClasses = {
  coral: 'badge-coral',
  teal: 'badge-teal',
  green: 'badge-green',
  blue: 'badge-blue',
  violet: 'badge-violet',
  gold: 'badge-gold'
}

function ToolBadge({ name }) {
  const config = getToolConfig(name)
  const Icon = config.icon
  const colorClass = colorClasses[config.color] || 'badge-teal'
  
  return (
    <span className={`tool-badge-mini ${colorClass}`}>
      <Icon className="w-3 h-3" />
      <span>{config.label}</span>
    </span>
  )
}

function MessageContent({ text }) {
  if (!text) return null

  const renderLine = (line, lineIndex) => {
    // Handle bullet points
    if (line.trim().startsWith('*') || line.trim().startsWith('•')) {
      const content = line.trim().slice(1).trim()
      return (
        <p key={lineIndex} className="message-line message-bullet">
          {renderTextWithFormatting(content)}
        </p>
      )
    }
    
    return (
      <p key={lineIndex} className="message-line">
        {renderTextWithFormatting(line)}
      </p>
    )
  }
  
  const renderTextWithFormatting = (text) => {
    // Handle bold **text**
    const parts = text.split(/(\*\*[^*]+\*\*)/g)
    
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>
      }
      // Handle URLs
      const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`[\]]+)/g
      const segments = part.split(urlRegex)
      return segments.map((seg, j) => {
        if (seg.match(/^https?:\/\//)) {
          return (
            <a 
              key={`${i}-${j}`}
              href={seg}
              target="_blank"
              rel="noopener noreferrer"
              className="message-link"
            >
              {seg.length > 50 ? seg.slice(0, 50) + '...' : seg}
            </a>
          )
        }
        return <span key={`${i}-${j}`}>{seg}</span>
      })
    })
  }

  return (
    <div className="message-content">
      {text.split('\n').map((line, index) => renderLine(line, index))}
    </div>
  )
}

export function ChatMessage({ message }) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  
  return (
    <div className={`chat-message ${isUser ? 'chat-message-user' : ''} ${isSystem ? 'chat-message-system' : ''}`}>
      {/* Avatar */}
      <div className={`message-avatar ${isUser ? 'avatar-user' : isSystem ? 'avatar-system' : 'avatar-agent'}`}>
        {isUser ? (
          <User className="w-4 h-4" />
        ) : isSystem ? (
          <Sparkles className="w-4 h-4" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>
      
      {/* Message Content */}
      <div className="message-body">
        <div className={`message-bubble ${isUser ? 'bubble-user' : isSystem ? 'bubble-system' : 'bubble-agent'}`}>
          <MessageContent text={message.text} />
        </div>
        
        {/* Tool calls indicator - now with fun labels */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="message-tools">
            {message.toolCalls.map((tool, idx) => (
              <ToolBadge key={idx} name={tool.name} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatMessage
