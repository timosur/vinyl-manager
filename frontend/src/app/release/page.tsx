"use client";
import { releaseService } from "@/service/release"
import { Release } from "@/models/Release"
import { useEffect, useState, useCallback } from "react";
import { StarRating } from "@/components/StarRating";
import { useRouter } from "next/navigation"
import { PrintReleaseDetails } from "@/components/release/PrintReleaseDetails";
import Image from "next/image";
import { TrashIcon } from "@heroicons/react/24/outline";
import { CopyReleaseDetails } from "@/components/release/CopyReleaseDeatils";
import { debounce } from "@/helper/debounce";

const SortIcon = ({ isSorted, direction }: { isSorted: boolean; direction: "asc" | "desc" }) => {
  if (!isSorted) return null;
  return direction === "asc" ? "↑" : "↓";
};

export default function ReleasesPage() {
  const router = useRouter()
  const [releaseOverview, setReleaseOverview] = useState<{ items: Release[], start: number, end: number, total: number }>({ items: [], start: 0, end: 0, total: 0 });
  const [page, setPage] = useState(1);
  const [pageLimit, setPageLimit] = useState(50);
  const [searchTerm, setSearchTerm] = useState("");
  const [releaseName, setReleaseName] = useState("");

  const [sortColumn, setSortColumn] = useState<string>("id_number");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const fetchReleaseOverview = useCallback(async () => {
    const releaseOverview = await releaseService.get(pageLimit, page, sortColumn, sortOrder, searchTerm);
    setReleaseOverview(releaseOverview);
  }, [page, pageLimit, sortColumn, sortOrder, searchTerm]);

  const handleSort = (column: string) => {
    const isAsc = sortColumn === column && sortOrder === "asc";
    setSortOrder(isAsc ? "desc" : "asc");
    setSortColumn(column);
  };

  const handleNewSearchTermDelayed = debounce((searchTerm: string) => {
    setSearchTerm(searchTerm);
  }, 500);

  const createRelease = async () => {
    const release = await releaseService.create(releaseName);
    location.href = `/release/${release.id}`;
  }

  const deleteRelease = async (e: any, id: string) => {
    e.preventDefault();

    await releaseService.delete(id);
    await fetchReleaseOverview();
  };

  const exportCSV = async () => {
    try {
      const blob = await releaseService.exportCSV();
      if (blob) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'releases_export.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to export CSV');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export CSV');
    }
  }

  const importCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert('Please select a CSV file');
      return;
    }

    try {
      const result = await releaseService.importCSV(file);
      if (result.status === 'SUCCESS') {
        alert(`Import completed!\nCreated: ${result.created_count}\nUpdated: ${result.updated_count}\nErrors: ${result.error_count}`);
        await fetchReleaseOverview(); // Refresh the list
      } else {
        alert('Import failed');
      }
    } catch (error) {
      console.error('Import error:', error);
      alert('Import failed: ' + (error as Error).message);
    }

    // Reset the input
    event.target.value = '';
  }

  useEffect(() => {
    fetchReleaseOverview();
  }, [searchTerm, sortColumn, sortOrder, page, pageLimit]);

  useEffect(() => {
    // Listen to keydown events for keyboard shortcuts, for pagination to next and prev page
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") {
        if (releaseOverview.end !== releaseOverview.total) {
          setPage(page + 1);
        }
      } else if (e.key === "ArrowLeft") {
        if (page !== 1) {
          setPage(page - 1);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [page, releaseOverview]);

  const PaginationBar = () => (
    <div className="text-sm text-gray-400 uppercase bg-gray-700 p-2 flex justify-end">
      <div>
        {/* Pagination */}
        {releaseOverview.start} - {releaseOverview.end} of {releaseOverview.total} releases
        {/* Buttons for getting to next and prev page */}
        <button onClick={() => setPage(page - 1)} disabled={page === 1} className={"p-2 mx-2 " + (page === 1 ? "bg-gray-700" : "bg-gray-800 hover:bg-gray-700")}>&lt;</button>
        <button onClick={() => setPage(page + 1)} disabled={releaseOverview.end === releaseOverview.total} className={"p-2 " + (releaseOverview.end === releaseOverview.total ? "bg-gray-700" : "bg-gray-800 hover:bg-gray-700")}>&gt;</button>
        {/* Input for selecting pageLimit from options 10, 20, 30, 50, 100 */}
        <select value={pageLimit} onChange={(e) => { setPage(1); setPageLimit(parseInt(e.target.value)) }} className="p-2 mx-2 bg-gray-800">
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="30">30</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      {/* Button on the right */}
      <div className="flex justify-end mb-4 flex-wrap gap-2">
        {/* New release by name */}
        <input type="text" placeholder="Release Name" value={releaseName} className="p-2 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500 transition-colors" onChange={(e) => setReleaseName(e.target.value)} />
        <button className="p-2 bg-blue-500 rounded hover:bg-blue-600" onClick={createRelease}>
          New Release
        </button>
        <button onClick={() => window.print()} className="p-2 bg-green-500 rounded hover:bg-green-600">
          Print Details
        </button>
        {/* CSV Export button */}
        <button onClick={exportCSV} className="p-2 bg-purple-500 rounded hover:bg-purple-600">
          Export CSV
        </button>
        {/* CSV Import button (hidden file input) */}
        <label className="p-2 bg-orange-500 rounded hover:bg-orange-600 cursor-pointer">
          Import CSV
          <input
            type="file"
            accept=".csv"
            onChange={importCSV}
            className="hidden"
          />
        </label>
      </div>
      <input
        type="text"
        placeholder="Search..."
        className="w-full p-3 mb-4 bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-blue-500 transition-colors"
        onChange={(e) => handleNewSearchTermDelayed(e.target.value)}
      />

      <div className="overflow-x-auto shadow">
        <PaginationBar />
        <table className="w-full text-left table-auto border-collapse bg-gray-800">
          <thead className="text-sm text-gray-400 uppercase bg-gray-700">
            <tr>
              <th className="px-3 py-1 cursor-pointer" onClick={() => handleSort("id_number")}>
                ID Number <SortIcon isSorted={sortColumn === "id_number"} direction={sortOrder} />
              </th>
              <th className="px-4 py-3"></th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("name")}>
                Name <SortIcon isSorted={sortColumn === "name"} direction={sortOrder} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("artists")}>
                Artists <SortIcon isSorted={sortColumn === "artists"} direction={sortOrder} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("tracks")}>
                Tracks <SortIcon isSorted={sortColumn === "tracks"} direction={sortOrder} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("labels")}>
                Labels <SortIcon isSorted={sortColumn === "labels"} direction={sortOrder} />
              </th>
              <th className="px-4 py-3 cursor-pointer" onClick={() => handleSort("styles")}>
                Styles <SortIcon isSorted={sortColumn === "styles"} direction={sortOrder} />
              </th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-600">
            {releaseOverview?.items?.map(release => (
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
                  <CopyReleaseDetails release={release} />

                  <a onClick={(e) => deleteRelease(e, release.id)} className="text-red-500 hover:text-red-700 cursor-pointer">
                    <TrashIcon className="h-5 w-5" />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <PaginationBar />
      </div>
      <div className="printable flex">
        {releaseOverview?.items?.map((release, index) => (
          <PrintReleaseDetails key={index} release={release} />
        ))}
      </div>
    </div>
  );
};
