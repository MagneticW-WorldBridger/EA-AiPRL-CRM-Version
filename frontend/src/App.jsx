/**
 * AIPRL Executive Assistant - April
 * Live streaming chat interface with real-time GHL integration
 */
import { useState, useRef, useEffect } from 'react'
import { RotateCcw } from 'lucide-react'
import { useAprilChat } from './hooks/useAprilChat'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import EventFeed from './components/EventFeed'
import './index.css'

function App() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  
  const {
    messages,
    liveEvents,
    status,
    streamingText,
    sendMessage,
    reset,
    cancelStream
  } = useAprilChat()

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, liveEvents, status])

  const handleSend = (text) => {
    const messageText = text || input
    if (messageText.trim()) {
      sendMessage(messageText.trim())
      setInput('')
    }
  }

  const isStreaming = status === 'streaming'
  const isLoading = status === 'loading'

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-brand">
            <div className="brand-avatar">
              A
            </div>
            <div className="brand-text">
              <h1 className="brand-title">April</h1>
              <p className="brand-subtitle">Executive Assistant</p>
            </div>
          </div>
          
          <button
            onClick={reset}
            className="reset-btn"
            title="New conversation"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Messages */}
      <main className="messages-container">
        <div className="messages">
          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
          
          {/* Live Event Feed - Shows during streaming */}
          {(isLoading || isStreaming) && (
            <EventFeed 
              events={liveEvents}
              isStreaming={isLoading || isStreaming}
              streamingText={streamingText}
            />
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="footer">
        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          onCancel={cancelStream}
          status={status}
        />
      </footer>
    </div>
  )
}

export default App


