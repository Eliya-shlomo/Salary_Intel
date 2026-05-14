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
      setError(err instanceof Error ? err.message : "שגיאה לא צפויה");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50" dir="rtl">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">
            🔍 Salary Intel
          </h1>
          <p className="text-gray-500 mt-1 text-sm">
            תובנות שכר מבוססות נתונים אמיתיים מהקהילה הישראלית
          </p>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Search Form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="כמה מרוויח מפתח React עם 4 שנות ניסיון בתל אביב?"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "מחפש..." : "חפש"}
          </button>
        </form>

        {/* Example Queries */}
        <div className="flex gap-2 mt-3 flex-wrap">
          {[
            "כמה מרוויח DevOps בכיר?",
            "שכר data scientist מתחיל",
            "מה מקבל team lead בפינטק?",
          ].map((example) => (
            <button
              key={example}
              onClick={() => setQuery(example)}
              className="text-sm text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1 rounded-full transition-colors"
            >
              {example}
            </button>
          ))}
        </div>

        {/* Error */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mt-8 flex flex-col items-center gap-3 text-gray-500">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
            <p className="text-sm">מחפש בנתוני הקהילה...</p>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-6 space-y-4">
            {/* Answer */}
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">💡</span>
                <h2 className="font-semibold text-gray-900">תשובה</h2>
                <span className="text-xs text-gray-400 mr-auto">
                  מבוסס על {result.posts_used} פוסטים
                </span>
              </div>
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {result.answer}
              </p>
            </div>

            {/* Sources */}
            {result.sources.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-2">
                  מקורות
                </h3>
                <div className="space-y-2">
                  {result.sources.map((source) => (
                    <div
                      key={source.id}
                      className="bg-white border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-medium text-gray-900 text-sm">
                          {source.role}
                        </span>
                        <span className="text-blue-600 font-semibold text-sm">
                          ₪{source.salary?.toLocaleString()}
                        </span>
                        <span className="text-gray-400 text-xs">
                          {source.years_experience} שנים
                        </span>
                        {source.location && (
                          <span className="text-gray-400 text-xs">
                            📍 {source.location}
                          </span>
                        )}
                        <span className="text-gray-300 text-xs mr-auto">
                          {Math.round(source.similarity * 100)}% התאמה
                        </span>
                      </div>
                      <p className="text-gray-500 text-sm leading-relaxed">
                        {source.raw_text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}