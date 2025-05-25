"use client";
import { useState } from "react";

export default function Chat({ repoUrl }: { repoUrl: string }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const newMessages = [...messages, { role: "user", text: question }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        body: JSON.stringify({ question, repo_url: repoUrl }),
        headers: { "Content-Type": "application/json" },
      });

      const data = await res.json();
      console.log(data);
      
      newMessages.push({ role: "ai", text: data.answer });
      setMessages(newMessages);
    } catch (err) {
      newMessages.push({ role: "ai", text: "❌ Failed to answer." });
      setMessages(newMessages);
    } finally {
      setLoading(false);
      setQuestion("");
    }
  };

  return (
    <div className="mt-8">
      <div className="space-y-4 max-h-[60vh] overflow-y-auto mb-4 p-4 border rounded bg-white shadow">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-2 rounded ${msg.role === "user" ? "bg-blue-100 text-right" : "bg-gray-100 text-left"}`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          className="flex-grow px-4 py-2 border rounded"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the repo..."
        />
        <button
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          onClick={sendQuestion}
        >
          {loading ? "⏳" : "Send"}
        </button>
      </div>
    </div>
  );
}
