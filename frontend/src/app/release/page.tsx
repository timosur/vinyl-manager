"use client";
import { releaseService } from "@/service/release"
import { Release } from "@/models/Release"
import { useEffect, useState } from "react";
import { TrashIcon } from "@heroicons/react/24/outline";

interface SearchableTableProps {
  releases: Release[];
}

const StarRating: React.FC<{ trackId: string; onRating: (trackId: string, rating: number) => void }> = ({ trackId, onRating }) => {
  const [rating, setRating] = useState(0);

  const handleRating = (rate: number) => {
    setRating(rate);
    onRating(trackId, rate);
  };

  return (
    <div className="flex items-center">
      {[...Array(5)].map((_, i) => (
        <svg
          key={i}
          onClick={() => handleRating(i + 1)}
          className={`h-6 w-6 cursor-pointer ${i < rating ? 'text-yellow-400' : 'text-gray-400'}`}
          fill="currentColor"
          viewBox="0 0 24 24">
          <path d="M12 .587l3.668 7.431L24 8.9l-6 5.833 1.417 8.267L12 19.764l-7.417 3.236L6 14.733 0 8.9l8.332-.982L12 .587z" />
        </svg>
      ))}
    </div>
  );
};

const SearchableTable: React.FC<SearchableTableProps> = ({ releases }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredReleases, setFilteredReleases] = useState<Release[]>(releases);

  const handleRating = (trackId: string, rating: number) => {
    // Update the rating for the track. This can be adapted to update the state or backend.
    console.log(`Track ID: ${trackId}, Rating: ${rating}`);
  };

  useEffect(() => {
    const filtered = releases.filter(release => 
      release.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      release.tracks.some(track => track.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.labels.some(label => label.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.artists.some(artist => artist.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setFilteredReleases(filtered);
  }, [searchTerm, releases]);

  const removeTrack = (releaseId: string, trackId: string) => {
    setFilteredReleases(filteredReleases.map(release => {
      if (release.id === releaseId) {
        return {
          ...release,
          tracks: release.tracks.filter(track => track.id !== trackId)
        };
      }
      return release;
    }));

    console.log(`Release ID: ${releaseId}, Track ID: ${trackId}`);
  };

  return (
    <div className="p-6">
      <input
        type="text"
        placeholder="Search by release name or ID"
        className="w-full p-3 mb-4 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500 transition-colors"
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div className="overflow-x-auto shadow">
        <table className="w-full text-left table-auto border-collapse bg-gray-800">
          <thead className="text-sm text-gray-400 uppercase bg-gray-700">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Artists</th>
              <th className="px-4 py-3">Tracks</th>
              <th className="px-4 py-3">Labels</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {filteredReleases.map(release => (
              <tr key={release.id} className="hover:bg-gray-700 transition-colors">
                <td className="px-4 py-3">{release.name}</td>
                <td className="px-4 py-3">
                  {release.artists.map(artist => (
                    <div key={artist.id}>{artist.name}</div>
                  ))}
                </td>
                <td className="px-4 py-3">
                  {release.tracks.map(track => (
                    <div key={track.id} className="flex justify-between items-center">
                      <span>{track.name}</span>
                      <div className="flex items-center">
                        <StarRating trackId={track.id} onRating={handleRating} />
                        <button
                          className="ml-3 text-red-500 hover:text-red-700"
                          onClick={() => removeTrack(release.id, track.id)}
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </td>
                <td className="px-4 py-3">
                  {release.labels.map(label => (
                    <div key={label.id}>{label.name}</div>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default function Release() {
  const [releases, setReleases] = useState<Release[]>([]);

  useEffect(() => {
    async function fetchReleases() {
      const releases = await releaseService.get();
      setReleases(releases);
    }
    fetchReleases();
  }, []);

  return (
    <SearchableTable releases={releases} />
  )
}
