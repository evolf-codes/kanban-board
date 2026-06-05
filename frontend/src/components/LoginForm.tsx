"use client";

import { FormEvent, useState } from "react";
import { login } from "@/lib/auth";

type LoginFormProps = {
  onSuccess: (username: string) => void;
  onAttempt?: () => void;
};

export const LoginForm = ({ onSuccess, onAttempt }: LoginFormProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    onAttempt?.();
    setSubmitting(true);

    try {
      const response = await login(username, password);
      onSuccess(response.username);
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : "Unable to sign in."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="relative mx-auto flex min-h-screen max-w-lg flex-col justify-center px-6 py-16">
      <section className="rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
          Project Management MVP
        </p>
        <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
          Sign in
        </h1>
        <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
          Use the demo credentials to access your Kanban board.
        </p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <label className="block space-y-2 text-sm font-medium text-[var(--navy-dark)]">
            <span>Username</span>
            <input
              className="w-full rounded-xl border border-[var(--stroke)] px-4 py-3 outline-none focus:border-[var(--primary-blue)]"
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>

          <label className="block space-y-2 text-sm font-medium text-[var(--navy-dark)]">
            <span>Password</span>
            <input
              className="w-full rounded-xl border border-[var(--stroke)] px-4 py-3 outline-none focus:border-[var(--primary-blue)]"
              type="password"
              name="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          {error ? (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          ) : null}

          <button
            className="w-full rounded-xl bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={submitting}
          >
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
};
