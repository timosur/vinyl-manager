"use client";
import { releaseService } from "@/service/release"
import { Release } from "@/models/Release"
import { useEffect, useState } from "react";
import { StarRating } from "@/components/StarRating";
import { useRouter } from "next/navigation"
import { PrintReleaseDetails } from "@/components/release/PrintReleaseDetails";
import Image from "next/image";

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

  const [sortColumn, setSortColumn] = useState<string | null>("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const sortData = (data: Release[], column: string | null, direction: "asc" | "desc") => {
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
        if (bVal === undefined) return 1;
      }

      // lower strings
      if (typeof aVal === "string") aVal = (aVal as string).toLowerCase();
      if (typeof bVal === "string") bVal = (bVal as string).toLowerCase();

      // sort by value
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

  useEffect(() => {
    let filtered = releases?.filter(release =>
      release.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      release.tracks.some(track => track.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.labels.some(label => label.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      release.artists.some(artist => artist.name.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    filtered = sortData(filtered || [], sortColumn, sortDirection);
    setFilteredReleases(filtered);
  }, [searchTerm, releases, sortColumn, sortDirection]);

  return (
    <div className="p-6">
      {/* Button on the right */}
      <div className="flex justify-end mb-4">
        {/* New release by name */}
        <input type="text" placeholder="Release Name" className="p-2 mr-2 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500 transition-colors" />
        <button className="p-2 bg-blue-500 rounded hover:bg-blue-600">
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
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {filteredReleases.map(release => (
              <tr key={release.id} className="hover:bg-gray-700 cursor-pointer transition-colors" onClick={() => router.push(`/release/${release.id}`)}>
                <td className="px-4 py-3">
                  <Image src={release.thumb} width={64} height={64} alt={release.name} />
                </td>
                <td className="px-4 py-3">{release.name}</td>
                <td className="px-4 py-3">
                  {release.artists.map(artist => (
                    <div key={artist.id}>{artist.name}</div>
                  ))}
                </td>
                <td className="px-4 py-3">
                  {release.tracks.map(track => (
                    <div key={track.id} className="flex justify-between items-center">
                      <span>{track.name} ({track.side})</span>
                      <div className="flex items-center">
                        <StarRating initialRating={track.rating || 0} />
                      </div>
                    </div>
                  ))}
                </td>
                <td className="px-4 py-3">
                  {release.labels.map(label => (
                    <div key={label.id}>{label.name}</div>
                  ))}
                </td>
                {/* Edit button, onclick go to edit page */}
                <td className="px-4 py-3">
                  <a href={`/release/${release.id}`} className="text-blue-500 hover:text-blue-700">Edit</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
