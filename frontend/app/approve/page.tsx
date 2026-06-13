"use client";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function ApproveInner() {
  const router = useRouter();
  const params = useSearchParams();
  const thread_id = params.get("thread_id");
  const destination = params.get("destination") || "";
  const dates = params.get("dates") || "";
  const budget = params.get("budget") || "";

  const [loading, setLoading] = useState<string | null>(null);
  const [booking, setBooking] = useState<any>(null);
  const [error, setError] = useState("");
  const [editNote, setEditNote] = useState("");
  const [showEdit, setShowEdit] = useState(false);

  const handleApprove = async () => {
    setLoading("approve");
    setError("");
    try {
      const res = await fetch(`http://localhost:8000/approve/${thread_id}`, { method: "POST" });
      const data = await res.json();
      setBooking(data.booking_confirmation);
    } catch {
      setError("Approval failed. Try again.");
    } finally {
      setLoading(null);
    }
  };

  const handleEdit = async () => {
    if (!editNote.trim()) return;
    setLoading("edit");
    setError("");
    try {
      // Send edit with a note embedded in summary
      const res = await fetch(`http://localhost:8000/edit/${thread_id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          edit_note: editNote,
        }),
      });
      await res.json();
      router.push(`/planning?thread_id=${thread_id}&destination=${encodeURIComponent(destination)}&dates=${encodeURIComponent(dates)}&budget=${budget}`);
    } catch {
      setError("Edit failed. Try again.");
    } finally {
      setLoading(null);
    }
  };

  const handleReject = async () => {
    setLoading("reject");
    setError("");
    try {
      await fetch(`http://localhost:8000/reject/${thread_id}`, { method: "POST" });
      router.push("/");
    } catch {
      setError("Reject failed. Try again.");
    } finally {
      setLoading(null);
    }
  };

  // Booking confirmed screen
  if (booking) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center mb-8">
          <div className="text-6xl mb-3">🎉</div>
          <h1 className="text-3xl font-bold text-teal-700">Trip Confirmed!</h1>
          <p className="text-gray-500 mt-2">Your bookings are confirmed. Have a great trip!</p>
        </div>

        <div className="w-full max-w-lg bg-white rounded-3xl shadow-xl p-8 flex flex-col gap-6">
          {/* Booking ID */}
          <div className="text-center bg-teal-50 rounded-2xl p-4">
            <div className="text-xs text-gray-500 mb-1">Booking Reference</div>
            <div className="text-2xl font-bold text-teal-700 tracking-widest">{booking.booking_id}</div>
          </div>

          {/* Flight */}
          {booking.flights?.map((f: any) => (
            <div key={f.confirmation_code} className="border border-gray-100 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">✈️</span>
                <span className="font-bold text-gray-800">Flight Confirmed</span>
                <span className="ml-auto text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">{f.status}</span>
              </div>
              <div className="text-sm text-gray-600 flex flex-col gap-1">
                <div><span className="font-medium">Airline:</span> {f.airline} {f.flight_number}</div>
                <div><span className="font-medium">Route:</span> {f.departure} → {f.arrival}</div>
                <div><span className="font-medium">Price:</span> ${f.price_usd}</div>
                <div><span className="font-medium">Confirmation:</span> <span className="font-mono text-teal-600">{f.confirmation_code}</span></div>
              </div>
            </div>
          ))}

          {/* Hotel */}
          {booking.hotels?.map((h: any) => (
            <div key={h.confirmation_code} className="border border-gray-100 rounded-2xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xl">🏨</span>
                <span className="font-bold text-gray-800">Hotel Confirmed</span>
                <span className="ml-auto text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">{h.status}</span>
              </div>
              <div className="text-sm text-gray-600 flex flex-col gap-1">
                <div><span className="font-medium">Hotel:</span> {h.hotel_name}</div>
                <div><span className="font-medium">Location:</span> {h.location}</div>
                <div><span className="font-medium">Check-in:</span> {h.check_in} · <span className="font-medium">Check-out:</span> {h.check_out}</div>
                <div><span className="font-medium">Nights:</span> {h.nights} · ${h.price_per_night_usd}/night</div>
                <div><span className="font-medium">Total:</span> ${h.total_usd}</div>
                <div><span className="font-medium">Confirmation:</span> <span className="font-mono text-teal-600">{h.confirmation_code}</span></div>
              </div>
            </div>
          ))}

          {/* Cost breakdown */}
          {booking.cost_breakdown && (
            <div className="bg-amber-50 rounded-2xl p-4">
              <h3 className="font-bold text-amber-700 mb-2">💰 Cost Breakdown</h3>
              <div className="flex flex-col gap-1 text-sm text-amber-800">
                <div className="flex justify-between"><span>Flights</span><span>${booking.cost_breakdown.flights_usd}</span></div>
                <div className="flex justify-between"><span>Hotels</span><span>${booking.cost_breakdown.hotels_usd}</span></div>
                <div className="flex justify-between"><span>Activities</span><span>${booking.cost_breakdown.activities_usd}</span></div>
                <div className="flex justify-between font-bold border-t border-amber-200 pt-1 mt-1"><span>Total</span><span>${booking.cost_breakdown.total_usd}</span></div>
              </div>
            </div>
          )}

          <p className="text-xs text-gray-400 text-center">{booking.note}</p>

          <button
            onClick={() => router.push("/")}
            className="w-full py-3 rounded-2xl bg-teal-600 text-white font-bold hover:bg-teal-700 transition-all"
          >
            Plan Another Trip ✈️
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
      <div className="text-center mb-8">
        <div className="text-5xl mb-3">👀</div>
        <h1 className="text-3xl font-bold text-teal-700">Review Your Trip</h1>
        <p className="text-gray-500 mt-2">
          {destination && <span className="font-semibold text-gray-700">{destination}</span>}
          {dates && <span className="text-gray-400"> · {dates}</span>}
          {budget && <span className="text-gray-400"> · ${budget}</span>}
        </p>
      </div>

      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl p-8 flex flex-col gap-4">
        <p className="text-gray-600 text-sm text-center">
          Happy with the itinerary? Approve to confirm bookings, request edits, or start over.
        </p>

        {error && <p className="text-red-500 text-sm text-center">{error}</p>}

        {/* Approve */}
        <button
          onClick={handleApprove}
          disabled={!!loading}
          className="w-full py-4 rounded-2xl bg-teal-600 text-white font-bold text-lg hover:bg-teal-700 transition-all disabled:opacity-60"
        >
          {loading === "approve" ? "Confirming bookings..." : "✅ Approve & Book"}
        </button>

        {/* Edit */}
        <button
          onClick={() => setShowEdit(!showEdit)}
          disabled={!!loading}
          className="w-full py-4 rounded-2xl bg-amber-400 text-white font-bold text-lg hover:bg-amber-500 transition-all disabled:opacity-60"
        >
          ✏️ Request Changes
        </button>

        {showEdit && (
          <div className="flex flex-col gap-2">
            <textarea
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-amber-300 resize-none"
              rows={3}
              placeholder="Describe what you'd like to change... e.g. 'More beach time on day 2, remove museums'"
              value={editNote}
              onChange={e => setEditNote(e.target.value)}
            />
            <button
              onClick={handleEdit}
              disabled={!!loading || !editNote.trim()}
              className="w-full py-3 rounded-2xl bg-amber-500 text-white font-bold hover:bg-amber-600 transition-all disabled:opacity-60"
            >
              {loading === "edit" ? "Submitting changes..." : "Submit Changes"}
            </button>
          </div>
        )}

        {/* Reject */}
        <button
          onClick={handleReject}
          disabled={!!loading}
          className="w-full py-3 rounded-2xl border border-red-200 text-red-500 font-medium hover:bg-red-50 transition-all disabled:opacity-60"
        >
          {loading === "reject" ? "Restarting..." : "❌ Start Over"}
        </button>

        <button
          onClick={() => router.back()}
          className="text-sm text-gray-400 hover:text-gray-600 text-center mt-1"
        >
          ← Back to itinerary
        </button>
      </div>
    </main>
  );
}

export default function ApprovePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-teal-600">Loading...</div>}>
      <ApproveInner />
    </Suspense>
  );
}
