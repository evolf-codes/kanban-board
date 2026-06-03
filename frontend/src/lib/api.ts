export async function readJson<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new Error(
      "API returned an unexpected response. Open http://localhost:8000 (not port 3000)."
    );
  }

  return response.json() as Promise<T>;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(path, {
      credentials: "include",
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch {
    throw new Error(
      "Cannot reach the API. Use http://localhost:8000 after running ./scripts/start.sh."
    );
  }

  if (!response.ok) {
    throw new Error("Request failed.");
  }

  return readJson<T>(response);
}
