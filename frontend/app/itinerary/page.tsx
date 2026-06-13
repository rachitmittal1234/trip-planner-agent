"use client";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function ItineraryInner() {
  const router = useRouter();
  const params = useSearchParams();
  const thread_id = params.get("thread_id");
  const destination = params.get("destination") || "";
  const dates = params.get("dates") || "";
  const budget = params.get("budget") || "";

  const [itinerary, setItinerary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!thread_id) return;
    fetch(`http://localhost:8000/status/${thread_id}`)
      .then(r => r.json())
      .then(data => {
        setItinerary(data.itinerary);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load itinerary.");
        setLoading(false);
      });
  }, [thread_id]);

  const handleExportPDF = () => {
    window.open(`http://localhost:8000/export/${thread_id}`, "_blank");
  };

  if (loading) return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-teal-600 text-xl font-semibold animate-pulse">Loading itinerary...</div>
    </main>
  );

  if (error) return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-red-500">{error}</div>
    </main>
  );

  return (
    <main className="min-h-screen px-4 py-12 max-w-3xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="text-5xl mb-2">🗺️</div>
        <h1 className="text-3xl font-bold text-teal-700">{itinerary?.destination || destination}</h1>
        <p className="text-gray-500 mt-1">{dates} · Budget: ${budget}</p>
        <p className="text-gray-600 mt-3 max-w-xl mx-auto text-sm leading-relaxed">{itinerary?.summary}</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-2xl shadow p-4 text-center">
          <div className="text-2xl font-bold text-teal-600">{itinerary?.total_days}</div>
          <div className="text-xs text-gray-500 mt-1">Days</div>
        </div>
        <div className="bg-white rounded-2xl shadow p-4 text-center">
          <div className="text-2xl font-bold text-amber-500">${itinerary?.total_estimated_cost}</div>
          <div className="text-xs text-gray-500 mt-1">Est. Total</div>
        </div>
        <div className="bg-white rounded-2xl shadow p-4 text-center">
          <div className="text-2xl font-bold text-teal-600">{itinerary?.currency || "USD"}</div>
          <div className="text-xs text-gray-500 mt-1">Currency</div>
        </div>
      </div>

      {/* Day cards */}
      <div className="flex flex-col gap-6 mb-8">
        {itinerary?.days?.map((day: any) => (
          <div key={day.day} className="bg-white rounded-2xl shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-teal-700">Day {day.day} — {day.date}</h2>
              <span className="text-sm bg-amber-100 text-amber-700 px-3 py-1 rounded-full font-medium">
                ${day.daily_total} / day
              </span>
            </div>

            <div className="flex flex-col gap-3">
              {["morning", "afternoon", "evening"].map(period => {
                const act = day[period];
                if (!act) return null;
                const icons: any = { morning: "🌅", afternoon: "☀️", evening: "🌙" };
                return (
                  <div key={period} className="flex gap-3 items-start">
                    <span className="text-xl mt-0.5">{icons[period]}</span>
                    <div>
                      <div className="font-semibold text-gray-800 text-sm">{act.name}</div>
                      <div className="text-xs text-gray-500">{act.location} · {act.time} · ${act.estimated_cost}</div>
                      <div className="text-xs text-gray-400 mt-0.5">{act.description}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-4 pt-3 border-t border-gray-100 flex items-center gap-2 text-sm text-gray-500">
              <span>🏨</span>
              <span>{day.hotel} — ${day.hotel_cost}/night</span>
            </div>

            {day.notes && (
              <div className="mt-2 text-xs text-teal-600 bg-teal-50 rounded-xl px-3 py-2">
                💡 {day.notes}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Packing tips */}
      {itinerary?.packing_tips?.length > 0 && (
        <div className="bg-amber-50 rounded-2xl p-6 mb-8">
          <h3 className="font-bold text-amber-700 mb-3">🎒 Packing Tips</h3>
          <ul className="flex flex-col gap-1">
            {itinerary.packing_tips.map((tip: string, i: number) => (
              <li key={i} className="text-sm text-amber-800">• {tip}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-4">
        <button
          onClick={() => router.push(`/approve?thread_id=${thread_id}&destination=${encodeURIComponent(destination)}&dates=${encodeURIComponent(dates)}&budget=${budget}`)}
          className="flex-1 py-4 rounded-2xl bg-teal-600 text-white font-bold text-lg hover:bg-teal-700 transition-all"
        >
          Review & Approve →
        </button>
        <button
          onClick={handleExportPDF}
          className="px-6 py-4 rounded-2xl bg-amber-400 text-white font-bold hover:bg-amber-500 transition-all"
        >
          PDF
        </button>
      </div>
    </main>
  );
}

export default function ItineraryPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-teal-600">Loading...</div>}>
      <ItineraryInner />
    </Suspense>
  );
}
