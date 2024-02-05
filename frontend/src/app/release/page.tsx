"use client";
import { releaseService } from "@/service/release"
import { Release } from "@/models/Release"
import { useEffect, useState } from "react";
import { StarRating } from "@/components/StarRating";
import { useRouter } from "next/navigation"
import { PrintReleaseDetails } from "@/components/release/PrintReleaseDetails";
import Image from "next/image";
import { TrashIcon } from "@heroicons/react/24/outline";

interface SearchableTableProps {
  releases: Release[];
}

const SortIcon = ({ isSorted, direction }: { isSorted: boolean; direction: "asc" | "desc" }) => {
  if (!isSorted) return null;
  return direction === "asc" ? "↑" : "↓";
};

const SearchableTable: React.FC<SearchableTableProps> = ({ releases }) => {
  const router = useRouter()
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredReleases, setFilteredReleases] = useState<Release[]>(releases);
  const [releaseName, setReleaseName] = useState("");

  const [sortColumn, setSortColumn] = useState<string | null>("id_number");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const sortData = (data: Release[], column: string | null, direction: "asc" | "desc") => {
    if (!column) return data;
    // split column name by dot
    const columnParts = column.split(".");

    return [...data].sort((a, b) => {
      // get value of column
      let aVal: any = a;
      let bVal: any = b;

      for (const part of columnParts) {
        aVal = aVal[part];
        if (aVal === undefined) return 1;
        bVal = bVal[part];
        if (bVal === undefined) return -1;
      }

      // lower strings
      if (typeof aVal === "string") aVal = (aVal as string).toLowerCase();
      if (typeof bVal === "string") bVal = (bVal as string).toLowerCase();

      // sort by value, if value empty, sort to bottom
      if (aVal === null) return 1;
      if (bVal === null) return -1;
      if (aVal < bVal) return direction === "asc" ? -1 : 1;
      if (aVal > bVal) return direction === "asc" ? 1 : -1;

      return 0;
    });
  };

  const handleSort = (column: string) => {
    const isAsc = sortColumn === column && sortDirection === "asc";
    setSortDirection(isAsc ? "desc" : "asc");
    setSortColumn(column);
  };

  const createRelease = async () => {
    const release = await releaseService.create(releaseName);

    location.href = `/release/${release.id}`;
  }

  const deleteRelease = async (e: any, id: string) => {
    e.preventDefault();

    await releaseService.delete(id);
    const releases = await releaseService.get();
    setFilteredReleases(releases);
  };

  useEffect(() => {
    let filtered = releases?.filter(release =>
      release.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      release.tracks.some(track => track.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.labels.some(label => label.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.artists.some(artist => artist.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.genre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      release.styles?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered = sortData(filtered || [], sortColumn, sortDirection);
    setFilteredReleases(filtered);
  }, [searchTerm, releases, sortColumn, sortDirection]);

  return (
    <div className="p-6">
      {/* Button on the right */}
      <div className="flex justify-end mb-4">
        {/* New release by name */}
        <input type="text" placeholder="Release Name" value={releaseName} className="p-2 mr-2 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500 transition-colors" onChange={(e) => setReleaseName(e.target.value)} />
        <button className="p-2 bg-blue-500 rounded hover:bg-blue-600" onClick={createRelease}>
          New Release
        </button>
        <button onClick={() => window.print()} className="p-2 ml-2 bg-green-500 rounded hover:bg-green-600">
          Print Details
        </button>
      </div>
      <input
        type="text"
        placeholder="Search..."
        className="w-full p-3 mb-4 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500 transition-colors"
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div className="overflow-x-auto shadow">
        <table className="w-full text-left table-auto border-collapse bg-gray-800">
          <thead className="text-sm text-gray-400 uppercase bg-gray-700">
            <tr>
              <th className="px-3 py-1 cursor-pointer" onClick={() => handleSort("id_number")}>
                ID Number <SortIcon isSorted={sortColumn === "id_number"} direction={sortDirection} />
              </th>
              <th className="px-4 py-3"></th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("name")}>
                Name <SortIcon isSorted={sortColumn === "name"} direction={sortDirection} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("artists.0.name")}>
                Artists <SortIcon isSorted={sortColumn === "artists.0.name"} direction={sortDirection} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("tracks.0.name")}>
                Tracks <SortIcon isSorted={sortColumn === "tracks.0.name"} direction={sortDirection} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("labels.0.name")}>
                Labels <SortIcon isSorted={sortColumn === "labels.0.name"} direction={sortDirection} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("labels.0.styles")}>
                Styles <SortIcon isSorted={sortColumn === "labels.0.styles"} direction={sortDirection} />
              </th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {filteredReleases.map(release => (
              <tr key={release.id} className="hover:bg-gray-700 transition-colors">
                <td className="px-3 py-1 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  <span>{release.id_number}</span>
                </td>
                <td className="px-3 py-1 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  <div style={{ width: "80px", height: "80px" }} className="relative">
                    {release.thumb && (<Image src={release.thumb} width={0} height={0} alt={release.name} layout="fill" />)}
                  </div>
                </td>
                <td className="px-4 py-3 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  <span>{release.name}</span>
                </td>
                <td className="px-4 py-3 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  {release.artists.map(artist => (
                    <div key={artist.id}>{artist.name}</div>
                  ))}
                </td>
                <td className="px-4 py-3 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  <div className="flex flex-wrap -mx-2">
                    {release.tracks.map(track => (
                      <div key={track.id} className="w-1/2 px-2 mb-4">
                        <div key={track.id} className="bg-gray-600 shadow-md rounded-lg p-4">
                          <div className="font-semibold text-lg text-white">{track.name}</div>
                          <div className="text-sm text-white">{track.side} • {track.genre}</div>
                          <div className="text-sm text-white">Key: {track.key} • BPM: {track.bpm}</div>
                          <div className="flex items-center mt-2">
                            <StarRating viewOnly={true} initialRating={track.rating || 0} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  {release.labels.map(label => (
                    <div key={label.id}>{label.name}</div>
                  ))}
                </td>
                <td className="px-4 py-3 cursor-pointer" onClick={() => router.push(`/release/${release.id}`)}>
                  <span>{release.styles}</span>
                </td>
                {/* Edit button, onclick go to edit page */}
                <td className="px-4 py-3">
                  <a onClick={(e) => deleteRelease(e, release.id)} className="text-red-500 hover:text-red-700 cursor-pointer">
                    <TrashIcon className="h-5 w-5" />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {/* Count of releases */}
        <div className="text-sm text-gray-400 uppercase bg-gray-700 p-2">
          {filteredReleases.length} Releases
        </div>
      </div>
      <div className="printable flex">
        {filteredReleases.map((release, index) => (
          <PrintReleaseDetails key={index} release={release} />
        ))}
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
