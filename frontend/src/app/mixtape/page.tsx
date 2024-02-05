"use client";

import { useEffect, useState } from "react";
import { mixtapeService } from "@/service/mixtape";
import Image from "next/image";
import { PlayIcon } from "@heroicons/react/24/outline";
import { Track } from "@/models/Release";
import { StarRating } from "@/components/StarRating";

const MatchingTracksTable = () => {
  const [initializing, setInitializing] = useState(true);
  const [style, setStyle] = useState("");
  const [bpm, setBpm] = useState("");
  const [key, setKey] = useState("");
  const [tracks, setTracks] = useState<Track[]>([]);
  const [matchedBy, setMatchedBy] = useState("");

  // Get filters from URL
  useEffect(() => {
    const url = new URL(window.location.href);
    const style = url.searchParams.get("style");
    const bpm = url.searchParams.get("bpm");
    const key = url.searchParams.get("key");

    if (style) setStyle(style);
    if (bpm) setBpm(bpm);
    if (key) setKey(key);

    setInitializing(false);
  }, []);

  // Fetch tracks on page load
  useEffect(() => {
    if (!initializing) fetchTracks();
  }, [initializing]);

  // Function to fetch tracks based on filters
  const fetchTracks = async () => {
    const result = await mixtapeService.getMatchingTracks(style, bpm, key);

    if (result) {
      setTracks(result.tracks);
      setMatchedBy(result.matched_by);
      return;
    }

    setTracks([]);
    setMatchedBy("");
  };

  // Function to handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // Prevent default form submission
    fetchTracks();

    // Store filters in URL
    const params = new URLSearchParams();
    if (style) params.append("style", style);
    if (bpm) params.append("bpm", bpm);
    if (key) params.append("key", key);
    window.history.replaceState({}, "", `${window.location.pathname}?${params}`);
  };

  return (
    <div className="p-6">
      {/* Filters Form */}
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-4 mb-8">
        <input
          type="text"
          placeholder="Style"
          value={style}
          onChange={(e) => setStyle(e.target.value)}
          className="p-2 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500"
        />
        <input
          type="number"
          placeholder="BPM"
          value={bpm}
          onChange={(e) => setBpm(e.target.value)}
          className="p-2 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500"
        />
        <input
          type="text"
          placeholder="Key"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          className="p-2 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500"
        />
        <button type="submit" className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Search
        </button>
        <button type="button" onClick={() => setTracks([])} className="p-2 bg-red-500 text-white rounded hover:bg-red-600">
          Clear
        </button>
      </form>

      {/* Tracks Table */}
      <div className="overflow-x-auto shadow">
        {matchedBy && (<small className="text-gray-500 block mb-4">Matched by: {matchedBy}</small>)}
        <table className="w-full text-left table-auto border-collapse bg-gray-800">
          <thead className="text-sm text-gray-400 uppercase bg-gray-700">
            <tr>
              <th className="px-4 py-3"></th>
              <th className="px-4 py-3">ID Number</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Rating</th>
              <th className="px-4 py-3">Genre</th>
              <th className="px-4 py-3">Key</th>
              <th className="px-4 py-3">BPM</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {tracks?.map((track) => (
              <tr key={track.id} className="hover:bg-gray-700 transition-colors cursor-pointer" onClick={() => location.href = `/release/${track.release?.id}`}>
                <td className="px-4 py-3">
                  {track.release?.thumb && (
                    <Image
                      src={track.release.thumb}
                      alt={track.release.name}
                      width={50}
                      height={50}
                      className="rounded"
                    />
                  )}
                </td>
                <td className="px-4 py-3">{track.release?.id_number}</td>
                <td className="px-4 py-3">{track.name}</td>
                <td className="px-4 py-3">
                  <StarRating initialRating={track.rating || 0} viewOnly={true} />
                </td>
                <td className="px-4 py-3">{track.genre}</td>
                <td className="px-4 py-3">{track.key}</td>
                <td className="px-4 py-3">{track.bpm}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {tracks?.length === 0 && (
          <div className="text-center text-gray-500 py-4">No matching tracks found</div>
        )}
      </div>
    </div>
  );
};

export default MatchingTracksTable;
