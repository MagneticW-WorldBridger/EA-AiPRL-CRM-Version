/**
 * useAprilChat - Chat hook for April Executive Assistant
 * REAL SSE Streaming - Shows tool calls as they happen!
 * 
 * Based on the Woodstock agent's proven streaming architecture
 */
import { useState, useRef, useCallback } from 'react'

// In production: VITE_API_BASE must be set to the backend URL
// In development: Falls back to /api which proxies to localhost:8001
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

// Log API base for debugging
if (import.meta.env.DEV) {
  console.log('[April] API_BASE:', API_BASE)
}

const randomId = (prefix) => `${prefix}_${Math.random().toString(36).slice(2, 10)}`

// Event types for categorization
export const EventType = {
  FUNCTION_CALL: 'function_call',
  FUNCTION_RESPONSE: 'function_response',
  TEXT: 'text',
  TEXT_PARTIAL: 'text_partial',
  ERROR: 'error',
  THINKING: 'thinking'
}

/**
 * Parse an ADK event and categorize it
 */
function parseEvent(event) {
  const parts = event?.content?.parts ?? []
  
  for (const part of parts) {
    // Check for function call
    if (part.functionCall) {
      return {
        type: EventType.FUNCTION_CALL,
        name: part.functionCall.name,
        args: part.functionCall.args,
        raw: event
      }
    }
    
    // Check for function response
    if (part.functionResponse) {
      return {
        type: EventType.FUNCTION_RESPONSE,
        name: part.functionResponse.name,
        response: part.functionResponse.response,
        raw: event
      }
    }
    
    // Check for text
    if (typeof part.text === 'string' && part.text.trim()) {
      return {
        type: event.partial ? EventType.TEXT_PARTIAL : EventType.TEXT,
        text: part.text.trim(),
        raw: event
      }
    }
  }
  
  return { type: EventType.THINKING, raw: event }
}

export function useAprilChat() {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      text: `Hey there! I'm April, your AI Executive Assistant 🚀\n\nI'm connected to your GoHighLevel account and ready to help you:\n\n**📅 Calendar** - Check your schedule, get meeting notes\n**👥 Contacts** - Search, create, update, tag your leads\n**💬 Messages** - Send SMS or emails directly\n**🎯 Pipeline** - Track deals, update stages, close more\n**💳 Payments** - View orders and transactions\n\nJust ask me anything! I'll chain multiple actions together to get you answers fast. Try "Show me my hot deals" or "What meetings do I have this week?"`
    }
  ])
  const [liveEvents, setLiveEvents] = useState([])
  const [status, setStatus] = useState('idle') // idle | loading | streaming
  const [streamingText, setStreamingText] = useState('')
  
  const userIdRef = useRef(randomId('user'))
  const sessionIdRef = useRef(null)
  const abortControllerRef = useRef(null)

  // Create or get session
  const ensureSession = useCallback(async () => {
    if (sessionIdRef.current) {
      return sessionIdRef.current
    }

    const response = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userIdRef.current })
    })

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.status}`)
    }

    const session = await response.json()
    sessionIdRef.current = session.session_id
    return session.session_id
  }, [])

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || status !== 'idle') return

    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', text: text.trim() }])
    setStatus('loading')
    setLiveEvents([])
    setStreamingText('')

    try {
      const sessionId = await ensureSession()
      
      abortControllerRef.current = new AbortController()
      
      // Use SSE endpoint for REAL streaming!
      const sseUrl = `${API_BASE}/run_sse`
      
      const response = await fetch(sseUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userIdRef.current,
          session_id: sessionId,
          message: text.trim()
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || `API error ${response.status}`)
      }

      setStatus('streaming')
      
      // Handle SSE stream - Parse events as they arrive!
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const allEvents = []
      let accumulatedText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.slice(6))
              const parsed = parseEvent(eventData)
              allEvents.push(parsed)
              
              // 🔥 UPDATE LIVE EVENTS IN REAL-TIME!
              if (parsed.type === EventType.FUNCTION_CALL || 
                  parsed.type === EventType.FUNCTION_RESPONSE) {
                setLiveEvents(prev => [...prev, { 
                  ...parsed, 
                  id: Date.now() + Math.random(), 
                  timestamp: new Date() 
                }])
              }
              
              // Accumulate streaming text
              if (parsed.type === EventType.TEXT_PARTIAL || parsed.type === EventType.TEXT) {
                accumulatedText = parsed.text // Replace with latest
                setStreamingText(parsed.text)
              }
            } catch (e) {
              // Skip malformed events
              console.debug('SSE parse error:', e)
            }
          }
        }
      }

      // Extract final text
      const textEvents = allEvents.filter(e => e.type === EventType.TEXT || e.type === EventType.TEXT_PARTIAL)
      const finalText = textEvents.length > 0 
        ? textEvents[textEvents.length - 1].text 
        : accumulatedText || ''
      
      const toolCalls = allEvents.filter(e => e.type === EventType.FUNCTION_CALL)

      // Add agent message with tool badges
      if (finalText.trim()) {
        setMessages(prev => [...prev, {
          role: 'agent',
          text: finalText,
          toolCalls,
          events: allEvents
        }])
      }

    } catch (error) {
      if (error.name !== 'AbortError') {
        setMessages(prev => [...prev, {
          role: 'agent',
          text: `❌ Error: ${error.message}. Please check if the server is running on port 8001.`
        }])
      }
    } finally {
      setStatus('idle')
      setLiveEvents([])
      setStreamingText('')
    }
  }, [status, ensureSession])

  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setMessages([messages[0]])
    setLiveEvents([])
    setStreamingText('')
    setStatus('idle')
    userIdRef.current = randomId('user')
    sessionIdRef.current = null
  }, [messages])

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }, [])

  return {
    messages,
    liveEvents,
    status,
    streamingText,
    sendMessage,
    reset,
    cancelStream
  }
}
