"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Send, Globe, Sparkles } from "lucide-react"
import { ChatMessage } from "@/components/chat-message"
import { LoadingDots } from "@/components/loading-dots"
import { cn } from "@/lib/utils"
import { toast } from 'sonner'
import Image from "next/image"


interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
  citations?: string[]
}

export default function UngithubChat() {
  const [messages, setMessages] = useState<Message[]>([])

  const [inputValue, setInputValue] = useState("")
  const [urlValue, setUrlValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const [loadingMessage, setLoadingMessage] = useState("AI is thinking...")
  const LOCAL_URI = process.env.NEXT_PUBLIC_LOCAL_URI
  const PROD_URI = process.env.NEXT_PUBLIC_PROD_URI


  useEffect(() => {
    setMessages([
      {
        id: "1",
        content:
          "Hello! I'm Ungithub AI. I can help you analyze GitHub repositories, understand code, and answer questions about development projects. What would you like to explore today?",
        role: "assistant",
        timestamp: new Date(),
      },
    ])
    if (typeof window !== "undefined") {
      const path = window.location.pathname // "/jayanth920/t2s-s2t"
      const parts = path.split("/").filter(Boolean)
      if (parts.length === 2) {
        const [owner, repo] = parts
        setUrlValue(`https://github.com/${owner}/${repo}`)
      }
    }
  }, [])


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    setLoadingMessage("AI is thinking...")
    setIsLoading(true)

    // ✅ Local check: 1000 characters or 2048 tokens max
    if (inputValue.length > 1000) {
      toast.error("❌ Your question is too long. Please shorten it to 1000 characters or less.")
      return
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      role: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    // Timer to show alert after 10 seconds if still indexing
    const indexingTimeout = setTimeout(() => {
      toast.info("📦 Still reading your repo... try again in a few more seconds if nothing shows up.")
    }, 10 * 1000)

    try {
      const res = await fetch(`${PROD_URI}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: urlValue, question: userMessage.content }),
      })

      // Cancel the delayed indexing alert once response is back
      clearTimeout(indexingTimeout)

      const data = await res.json()

      console.log("data: ", data)

      if (res.status === 202 && data.status === "indexing") {
        // Repo is being indexed
        console.log("Repo is being indexed. Please wait...")
        const indexingMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "🔍 Reading your repo... Please wait a moment and try again.",
          role: "assistant",
          timestamp: new Date(),
        }

        setLoadingMessage("Repo is being indexed. Please wait...")
        setMessages((prev) => [...prev, indexingMessage])
        toast.info("⏳ Repo is being indexed. Try asking again in a few seconds.")
        return
      }

      if (!res.ok) {
        toast.error(`⚠️ ${data.detail || "An error occurred."}`)
        return
      }

      const aiMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: data.answer || "Sorry, I couldn't find an answer.",
        role: "assistant",
        timestamp: new Date(),
        citations: data.citations || [],
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (err) {
      clearTimeout(indexingTimeout)
      console.error("Error fetching AI response:", err)
      toast.error("🚨 Failed to fetch response.")
    } finally {
      setIsLoading(false)
    }
  }


  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated background elements */}
      {/* <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse delay-500"></div>
      </div> */}

      {/* Main container */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="p-6">
          <div className="max-w-4xl mx-auto">
            <Card className="bg-black/20 backdrop-blur-xl border border-white/10 shadow-2xl">
              <div className="p-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="flex items-center space-x-3">
                    {/* <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                      <span className="text-xl">💬</span>
                    </div> */}
                    <Image src="/logo.png" alt="Ungithub Logo" width={50} height={50} className="rounded-full" />
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent text-center">
                      Ungithub Chat
                    </h1>
                  </div>
                </div>

                {/* URL Input */}
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white" />
                  <Input
                    value={urlValue}
                    onChange={(e) => setUrlValue(e.target.value)}
                    placeholder="Enter GitHub repository URL..."
                    className="pl-10 bg-white/5 border-white/10 text-white placeholder-gray-300 focus:border-purple-400 focus:ring-purple-400/20"
                  />
                </div>
              </div>
            </Card>
          </div>
        </header>

        {/* Chat messages */}
        <main className="flex-1 p-6 pb-32 overflow-y-auto scroll-smooth">
          <div className="w-full mx-auto max-w-4xl space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} urlValue={urlValue} />
            ))}
            {isLoading && (
              <div className="flex justify-start mt-4">
                <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-4 max-w-xs">
                  <LoadingDots text={loadingMessage} />
                </div>
              </div>
            )}
            <div className="h-28" />
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Floating input area */}
        <div className="fixed bottom-0 left-0 w-full px-6 pb-6">
          <div className="h-[25vh] max-w-4xl mx-auto bg-black/30 backdrop-blur-xl border border-white/10 rounded-xl pl-4 pt-4 pb-4 shadow-2xl">
            <div className="flex h-fit">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about the repository..."
                className="w-[96%] rounded-lg resize-none flex-1 bg-white/5 border-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400/20 focus:border-purple-400 p-2 h-[20vh]"
                disabled={isLoading}
              />

              <button
                className={cn(
                  "m-4 p-2 w-10 h-10 rounded-full cursor-pointer bg-amber-50 shadow-[0_4px_10px_rgba(0,0,0,0.25)] transition-all duration-300 ease-in-out active:translate-y-[1px] active:shadow-sm",
                  inputValue.trim() && !isLoading
                    ? "opacity-80 pointer-events-auto"
                    : "opacity-0 pointer-events-none"
                )}
                onClick={handleSendMessage}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-6 h-6 text-black"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M7 17L17 7M7 7h10v10"
                  />
                </svg>
              </button>

            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
