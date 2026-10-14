import { forwardToBackend } from "@/lib/proxy";

export async function POST(request: Request) {
  const { question } = await request.json();
  return forwardToBackend("/api/v1/analyst/ask", { question });
}
