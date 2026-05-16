"use client";

import { useState } from "react";
import { querySalary, QueryResponse } from "@/lib/api";

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await querySalary(query);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main dir="rtl" style={{ minHeight: "100vh", background: "linear-gradient(160deg, #f0f4ff 0%, #e8eeff 40%, #f0f9ff 100%)", fontFamily: "sans-serif" }}>

      {/* Glow blobs */}
      <div style={{ position: "fixed", top: -200, right: -200, width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(99,102,241,0.12), transparent)", pointerEvents: "none" }} />
      <div style={{ position: "fixed", bottom: -200, left: -200, width: 500, height: 500, borderRadius: "50%", background: "radial-gradient(circle, rgba(59,130,246,0.1), transparent)", pointerEvents: "none" }} />

      {/* Header */}
      <header style={{ borderBottom: "1px solid rgba(99,102,241,0.1)", background: "rgba(255,255,255,0.7)", backdropFilter: "blur(12px)", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: 760, margin: "0 auto", padding: "14px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg, #6366f1, #3b82f6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>🔍</div>
            <span style={{ fontWeight: 700, fontSize: 16, color: "#1e1b4b" }}>Salary Intel</span>
          </div>
          <span style={{ fontSize: 12, color: "#6366f1", background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.15)", borderRadius: 20, padding: "4px 12px" }}>
            🇮🇱 שוק ההייטק הישראלי
          </span>
        </div>
      </header>

      {/* Hero */}
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "60px 24px 32px", textAlign: "center" }}>

        {/* Badge */}
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "white", border: "1px solid rgba(99,102,241,0.2)", borderRadius: 24, padding: "6px 16px", fontSize: 13, color: "#6366f1", marginBottom: 28, boxShadow: "0 2px 12px rgba(99,102,241,0.08)" }}>
          <span style={{ width: 8, height: 8, background: "#4ade80", borderRadius: "50%", display: "inline-block", animation: "pulse 2s infinite" }} />
          מבוסס על קבוצת הפייסבוק ״משכורות בהייטקס״
          </div>

        {/* Headline */}
        <h1 style={{ fontSize: 52, fontWeight: 800, lineHeight: 1.15, color: "#1e1b4b", marginBottom: 16 }}>
          כמה אתה{" "}
          <span style={{ background: "linear-gradient(90deg, #6366f1 0%, #3b82f6 100%)", backgroundClip: "text", WebkitBackgroundClip: "text", color: "transparent", WebkitTextFillColor: "transparent", display: "inline-block" }}>
            שווה?
          </span>
        </h1>

        <p style={{ fontSize: 17, color: "#64748b", marginBottom: 36, lineHeight: 1.6 }}>
          תובנות שכר חכמות מבוססות AI — ממאות דיונים אמיתיים בקהילת ההייטק הישראלית
        </p>

        {/* Search box */}
        <form onSubmit={handleSubmit}>
          <div style={{ display: "flex", gap: 8, background: "white", border: "1.5px solid rgba(99,102,241,0.2)", borderRadius: 18, padding: 8, boxShadow: "0 8px 32px rgba(99,102,241,0.1)" }}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="כמה מרוויח מפתח React עם 4 שנות ניסיון בתל אביב?"
              disabled={loading}
              style={{ flex: 1, background: "transparent", border: "none", outline: "none", padding: "12px 16px", fontSize: 15, color: "#1e1b4b", textAlign: "right", direction: "rtl" }}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              style={{ padding: "12px 24px", borderRadius: 12, border: "none", cursor: loading || !query.trim() ? "not-allowed" : "pointer", background: "linear-gradient(135deg, #6366f1, #3b82f6)", color: "white", fontWeight: 600, fontSize: 15, opacity: loading || !query.trim() ? 0.6 : 1, transition: "all 0.2s", display: "flex", alignItems: "center", gap: 8 }}
            >
              {loading ? (
                <>
                  <span style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTop: "2px solid white", borderRadius: "50%", display: "inline-block", animation: "spin 0.8s linear infinite" }} />
                  מחפש
                </>
              ) : "חפש →"}
            </button>
          </div>
        </form>

        {/* Example chips */}
        <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap", justifyContent: "center" }}>
          {["כמה מרוויח DevOps בכיר?", "שכר data scientist מתחיל", "מה מקבל team lead בפינטק?"].map((ex) => (
            <button
              key={ex}
              onClick={() => setQuery(ex)}
              style={{ fontSize: 13, color: "#6366f1", background: "white", border: "1px solid rgba(99,102,241,0.15)", borderRadius: 20, padding: "6px 14px", cursor: "pointer", transition: "all 0.2s", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "0 24px 80px" }}>

        {error && (
          <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 16, padding: 16, color: "#dc2626", fontSize: 14 }}>
            {error}
          </div>
        )}

        {loading && (
          <div style={{ textAlign: "center", padding: "64px 0" }}>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "conic-gradient(from 0deg, #6366f1, #3b82f6, #e0e7ff)", animation: "spin 1s linear infinite", margin: "0 auto 16px" }} />
            <p style={{ color: "#94a3b8", fontSize: 14 }}>מחפש בנתוני הקהילה...</p>
          </div>
        )}

        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Answer card */}
            <div style={{ background: "linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%)", border: "1.5px solid rgba(99,102,241,0.15)", borderRadius: 20, padding: 28, boxShadow: "0 8px 32px rgba(99,102,241,0.08)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #6366f1, #3b82f6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>💡</div>
                  <span style={{ fontWeight: 700, fontSize: 16, color: "#1e1b4b" }}>תשובה</span>
                </div>
                <span style={{ fontSize: 12, color: "#94a3b8", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 20, padding: "4px 12px" }}>
                  מבוסס על {result.posts_used} פוסטים
                </span>
              </div>
              <p style={{ color: "#334155", lineHeight: 1.8, fontSize: 15, whiteSpace: "pre-wrap" }}>
                {result.answer}
              </p>
            </div>

            {/* Sources */}
            {result.sources.length > 0 && (
              <div>
                <p style={{ color: "#94a3b8", fontSize: 13, marginBottom: 10, paddingRight: 4 }}>מקורות</p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {result.sources.map((source) => (
                    <div
                      key={source.id}
                      style={{ background: "white", border: "1px solid #e8eeff", borderRadius: 16, padding: 18, boxShadow: "0 2px 8px rgba(0,0,0,0.04)", transition: "all 0.2s" }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8, flexWrap: "wrap" }}>
                        <span style={{ fontWeight: 600, fontSize: 14, color: "#1e1b4b" }}>{source.role}</span>
                        {source.salary && (
                          <span style={{ fontWeight: 700, fontSize: 13, background: "linear-gradient(135deg, #ede9fe, #dbeafe)", color: "#4f46e5", borderRadius: 8, padding: "3px 10px" }}>
                            ₪{source.salary.toLocaleString()}
                          </span>
                        )}
                        {source.years_experience && (
                          <span style={{ fontSize: 12, color: "#94a3b8" }}>{source.years_experience} שנים</span>
                        )}
                        {source.location && (
                          <span style={{ fontSize: 12, color: "#94a3b8" }}>📍 {source.location}</span>
                        )}
                        <span style={{ fontSize: 11, color: "#cbd5e1", marginRight: "auto" }}>
                          {Math.round(source.similarity * 100)}% התאמה
                        </span>
                      </div>
                      <p style={{ color: "#64748b", fontSize: 13, lineHeight: 1.6 }}>{source.raw_text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
    </main>
  );
}