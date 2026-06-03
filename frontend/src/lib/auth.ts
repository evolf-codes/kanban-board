import { readJson } from "@/lib/api";

export type SessionResponse = {
  authenticated: boolean;
  username: string | null;
};

export type LoginResponse = {
  username: string;
};

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message =
      response.status === 401 ? "Invalid username or password." : "Request failed.";
    throw new Error(message);
  }

  return readJson<T>(response);
}

export async function fetchSession(): Promise<SessionResponse> {
  let response: Response;

  try {
    response = await fetch("/api/auth/session", {
      credentials: "include",
    });
  } catch {
    throw new Error(
      "Cannot reach the API. Use http://localhost:8000 after running ./scripts/start.sh."
    );
  }

  if (!response.ok) {
    throw new Error("Unable to load session.");
  }

  return readJson<SessionResponse>(response);
}

export async function login(
  username: string,
  password: string
): Promise<LoginResponse> {
  let response: Response;

  try {
    response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });
  } catch {
    throw new Error(
      "Cannot reach the API. Use http://localhost:8000 after running ./scripts/start.sh."
    );
  }

  return parseJson<LoginResponse>(response);
}

export async function logout(): Promise<void> {
  const response = await fetch("/api/auth/logout", {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Logout failed.");
  }
}
