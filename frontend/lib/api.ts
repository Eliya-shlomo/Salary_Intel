export interface Source {
  id: number;
  role: string;
  salary: number;
  years_experience: number;
  location: string;
  raw_text: string;
  similarity: number;
}

export interface QueryResponse {
  answer: string;
  posts_used: number;
  sources: Source[];
}

export interface AnalystResponse {
  answer: string | null;
  verified: boolean;
  unsupported: number[];
  message: string | null;
}

// Both calls go to our own Next.js server, which adds the API key and forwards to the backend
async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Server error");
  }

  return response.json();
}

export function querySalary(query: string): Promise<QueryResponse> {
  return post("/api/query", { query });
}

export function askAnalyst(question: string): Promise<AnalystResponse> {
  return post("/api/analyst/ask", { question });
}
