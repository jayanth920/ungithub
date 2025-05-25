"use client";
import { useState } from "react";

export default function RepoInput({ setRepoUrl, setRepoIndexed, loading, setLoading }: any) {
  const [inputUrl, setInputUrl] = useState("");

  const handleSubmit = async () => {
    if (!inputUrl) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        body: JSON.stringify({ question: "whats the name of this repo?", repo_url: inputUrl }),
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) throw new Error("Failed to index");
      setRepoUrl(inputUrl);
      setRepoIndexed(true);
    } catch (e) {
        console.error(e);
      alert("Failed to index repo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex gap-2">
      <input
        className="flex-grow px-4 py-2 border rounded text-slate-900"
        type="text"
        placeholder="Enter GitHub repo URL..."
        value={inputUrl}
        onChange={(e) => setInputUrl(e.target.value)}
      />
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        onClick={handleSubmit}
      >
        {loading ? "🔄" : "➡️"}
      </button>
    </div>
  );
}
