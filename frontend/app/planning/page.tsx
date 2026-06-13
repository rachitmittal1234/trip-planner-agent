"use client";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

const NODES = [
  { key: "preference_extractor", label: "Extracting preferences" },
  { key: "destination_researcher", label: "Researching destination" },
  { key: "weather_fetcher", label: "Fetching weather forecast" },
  { key: "flights_hotels_searcher", label: "Searching flights & hotels" },
  { key: "itinerary_generator", label: "Generating itinerary" },
  { key: "quality_checker", label: "Checking quality" },
  { key: "human_approval", label: "Ready for your review" },
];

function PlanningInner() {
  const router = useRouter();
  const params = useSearchParams();
  const thread_id = params.get("thread_id");
  const destination = params.get("destination") || "";
  const dates = params.get("dates") || "";
  const budget = params.get("budget") || "";

  const [completed, setCompleted] = useState<string[]>([]);
  const [current, setCurrent] = useState<string>("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!thread_id) return;

    // Poll status every 2s since SSE streams after graph already ran
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/status/${thread_id}`);
        const data = await res.json();
        if (data.next && data.next.includes("human_approval")) {
          // Graph paused at approval — all nodes done
          setCompleted(NODES.map(n => n.key));
          setCurrent("human_approval");
          setDone(true);
          clearInterval(interval);
          setTimeout(() => {
            router.push(`/itinerary?thread_id=${thread_id}&destination=${encodeURIComponent(destination)}&dates=${encodeURIComponent(dates)}&budget=${budget}`);
          }, 1500);
        }
      } catch {
        setError("Lost connection to backend.");
        clearInterval(interval);
      }
    }, 2000);

    // Animate nodes progressively while waiting
    let i = 0;
    const animInterval = setInterval(() => {
      if (i < NODES.length - 1) {
        setCurrent(NODES[i].key);
        setCompleted(prev => [...prev, NODES[i].key]);
        i++;
      } else {
        clearInterval(animInterval);
      }
    }, 3000);

    return () => {
      clearInterval(interval);
      clearInterval(animInterval);
    };
  }, [thread_id, router, destination, dates, budget]);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      <div className="text-center mb-10">
        <div className="text-5xl mb-3">🧠</div>
        <h1 className="text-3xl font-bold text-teal-700">Planning your trip</h1>
        <p className="text-gray-500 mt-2">
          {destination && <span className="font-semibold text-gray-700">{destination}</span>}
          {dates && <span className="text-gray-400"> · {dates}</span>}
          {budget && <span className="text-gray-400"> · ${budget}</span>}
        </p>
      </div>

      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl p-8 flex flex-col gap-4">
        {NODES.map((node) => {
          const isCompleted = completed.includes(node.key);
          const isCurrent = current === node.key && !isCompleted;
          return (
            <div key={node.key} className="flex items-center gap-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                isCompleted
                  ? "bg-teal-500 text-white"
                  : isCurrent
                  ? "bg-amber-400 text-white animate-pulse"
                  : "bg-gray-100 text-gray-400"
              }`}>
                {isCompleted ? "✓" : isCurrent ? "⟳" : "○"}
              </div>
              <span className={`text-sm font-medium transition-all ${
                isCompleted ? "text-teal-700" : isCurrent ? "text-amber-600" : "text-gray-400"
              }`}>
                {node.label}
              </span>
              {isCompleted && node.key === "quality_checker" && (
                <span className="ml-auto text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">✓ passed</span>
              )}
            </div>
          );
        })}

        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

        {done && (
          <div className="mt-4 text-center">
            <p className="text-teal-600 font-semibold">✅ Itinerary ready! Redirecting...</p>
          </div>
        )}
      </div>
    </main>
  );
}

export default function PlanningPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-teal-600">Loading...</div>}>
      <PlanningInner />
    </Suspense>
  );
}
