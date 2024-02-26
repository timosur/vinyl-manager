"use client";
import { backupService } from "@/service/backup";
import { releaseService } from "@/service/release";
import React, { useState } from "react";

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files && event.target.files[0]);
  }

  async function handleFileUpload(type: "deejayde" | "collection") {
    if (!file) {
      alert("Please select a file first.");
      return;
    }
    
    switch (type) {
      case "deejayde":
        await releaseService.importDeejayDeCSV(file);
        break;
      case "collection":
        await backupService.import(file);
        break;
    }
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
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={(e) => handleFileUpload("deejayde")}>Upload Deejay.de CSV</button>
      </div>
      <div className="mb-4">
        <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" onClick={handleSyncWithDiscogs}>Sync with Discogs</button>
      </div>
      <div className="mb-4">
        <input className="border border-gray-300 p-2 mr-2" type="file" onChange={handleFileChange} />
        <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={(e) => handleFileUpload("collection")}>Import Collection Backup</button>
      </div>
      <div className="mb-4">
        <button className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" onClick={backupService.export}>Export Collection Backup</button>
      </div>
    </div>
  );
}
