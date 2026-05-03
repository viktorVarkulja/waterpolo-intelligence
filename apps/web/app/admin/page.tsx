"use client";

import { useEffect, useState } from "react";

import { api, ScheduleOption } from "../../lib/api";

type LoginResponse = {
  access_token: string;
  token_type: string;
};

export default function AdminPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [season, setSeason] = useState("CL26");
  const [stage, setStage] = useState("");
  const [csvPath, setCsvPath] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<string[]>([]);
  const [apiBase, setApiBase] = useState("");
  const [schedules, setSchedules] = useState<ScheduleOption[]>([]);
  const [calendarUrl, setCalendarUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  useEffect(() => {
    setToken(localStorage.getItem("admin_token"));
    const base =
      window.location.hostname.includes("waterpolo.localhost")
        ? `${window.location.protocol}//waterpolo-api.localhost`
        : process.env.NEXT_PUBLIC_API_URL ||
          (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
            ? "http://localhost:8000"
            : `${window.location.protocol}//waterpolo-api.localhost`);
    setApiBase(base);
  }, []);

  useEffect(() => {
    api
      .options()
      .then((data) => setSchedules(data.schedules))
      .catch(() => pushNotice("Failed to load schedule options."));
  }, []);
  const isLoggedIn = Boolean(token);

  function pushNotice(message: string) {
    setNotifications((prev) => [message, ...prev].slice(0, 5));
  }

  async function handleLogin() {
    setStatus(null);
    pushNotice("Logging in...");
    setIsLoading(true);
    if (!apiBase) {
      setStatus("API base not ready.");
      pushNotice("API base not ready.");
      setIsLoading(false);
      return;
    }
    const res = await fetch(`${apiBase}/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      setStatus("Login failed.");
      pushNotice("Login failed.");
      setIsLoading(false);
      return;
    }
    const data = (await res.json()) as LoginResponse;
    localStorage.setItem("admin_token", data.access_token);
    setToken(data.access_token);
    setStatus("Logged in successfully.");
    pushNotice("Logged in successfully.");
    setIsLoading(false);
  }

  async function handleScrape() {
    if (!token) {
      setStatus("Login required.");
      pushNotice("Login required.");
      return;
    }
    setStatus("Starting scrape...");
    pushNotice("Starting scrape...");
    setIsLoading(true);
    if (!apiBase) {
      setStatus("API base not ready.");
      pushNotice("API base not ready.");
      setIsLoading(false);
      return;
    }
    const res = await fetch(`${apiBase}/admin/scrape/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ season, stage: stage || null, calendar_url: calendarUrl || null })
    });
    if (!res.ok) {
      setStatus("Scrape failed.");
      pushNotice("Scrape failed.");
      setIsLoading(false);
      return;
    }
    setStatus("Scrape started.");
    pushNotice("Scrape started.");
    setIsLoading(false);
  }

  async function handleCsvImport() {
    if (!token) {
      setStatus("Login required.");
      pushNotice("Login required.");
      return;
    }
    setStatus("Importing CSV...");
    pushNotice("Importing CSV...");
    setIsLoading(true);
    if (!apiBase) {
      setStatus("API base not ready.");
      pushNotice("API base not ready.");
      setIsLoading(false);
      return;
    }
    const res = await fetch(`${apiBase}/admin/import/csv`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ path: csvPath || null })
    });
    if (!res.ok) {
      setStatus("Import failed.");
      pushNotice("Import failed.");
      setIsLoading(false);
      return;
    }
    setStatus("Import complete.");
    pushNotice("Import complete.");
    setIsLoading(false);
  }

  return (
    <section className="grid gap-6">
      {isLoading ? (
        <div className="h-1 w-full overflow-hidden rounded-full bg-slate/20">
          <div className="h-full w-1/3 animate-pulse rounded-full bg-wave" />
        </div>
      ) : null}
      <div>
        <h2 className="text-3xl font-semibold">Admin</h2>
        <p className="text-slate">Secure controls for scraping and imports.</p>
      </div>

      <div className="rounded-2xl bg-white/80 p-6 border border-white grid gap-4">
        <h3 className="text-lg font-semibold">Login</h3>
        {isLoggedIn ? (
          <p className="text-sm text-wave">Logged in.</p>
        ) : (
          <p className="text-sm text-slate">Use admin credentials to unlock actions.</p>
        )}
        <p className="text-xs text-slate">API: {apiBase || "..."}</p>
        <div className="grid gap-3 md:grid-cols-2">
          <input
            className="rounded-lg border border-slate/40 px-3 py-2"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            className="rounded-lg border border-slate/40 px-3 py-2"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button
          className="rounded-full bg-ink text-white px-4 py-2 text-sm"
          onClick={handleLogin}
        >
          Sign in
        </button>
      </div>

      <div className="rounded-2xl bg-white/80 p-6 border border-white grid gap-3">
        <h3 className="text-lg font-semibold">Notifications</h3>
        {notifications.length === 0 ? (
          <p className="text-sm text-slate">No recent activity.</p>
        ) : (
          notifications.map((note, idx) => (
            <p key={`${note}-${idx}`} className="text-sm text-slate">
              {note}
            </p>
          ))
        )}
      </div>

      <div className="rounded-2xl bg-white/80 p-6 border border-white grid gap-4">
        <h3 className="text-lg font-semibold">Scrape season</h3>
        <div className="grid gap-3 md:grid-cols-2">
          <input
            className="rounded-lg border border-slate/40 px-3 py-2"
            placeholder="Season (e.g. CL26)"
            value={season}
            onChange={(e) => setSeason(e.target.value)}
          />
          <input
            className="rounded-lg border border-slate/40 px-3 py-2"
            placeholder="Stage (optional)"
            value={stage}
            onChange={(e) => setStage(e.target.value)}
          />
          <select
            className="rounded-lg border border-slate/40 px-3 py-2"
            value={calendarUrl}
            onChange={(e) => setCalendarUrl(e.target.value)}
          >
            <option value="">Use default calendar</option>
            {schedules.map((item) => (
              <option key={item.file} value={`https://len.microplustimingservices.com/lenchampionsleague202526/${item.file}`}>
                {item.date || item.file}
              </option>
            ))}
          </select>
        </div>
        <button
          className="rounded-full bg-wave text-white px-4 py-2 text-sm"
          onClick={handleScrape}
        >
          Run scrape
        </button>
      </div>

      <div className="rounded-2xl bg-white/80 p-6 border border-white grid gap-4">
        <h3 className="text-lg font-semibold">CSV seed</h3>
        <p className="text-sm text-slate">
          Leave empty to use the API default path (recommended for Docker).
        </p>
        <input
          className="rounded-lg border border-slate/40 px-3 py-2"
          placeholder="/data/match_data_correct.csv"
          value={csvPath}
          onChange={(e) => setCsvPath(e.target.value)}
        />
        <button
          className="rounded-full border border-slate/40 px-4 py-2 text-sm"
          onClick={handleCsvImport}
        >
          Import CSV
        </button>
      </div>

      {status ? <p className="text-sm text-slate">{status}</p> : null}
    </section>
  );
}
