import { Release } from '@/models/Release';
import { ClipboardIcon } from '@heroicons/react/24/outline';
import React, { useState, useEffect } from 'react';

export const CopyReleaseDetails = ({ release }: { release: Release }) => {
  const [formattedContent, setFormattedContent] = useState('');

  // Function to format the content based on the Release and its Tracks
  const formatContent = (release: Release) => {
    const { id_number, name, labels, tracks, artists } = release;
    let formatted = `${id_number} - ${labels.map(label => label.name).join(', ')} - ${name}\n`;

    tracks.forEach(track => {
      formatted += `${track.side} - ${track.rating ?? 'x'}✵ - ${track.key} - ${track.bpm} - ${track.genre} - ${artists.map(artist => artist.name).join(', ')} - ${track.name}\n`;
    });

    return formatted;
  };

  // Function to copy content to clipboard using Clipboard API
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(formattedContent);
      console.log('Content copied to clipboard');
    } catch (err) {
      console.error('Failed to copy: ', err);
    }
  };

  // Effect to format content whenever release data changes
  useEffect(() => {
    if (release) {
      setFormattedContent(formatContent(release));
    }
  }, [release]);

  return (
    <div>
      <button onClick={copyToClipboard} className="text-green-500 hover:text-green-700 cursor-pointer">
        <ClipboardIcon className="h-5 w-5" />
      </button>
    </div>
  );
};
