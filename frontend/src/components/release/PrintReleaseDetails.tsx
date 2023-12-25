import { formatSecondsToMinutes } from "@/helper/time";
import { Release } from "@/models/Release";

export const PrintReleaseDetails = ({ release }: { release: Release }) => {
  if (!release) return <div>Loading...</div>;

  return (
    <div className="font-sans text-xs max-w-xs mx-auto">
      <h2 className="text-lg font-bold mb-2">{release.name}</h2>
      <div><strong>Short:</strong> {release.short}</div>
      {release.notes && <div><strong>Description:</strong> {release.notes}</div>}
      <h3 className="text-md font-semibold mt-4 mb-2">Artists:</h3>
      <div className="flex flex-wrap -mx-1">
        {release.artists?.map((artist, index) => (
          <div key={index} className="p-2 border border-gray-300 rounded-lg m-1 w-36">
            <div>{artist.name}</div>
          </div>
        ))}
      </div>
      <h3 className="text-md font-semibold mt-4 mb-2">Labels:</h3>
      <div className="flex flex-wrap -mx-1">
        {release.labels?.map((label, index) => (
          <div key={index} className="p-2 border border-gray-300 rounded-lg m-1 w-36">
            <div>{label.name}</div>
          </div>
        ))}
      </div>
      <h3 className="text-md font-semibold mt-4 mb-2">Tracks:</h3>
      <div className="flex flex-wrap -mx-1">
        {release.tracks?.map((track, index) => (
          <div key={index} className="p-2 border border-gray-300 rounded-lg m-1 w-36">
            <div>{track.name}</div>
            <div><strong>Genre:</strong> {track.genre}</div>
            <div><strong>Key:</strong> {track.key}</div>
            <div><strong>Length:</strong> {formatSecondsToMinutes(track.length)}</div>
            <div><strong>BPM:</strong> {track.bpm}</div>
            <div><strong>Rating:</strong> {track.rating}</div>
          </div>
        ))}
      </div>
    </div>
  );
};