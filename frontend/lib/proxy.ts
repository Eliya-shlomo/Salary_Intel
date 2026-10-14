const API_URL =
  process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || "http://localhost:8000";

// Server-only: API_KEY has no NEXT_PUBLIC_ prefix, so the browser never receives it
export async function forwardToBackend(path: string, body: unknown): Promise<Response> {
  const apiKey = process.env.API_KEY;
  if (!apiKey) {
    return Response.json({ detail: "Server is not configured" }, { status: 500 });
  }

  try {
    const upstream = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
      body: JSON.stringify(body),
    });
    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return Response.json({ detail: "Backend is unreachable" }, { status: 502 });
  }
}
