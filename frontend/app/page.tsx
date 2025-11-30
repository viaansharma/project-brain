"use client";
import { useState } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState<any>(null);

  // 1. Function to send message to your Backend
  const sendMessage = async () => {
    if (!input) return;
    const newMsg = { role: "user", content: input };
    setMessages([...messages, newMsg]);
    setLoading(true);
    setInput("");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });
      const data = await res.json();
      
      // Add AI response to chat
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: data.answer, sources: data.sources },
      ]);
    } catch (e) {
      console.error(e);
      setMessages((prev) => [...prev, { role: "ai", content: "⚠️ Error connecting to server." }]);
    }
    setLoading(false);
  };

  // 2. Function to ask for the Door Schedule
  const generateSchedule = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/extract`, {
        method: "POST",
      });
      const data = await res.json();
      setSchedule(data.doors);
      setMessages(prev => [...prev, { role: "ai", content: "✅ I have generated the door schedule." }]);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <main className="flex h-screen bg-gray-50 text-black">
      {/* LEFT PANEL: Door Schedule */}
      <div className="w-1/3 p-6 border-r bg-white overflow-auto hidden md:block">
        <h2 className="text-xl font-bold mb-4 text-blue-800">Project Brain 🧠</h2>
        <p className="text-sm text-black mb-4">Construction Intelligence</p>
        
        <button
          onClick={generateSchedule}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          📄 Generate Door Schedule
        </button>

        {schedule && (
          <div className="mt-6 border rounded shadow-sm overflow-hidden">
            <table className="min-w-full text-xs text-left text-black">
              <thead className="bg-gray-100 uppercase font-medium text-black">
                <tr>
                  <th className="px-3 py-2">Mark</th>
                  <th className="px-3 py-2">Loc</th>
                  <th className="px-3 py-2">Rating</th>
                  <th className="px-3 py-2">Material</th>
                </tr>
              </thead>
              <tbody className="divide-y text-black">
                {schedule.map((door: any, i: number) => (
                  <tr key={i} className="bg-white hover:bg-gray-50">
                    <td className="px-3 py-2 font-bold text-blue-600">{door.mark}</td>
                    <td className="px-3 py-2">{door.location}</td>
                    <td className="px-3 py-2 text-red-600">{door.fire_rating}</td>
                    <td className="px-3 py-2">{door.material}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* RIGHT PANEL: Chat */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        <div className="flex-1 overflow-auto p-4 space-y-6">
          {messages.length === 0 && (
            <div className="text-center text-black mt-20">
              <p>Ask a question about the specs...</p>
              <p className="text-sm">"What is the fire rating?"</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`p-4 max-w-[80%] rounded-2xl ${
                  msg.role === "user" 
                    ? "bg-blue-100 text-black rounded-br-none" 
                    : "bg-white border shadow-sm rounded-bl-none"
                }`}
              >
                {/* --- FIX APPLIED HERE: Forced strict black text on ALL message content --- */}
                <div className="prose text-sm max-w-none text-black [&_*]:text-black">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>

              {/* Citations */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 flex gap-2">
                  {msg.sources.map((s: any, i: number) => (
                    <span key={i} className="text-xs bg-gray-200 text-black px-2 py-1 rounded border">
                      🔍 {s.file} (Pg {s.page})
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && <div className="text-center text-black text-sm animate-pulse">Thinking...</div>}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t">
          <div className="flex gap-2">
            <input
              className="flex-1 border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-black placeholder-gray-500"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask a question..."
            />
            <button 
              onClick={sendMessage} 
              disabled={loading}
              className="bg-black text-white px-6 rounded-lg font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}