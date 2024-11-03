'use client'

import { ArrowRight, Music, Play, Pause, SkipBack, SkipForward } from 'lucide-react'
import { useEffect, useState } from 'react'

const educationMessages = [
  { type: 'user', message: 'Hey TuneTutor, teach me calculus' },
  { type: 'tutor', message: 'Here\'s a catchy tune about derivatives and integrals!' },

]

const viralMessages = [
  { type: 'user', message: 'Hey TuneTutor, generate a song on how much I hate AI' },
  { type: 'tutor', message: ':( Okay, here\'s a jingle, but :(' },
]

export default function HeroSection() {
  const [visibleEducationMessages, setVisibleEducationMessages] = useState<{ type: string; message: string }[]>([])
  const [visibleViralMessages, setVisibleViralMessages] = useState<{ type: string; message: string }[]>([])
  const [isTyping, setIsTyping] = useState({ education: false, viral: false })

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | undefined

    const showMessages = (messages: typeof educationMessages, setMessages: React.Dispatch<React.SetStateAction<{ type: string; message: string }[]>>, typingKey: 'education' | 'viral', index = 0) => {
      if (index >= messages.length) return
      const currentMessage = messages[index]

      setMessages((prev) => [...prev, currentMessage])

      if (currentMessage.type === 'user') {
        timeoutId = setTimeout(() => {
          setIsTyping((prev) => ({ ...prev, [typingKey]: true }))
          timeoutId = setTimeout(() => {
            setIsTyping((prev) => ({ ...prev, [typingKey]: false }))
            showMessages(messages, setMessages, typingKey, index + 1)
          }, 1000) // Tutor typing time
        }, 800) // Delay before tutor starts typing
      } else {
        timeoutId = setTimeout(() => showMessages(messages, setMessages, typingKey, index + 1), 1500) // Delay before next user message
      }
    }

    showMessages(educationMessages, setVisibleEducationMessages, 'education')
    showMessages(viralMessages, setVisibleViralMessages, 'viral')

    return () => clearTimeout(timeoutId)
  }, [])

  return (
    <section className="relative w-full bg-gradient-to-b from-st-tropaz to-bright-green text-white py-20 overflow-hidden">
      <div className="container mx-auto grid grid-cols-1 md:grid-cols-3 gap-4 px-4 relative z-10">
        {/* Left Column for Education Messages */}
        <div className="flex flex-col items-start space-y-4 h-[400px] order-2 md:order-1">
          <h2 className="text-2xl font-bold mb-4">Educational Tunes</h2>
          <div className="space-y-4">
            {visibleEducationMessages.map((chat, index) => (
              <ChatMessage 
                key={index} 
                type={chat.type} 
                message={chat.message} 
                className="animate-slideInLeft"
              />
            ))}
            {isTyping.education && <TypingIndicator />}
          </div>
        </div>

        {/* Center Column for Hero Content */}
        <div className="text-center order-1 md:order-2 mb-8 md:mb-0">
          <div className="flex justify-center mb-8">
            <Music className="h-24 w-24 animate-bounce" />
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-4 animate-pulse">
            Welcome to TuneTutor
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-2xl mx-auto">
            Transform knowledge into catchy tunes that stick! Learn anything through the power of music.
          </p>
          <button
            className="bg-white text-st-tropaz px-8 py-4 rounded-full text-lg font-semibold hover:bg-opacity-90 transition-transform transform hover:scale-105 flex items-center mx-auto"
            onClick={() =>
              document
                .getElementById('topic-input')
                ?.scrollIntoView({ behavior: 'smooth' })
            }
          >
            Get Started
            <ArrowRight className="ml-2 h-5 w-5" />
          </button>
        </div>

        {/* Right Column for Viral Messages */}
        <div className="flex flex-col items-end space-y-4 h-[400px] order-3">
          <h2 className="text-2xl font-bold mb-4 self-start">Viral Hits</h2>
          <div className="space-y-4">
            {visibleViralMessages.map((chat, index) => (
              <ChatMessage 
                key={index} 
                type={chat.type} 
                message={chat.message} 
                className="animate-slideInRight"
              />
            ))}
            {isTyping.viral && <TypingIndicator />}
          </div>
        </div>
      </div>
    </section>
  )
}

function ChatMessage({ type, message, className = '' }: { type: string; message: string; className?: string }) {
  const alignmentClass = type === 'user' ? 'justify-start' : 'justify-end'
  const bgColor =
    type === 'user' ? 'bg-white text-st-tropaz' : 'bg-tutor-response text-white'

  return (
    <div
      className={`flex ${alignmentClass} w-full max-w-sm ${className} mb-4`}
    >
      <div
        className={`rounded-lg px-4 py-2 max-w-[75%] ${
          type === 'user' ? 'rounded-bl-none' : 'rounded-br-none'
        } ${bgColor}`}
      >
        {message}
        {type === 'tutor' && <MusicPlayer />}
      </div>
    </div>
  )
}

function MusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    let intervalId: NodeJS.Timeout | undefined

    if (isPlaying) {
      intervalId = setInterval(() => {
        setProgress((prevProgress) => {
          if (prevProgress >= 100) {
            setIsPlaying(false)
            return 0
          }
          return prevProgress + 1
        })
      }, 100)
    }

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [isPlaying])

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleSkipBack = () => {
    setProgress(0)
  }

  const handleSkipForward = () => {
    setProgress(100)
    setIsPlaying(false)
  }

  return (
    <div className="mt-2 bg-white rounded-lg p-2 text-tutor-response">
      <div className="flex items-center justify-between">
        <SkipBack size={20} className="cursor-pointer" onClick={handleSkipBack} />
        {isPlaying ? (
          <Pause size={24} className="cursor-pointer" onClick={handlePlayPause} />
        ) : (
          <Play size={24} className="cursor-pointer" onClick={handlePlayPause} />
        )}
        <SkipForward size={20} className="cursor-pointer" onClick={handleSkipForward} />
      </div>
      <div className="mt-2 bg-gray-200 rounded-full h-1">
        <div 
          className="bg-tutor-response h-1 rounded-full transition-all duration-100 ease-linear"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-end w-full max-w-sm mb-4">
      <div className="bg-tutor-response text-white rounded-lg rounded-br-none px-4 py-2 max-w-[75%]">
        <div className="flex space-x-1">
          <div className="dot w-2 h-2 bg-white rounded-full animate-bounce"></div>
          <div className="dot w-2 h-2 bg-white rounded-full animate-bounce delay-100"></div>
          <div className="dot w-2 h-2 bg-white rounded-full animate-bounce delay-200"></div>
        </div>
      </div>
    </div>
  )
}