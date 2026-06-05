"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import { fetchSession, logout } from "@/lib/auth";

export const AppGate = () => {
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchSession()
      .then((session) => {
        if (!active) {
          return;
        }

        setError(null);
        setUsername(session.authenticated ? session.username : null);
      })
      .catch((sessionError) => {
        if (active) {
          setUsername(null);
          setError(
            sessionError instanceof Error
              ? sessionError.message
              : "Unable to reach the API."
          );
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const handleLogout = async () => {
    await logout();
    setUsername(null);
  };

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center px-6">
        <p className="text-sm text-[var(--gray-text)]">Loading...</p>
      </main>
    );
  }

  if (!username) {
    return (
      <>
        {error ? (
          <main className="mx-auto max-w-lg px-6 py-6">
            <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
              {error}
            </p>
          </main>
        ) : null}
        <LoginForm onSuccess={setUsername} onAttempt={() => setError(null)} />
      </>
    );
  }

  return <KanbanBoard username={username} onLogout={handleLogout} />;
};
