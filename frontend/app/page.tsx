"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

const VIBES = ["Cultural", "Adventure", "Relaxed", "Foodie", "Luxury", "Budget"];

export default function Home() {
  const router = useRouter();
  const [form, setForm] = useState({
    source: "",
    dates: "",
    budget: 2000,
    travel_style: "Cultural",
    preferences: [] as string[],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const togglePref = (v: string) => {
    setForm(f => ({
      ...f,
      preferences: f.preferences.includes(v)
        ? f.preferences.filter(p => p !== v)
        : [...f.preferences, v],
    }));
  };

  const handleSubmit = async () => {
    if (!form.source || !form.destination || !form.dates) {
      setError("Please fill in source, destination and dates.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: form.source,
          destination: form.destination,
          dates: form.dates,
          budget: String(form.budget),
          travel_style: form.travel_style.toLowerCase(),
          preferences: form.preferences,
        }),
      });
      const data = await res.json();
      if (data.thread_id) {
        router.push(`/planning?thread_id=${data.thread_id}&destination=${encodeURIComponent(form.destination)}&dates=${encodeURIComponent(form.dates)}&budget=${form.budget}`);
      } else {
        setError("Something went wrong. Try again.");
      }
    } catch {
      setError("Cannot connect to backend. Is the server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="text-5xl mb-3">✈️</div>
        <h1 className="text-4xl font-bold text-teal-700 tracking-tight">AI Trip Planner</h1>
        <p className="text-gray-500 mt-2 text-lg">Tell us where you want to go. We'll handle the rest.</p>
      </div>

      {/* Card */}
      <div className="w-full max-w-xl bg-white rounded-3xl shadow-xl p-8 flex flex-col gap-6">

        {/* Source */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">From (Source)</label>
          <input
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-400"
            placeholder="e.g. Delhi, New York"
            value={form.source}
            onChange={e => setForm(f => ({ ...f, source: e.target.value }))}
          />        </div>

        {/* Destination */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Destination</label>
          <input
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-400"
            placeholder="e.g. Paris, Tokyo, Goa"
            value={form.destination}
            onChange={e => setForm(f => ({ ...f, destination: e.target.value }))}
          />
        </div>

        {/* Dates */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Travel Dates</label>
          <input
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-teal-400"
            placeholder="e.g. 2025-08-01 to 2025-08-05"
            value={form.dates}
            onChange={e => setForm(f => ({ ...f, dates: e.target.value }))}
          />
        </div>

        {/* Budget */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">
            Budget: <span className="text-teal-600 font-bold">${form.budget}</span>
          </label>
          <input
            type="range" min={300} max={10000} step={100}
            value={form.budget}
            onChange={e => setForm(f => ({ ...f, budget: Number(e.target.value) }))}
            className="w-full accent-teal-500"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>$300</span><span>$10,000</span>
          </div>
        </div>

        {/* Travel Vibe */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Travel Vibe</label>
          <div className="flex flex-wrap gap-2">
            {VIBES.map(v => (
              <button
                key={v}
                onClick={() => setForm(f => ({ ...f, travel_style: v }))}
                className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all ${
                  form.travel_style === v
                    ? "bg-teal-500 text-white border-teal-500"
                    : "bg-white text-gray-600 border-gray-200 hover:border-teal-300"
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>

        {/* Preferences */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Interests (optional)</label>
          <div className="flex flex-wrap gap-2">
            {["Museums", "Food", "Beaches", "Temples", "Shopping", "Nightlife", "Nature", "History"].map(p => (
              <button
                key={p}
                onClick={() => togglePref(p.toLowerCase())}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                  form.preferences.includes(p.toLowerCase())
                    ? "bg-amber-400 text-white border-amber-400"
                    : "bg-white text-gray-500 border-gray-200 hover:border-amber-300"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full py-4 rounded-2xl bg-teal-600 text-white font-bold text-lg hover:bg-teal-700 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? "Planning your trip..." : "Plan My Trip 🗺️"}
        </button>
      </div>
    </main>
  );
}
