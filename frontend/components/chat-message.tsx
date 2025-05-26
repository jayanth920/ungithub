"use client"

import MarkdownRenderer from "@/components/MarkdownRenderer"
import { Card } from "@/components/ui/card"
import { User, Bot } from "lucide-react"

interface Message {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
  citations?: string[]
}

interface ChatMessageProps {
  message: Message
  urlValue?: string | undefined
}

export function ChatMessage({ message, urlValue }: ChatMessageProps) {
  const isUser = message.role === "user"

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-in slide-in-from-bottom-2 duration-300`}>
      <div className={`flex items-start space-x-3 max-w-[80%] ${isUser ? "flex-row-reverse space-x-reverse" : ""}`}>
        {/* Avatar */}
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? "bg-gradient-to-r from-purple-500 to-blue-500" : "bg-gradient-to-r from-emerald-500 to-teal-500"
            }`}
        >
          {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
        </div>

        {/* Message Content */}
        <Card
          className={`${isUser
            ? "bg-gradient-to-r from-purple-500/20 to-blue-500/20 border-purple-400/30"
            : "bg-white/5 border-white/10"
            } backdrop-blur-sm shadow-lg`}
        >
          <div className="p-4">
            <div className={`text-sm ${isUser ? "text-white" : "text-gray-100"}`}>
              <MarkdownRenderer content={message.content} />
            </div>

            {/* Timestamp */}
            <div className={`text-xs mt-1 ${isUser ? "text-purple-200" : "text-gray-400"}`}>
              {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </div>

            {/* Citations */}
            {!isUser && (message.citations?.length ?? 0) > 0 && (
              <div className="mt-3 text-xs text-purple-300 border-t border-white/10 pt-2">
                <span className="font-semibold">📄 Sources:</span>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  {message.citations?.map((path, idx) => (
                    <li key={idx} className="truncate">
                      <code>{path.split("/").pop()}</code>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>

      </div>
    </div>
  )
}
