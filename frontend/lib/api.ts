const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

export async function querySalary(query: string): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/api/v1/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "שגיאה בשרת");
  }

  return response.json();
}