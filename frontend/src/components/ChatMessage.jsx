/**
 * ChatMessage - REVOLUTIONARY Message Display
 * Shows friendly tool badges with commercial verbiage
 * 
 * Updated for NEW MCP tool names (ghl_calendars_*, ghl_contacts_*, etc.)
 */
import { User, Bot, Sparkles, Users, Calendar, MessageSquare, Target, MapPin, CreditCard, Tag, FileText, Phone, Briefcase, Settings, Clock, Mail, Globe, FileEdit, Share2, BarChart3, Search, Star } from 'lucide-react'

// 🎯 FRIENDLY TOOL NAMES WITH EMOJIS - NEW MCP NAMES
const TOOL_CONFIG = {
  // DateTime
  'get_current_datetime': { label: '🕐 Time Check', icon: Clock, color: 'violet' },

  // Calendar
  'ghl_calendars_get_calendar_events': { label: '📅 Calendar Check', icon: Calendar, color: 'coral' },
  'ghl_calendars_get_appointment_notes': { label: '📝 Meeting Notes', icon: FileText, color: 'violet' },
  
  // Contacts
  'ghl_contacts_get_contact': { label: '👤 Contact Lookup', icon: Users, color: 'teal' },
  'ghl_contacts_get_contacts': { label: '🔍 Contact Search', icon: Search, color: 'teal' },
  'ghl_contacts_create_contact': { label: '✨ New Contact', icon: Users, color: 'green' },
  'ghl_contacts_update_contact': { label: '✏️ Contact Update', icon: Users, color: 'blue' },
  'ghl_contacts_upsert_contact': { label: '🔄 Contact Sync', icon: Users, color: 'blue' },
  'ghl_contacts_add_tags': { label: '🏷️ Added Tags', icon: Tag, color: 'violet' },
  'ghl_contacts_remove_tags': { label: '✂️ Tags Removed', icon: Tag, color: 'coral' },
  'ghl_contacts_get_all_tasks': { label: '✅ Task List', icon: FileText, color: 'teal' },
  
  // Conversations
  'ghl_conversations_search_conversation': { label: '💬 Message Search', icon: MessageSquare, color: 'blue' },
  'ghl_conversations_get_messages': { label: '📥 Messages', icon: MessageSquare, color: 'blue' },
  'ghl_conversations_send_a_new_message': { label: '📤 Message Sent', icon: Phone, color: 'green' },
  
  // Opportunities
  'ghl_opportunities_get_pipelines': { label: '🎯 Pipelines', icon: Target, color: 'coral' },
  'ghl_opportunities_search_opportunity': { label: '💰 Deal Search', icon: Briefcase, color: 'coral' },
  'ghl_opportunities_get_opportunity': { label: '📈 Deal Details', icon: Target, color: 'coral' },
  'ghl_opportunities_update_opportunity': { label: '🚀 Deal Updated', icon: Star, color: 'gold' },
  
  // Location
  'ghl_locations_get_location': { label: '📍 Location Info', icon: MapPin, color: 'teal' },
  'ghl_locations_get_custom_fields': { label: '⚙️ Custom Fields', icon: Settings, color: 'violet' },
  
  // Payments
  'ghl_payments_get_order_by_id': { label: '🧾 Order Details', icon: CreditCard, color: 'green' },
  'ghl_payments_list_transactions': { label: '💳 Transactions', icon: CreditCard, color: 'green' },

  // Emails
  'ghl_emails_fetch_template': { label: '📧 Email Templates', icon: Mail, color: 'blue' },
  'ghl_emails_create_template': { label: '✨ New Template', icon: Mail, color: 'green' },

  // Blogs
  'ghl_blogs_get_blogs': { label: '📰 Blogs', icon: FileEdit, color: 'violet' },
  'ghl_blogs_get_blog_post': { label: '📝 Blog Posts', icon: FileEdit, color: 'violet' },
  'ghl_blogs_create_blog_post': { label: '✍️ New Post', icon: FileEdit, color: 'green' },
  'ghl_blogs_update_blog_post': { label: '✏️ Blog Update', icon: FileEdit, color: 'blue' },
  'ghl_blogs_check_url_slug_exists': { label: '🔗 URL Check', icon: FileEdit, color: 'teal' },
  'ghl_blogs_get_all_blog_authors_by_location': { label: '✍️ Authors', icon: Users, color: 'violet' },
  'ghl_blogs_get_all_categories_by_location': { label: '🏷️ Categories', icon: Tag, color: 'violet' },

  // Social Media
  'ghl_socialmediaposting_get_account': { label: '📱 Social Accounts', icon: Share2, color: 'blue' },
  'ghl_socialmediaposting_get_posts': { label: '📱 Social Posts', icon: Share2, color: 'blue' },
  'ghl_socialmediaposting_get_post': { label: '📱 Post Details', icon: Share2, color: 'blue' },
  'ghl_socialmediaposting_create_post': { label: '🚀 New Post', icon: Share2, color: 'green' },
  'ghl_socialmediaposting_edit_post': { label: '✏️ Edit Post', icon: Share2, color: 'blue' },
  'ghl_socialmediaposting_get_social_media_statistics': { label: '📊 Analytics', icon: BarChart3, color: 'coral' },

  // Google Search
  'google_search': { label: '🌐 Web Search', icon: Globe, color: 'blue' },
  
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
