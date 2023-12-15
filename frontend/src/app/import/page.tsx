"use client";
import { releaseService } from "@/service/release";
import React, { useState } from "react";

export default function Page() {
  const [file, setFile] = useState(null);

  // Handle CSV file change
  function handleFileChange(event) {
    setFile(event.target.files[0]);
  }

  // Handle CSV file upload
  async function handleFileUpload() {
    if (!file) {
      alert("Please select a file first.");
      return;
    }
    
    await releaseService.importDeejayDeCSV(file);
  }

  // Handle syncing with Discogs
  async function handleSyncWithDiscogs() {
    await releaseService.discogsSync();
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-xl font-bold mb-4">Vinyl Collection</h1>
      <div className="mb-4">
        <input className="border border-gray-300 p-2 mr-2" type="file" onChange={handleFileChange} />
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={handleFileUpload}>Upload CSV</button>
      </div>
      <div>
        <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" onClick={handleSyncWithDiscogs}>Sync with Discogs</button>
      </div>
    </div>
  );
}
