/**
 * ChatInput - REVOLUTIONARY Message Input
 * Smart suggestions that showcase ALL 21 GHL tools
 * Makes users excited to explore capabilities!
 */
import { useRef, useEffect, useState } from 'react'
import { Send, Loader2, StopCircle, Sparkles, ChevronDown, ChevronUp } from 'lucide-react'

// Categorized suggestions to showcase different capabilities
const SUGGESTION_CATEGORIES = [
  {
    label: "🚀 Quick Actions",
    items: [
      "What's my location info?",
      "Show me all pipelines",
      "Any unread conversations?",
    ]
  },
  {
    label: "👥 Contacts & CRM",
    items: [
      "Find contacts named John",
      "Search contacts by email sarah@",
      "Show tasks for my top lead",
      "Add 'VIP' tag to contact",
    ]
  },
  {
    label: "📅 Calendar",
    items: [
      "What meetings do I have this week?",
      "Check my schedule for tomorrow",
      "Get notes from my last appointment",
    ]
  },
  {
    label: "💰 Deals & Pipeline",
    items: [
      "Show deals in prospect stage",
      "What opportunities are open?",
      "Find deals worth over $5000",
      "Update deal to won status",
    ]
  },
  {
    label: "💬 Messages",
    items: [
      "Search recent conversations",
      "Send an SMS to my client",
      "Get message history with John",
    ]
  },
  {
    label: "💳 Payments",
    items: [
      "Show recent transactions",
      "Get order details",
      "List payments this month",
    ]
  }
]

// Flatten for initial display
const QUICK_SUGGESTIONS = [
  "What's my location info?",
  "Show my pipelines",
  "Find recent contacts",
  "Check my calendar this week",
  "Search open opportunities",
]

export function ChatInput({ value, onChange, onSend, onCancel, status }) {
  const inputRef = useRef(null)
  const [showMore, setShowMore] = useState(false)
  const isLoading = status === 'loading'
  const isStreaming = status === 'streaming'
  const isBusy = isLoading || isStreaming

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = (e) => {
    e?.preventDefault()
    if (value.trim() && !isBusy) {
      onSend(value)
      setShowMore(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleSuggestion = (text) => {
    if (!isBusy) {
      onSend(text) // Auto-send suggestions immediately
      setShowMore(false)
    }
  }

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-input-form">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask April to manage contacts, check calendar, close deals..."
            rows={1}
            className="chat-textarea"
            disabled={isBusy}
          />
        </div>
        
        {isStreaming ? (
          <button
            type="button"
            onClick={onCancel}
            className="send-btn cancel-btn"
            aria-label="Cancel"
          >
            <StopCircle className="w-5 h-5" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!value.trim() || isBusy}
            className="send-btn"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        )}
      </form>
      
      {/* Quick suggestions */}
      <div className="suggestions">
        {QUICK_SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => handleSuggestion(suggestion)}
            className="suggestion-btn"
            disabled={isBusy}
          >
            {suggestion}
          </button>
        ))}
        
        <button
          onClick={() => setShowMore(!showMore)}
          className="suggestion-btn suggestion-more"
          disabled={isBusy}
        >
          <Sparkles className="w-3 h-3" />
          {showMore ? 'Less' : 'More ideas'}
          {showMore ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>
      
      {/* Expanded suggestions by category */}
      {showMore && (
        <div className="suggestions-expanded animate-slide-up">
          {SUGGESTION_CATEGORIES.map((category) => (
            <div key={category.label} className="suggestion-category">
              <div className="suggestion-category-label">{category.label}</div>
              <div className="suggestion-category-items">
                {category.items.map((item) => (
                  <button
                    key={item}
                    onClick={() => handleSuggestion(item)}
                    className="suggestion-btn suggestion-btn-sm"
                    disabled={isBusy}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ChatInput
