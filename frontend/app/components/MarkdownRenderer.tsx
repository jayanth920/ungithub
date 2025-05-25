"use client"
import React from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { lucario as theme } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="overflow-x-auto">
      <div className="prose prose-invert prose-sm max-w-none">
        <ReactMarkdown
          components={{
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <SyntaxHighlighter
                  style={theme}
                  language={match[1]}
                  customStyle={{
                    background: "#011627",
                    padding: "1rem",
                    borderRadius: "8px",
                    border: "1px solid #1e293b",
                    fontSize: "15px",
                    margin: "1rem 0",
                    overflowX: "auto"
                  }}
                  {...props}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              ) : (
                <code className="bg-blue-900 p-1 rounded" {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}
// d