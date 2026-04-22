/**
 * VIDER Chat API Service
 *
 * Handles communication between the frontend and the FastAPI backend.
 * Base URL is configurable via VITE_API_URL environment variable.
 */

// In development: http://localhost:8000
// In production: set VITE_API_URL to your backend server URL
const API_BASE_URL: string = import.meta.env.VITE_API_URL || "http://localhost:8000";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

export interface ChatApiResponse {
  reply: string;
  message_id?: number;
}

export interface HistoryMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface ChatApiError {
  detail: string;
}

/* ------------------------------------------------------------------ */
/* API functions                                                       */
/* ------------------------------------------------------------------ */

/**
 * Send a chat message to the backend and receive an AI-generated reply.
 *
 * @param username - The current user's username
 * @param message  - The message text to send
 * @returns        - The AI's reply and optional message ID
 * @throws         - Error with descriptive message on failure
 */
export async function sendMessage(
  username: string,
  message: string,
): Promise<ChatApiResponse> {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, message }),
  });

  if (!res.ok) {
    const err: ChatApiError = await res.json().catch(() => ({
      detail: `Server error (${res.status})`,
    }));
    throw new Error(err.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

/**
 * Fetch chat history for a user.
 *
 * @param username - The user whose history to retrieve
 * @param limit    - Max number of messages (default 50)
 */
export async function fetchHistory(
  username: string,
  limit = 50,
): Promise<HistoryMessage[]> {
  const params = new URLSearchParams({ username, limit: String(limit) });
  const res = await fetch(`${API_BASE_URL}/chat/history?${params}`);

  if (!res.ok) {
    throw new Error(`Failed to fetch history (${res.status})`);
  }

  return res.json();
}

/**
 * Check if the backend is reachable.
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    return res.ok;
  } catch {
    return false;
  }
}
