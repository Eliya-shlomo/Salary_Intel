// No API_KEY here — the browser never sees it
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
    // Calls our own Next.js server, not the backend directly
    const response = await fetch("/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });
  
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Server error");
    }
  
    return response.json();
  }