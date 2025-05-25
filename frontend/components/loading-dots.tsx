"use client"

export function LoadingDots({text}: {text?: string}) {
  return (
    <div className="flex items-center space-x-1">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100"></div>
        <div className="w-2 h-2 bg-teal-400 rounded-full animate-bounce delay-200"></div>
      </div>
      <span className="text-gray-400 text-sm ml-2">{text}</span>
    </div>
  )
}
