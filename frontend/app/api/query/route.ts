import { forwardToBackend } from "@/lib/proxy";

export async function POST(request: Request) {
  const { query } = await request.json();
  return forwardToBackend("/api/v1/query", { query });
}
