"use client";
import { useEffect, useState } from 'react';
import { releaseService } from '@/service/release';
import { Release, Track } from '@/models/Release';
import { StarRating } from '@/components/StarRating';
import { formatMinutesToSeconds, formatSecondsToMinutes } from '@/helper/time';
import TrashIcon from '@heroicons/react/24/outline/TrashIcon';
import { CamelotWheel } from '@/components/CamelotWheel';
import AudioPlayer from '@/components/AudioPlayer';
// ignore TS error for now
// @ts-ignore
import { AudioVisualizer } from 'react-audio-visualize';
import { AudioRecorder } from '@/components/AudioRecorder';

const PrintReleaseDetails = ({ release }: { release: Release }) => {
  if (!release) return <div>Loading...</div>;

  return (
    <div className="font-sans text-xs max-w-xs mx-auto">
      <h2 className="text-lg font-bold mb-2">{release.name}</h2>
      <div><strong>Short:</strong> {release.short}</div>
      <div><strong>Notes:</strong> {release.notes}</div>
      <h3 className="text-md font-semibold mt-4 mb-2">Tracks:</h3>
      <div className="flex flex-wrap -mx-1">
        {release.tracks?.map((track, index) => (
          <div key={index} className="p-2 border border-gray-300 rounded-lg m-1 w-36">
            <div><strong>Name:</strong> {track.name}</div>
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

const EditRelease = ({ params }: { params: { id: string } }) => {
  const [release, setRelease] = useState<Release>({} as Release);
  const [analysis, setAnalysis] = useState<boolean>(true);
  const [newTrackName, setNewTrackName] = useState('');

  useEffect(() => {
    const fetchRelease = async () => {
      if (!params.id) return;
      const fetchedRelease = await releaseService.getById(params.id as string);
      setRelease(fetchedRelease);
    };
    fetchRelease();
  }, [params.id]);

  const handleAddTrack = () => {
    const newTrack: Track = {
      id: Math.random().toString(36),
      name: newTrackName,
      genre: '',
      side: '',
      key: '',
      length: 0,
      bpm: 0,
      rating: 0,
      audio: '',
      release_id: release.id,
    };

    setRelease({
      ...release,
      tracks: [...release.tracks, newTrack],
    });

    setNewTrackName('');
  }

  const handleRemoveTrack = (trackId: string) => {
    setRelease({
      ...release,
      tracks: release.tracks.filter((track) => track.id !== trackId),
    });
  };

  const handleSave = async () => {
    const updatedRelease = await releaseService.update(params.id as string, release, analysis);

    setRelease(updatedRelease);
  };

  const handleChange = (value: any, field: keyof Release) => {
    setRelease({
      ...release,
      [field]: value,
    });
  };

  const handleTrackChange = (trackId: string, value: any, field: keyof Track) => {
    setRelease({
      ...release,
      tracks: release.tracks.map((track) =>
        track.id === trackId ? { ...track, [field]: value } : track
      ),
    });
  }

  if (!release) return <div>Loading...</div>;

  return (
    <div className="text-white bg-[#0e181a] p-6 rounded-lg shadow-md">
      <h1 className="text-2xl mb-2">Edit Release</h1>
      <input
        type="text"
        value={release.name}
        onChange={(e) => handleChange(e.target.value, 'name')}
        className="w-full p-2 mb-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Name"
      />
      {/* Short Release name */}
      <input
        type="text"
        value={release.short}
        onChange={(e) => handleChange(e.target.value, 'short')}
        className="w-full p-2 mb-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Short Release Name"
      />
      {/* Release notes */}
      <textarea
        value={release.notes}
        onChange={(e) => handleChange(e.target.value, 'notes')}
        className="w-full p-2 mb-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Notes"
      />
      <div>
        <h2 className="text-xl mb-2">Tracks</h2>
        <div className="flex flex-wrap -mx-2">
          {release.tracks?.map((track, index) => (
            <div key={index} className="w-full md:w-1/2 px-2 mb-4">
              <div className="card bg-gray-800 border border-gray-600 rounded p-4">
                {/* Track Name */}
                <label className="block mb-2">
                  Name:
                  <input
                    type="text"
                    value={track.name}
                    onChange={(e) => handleTrackChange(track.id, e.target.value, 'name')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="Track Name"
                  />
                </label>

                {/* Genre */}
                <label className="block mb-2">
                  Genre:
                  <input
                    type="text"
                    value={track.genre}
                    onChange={(e) => handleTrackChange(track.id, e.target.value, 'genre')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="Track Genre"
                  />
                </label>

                {/* Track Side */}
                <label className="block mb-2">
                  Side:
                  <input
                    type="text"
                    value={track.side}
                    onChange={(e) => handleTrackChange(track.id, e.target.value, 'side')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="Track Side"
                  />
                </label>

                {/* Key Wheel Selector */}
                <label className="block mb-2">
                  Key:
                  <CamelotWheel
                    selectedKey={track.key}
                    onSelectKey={(newKey: string) => handleTrackChange(track.id, newKey, 'key')}
                  />
                </label>

                {/* Audio Section */}
                <label className="block mb-2">
                  Audio:
                  <AudioRecorder onRecordingComplete={(blob: Blob) => handleTrackChange(track.id, blob, 'audio')} />
                  {track.audio && (
                    <>
                      <AudioVisualizer
                        blob={track.audio}
                        width={500}
                        height={75}
                        barWidth={1}
                        gap={0}
                        barColor={'lightblue'}
                      />
                      <AudioPlayer blob={track.audio as Blob} />
                    </>
                  )}
                </label>


                {/* Track Length */}
                <label className="block mb-2">
                  Length:
                  <input
                    type="text"
                    value={formatSecondsToMinutes(track.length)}
                    onChange={(e) => handleTrackChange(track.id, formatMinutesToSeconds(e.target.value), 'length')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="Track Length"
                    readOnly
                  />
                </label>

                {/* BPM */}
                <label className="block mb-2">
                  BPM:
                  <input
                    type="number"
                    value={track.bpm}
                    onChange={(e) => handleTrackChange(track.id, e.target.value, 'bpm')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="BPM"
                  />
                </label>

                {/* Star Rating */}
                <label className="block mb-2">
                  Rating:
                  <StarRating
                    initialRating={track.rating || 0}
                    onRating={(newRating: number) => handleTrackChange(track.id, newRating, 'rating')}
                  />
                </label>

                {/* Remove Button */}
                <div>
                  <button onClick={() => handleRemoveTrack(track.id)} className="text-red-500 hover:text-red-700">
                    <TrashIcon className="w-6 h-6" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        {/* Add new track */}
        <div className="flex">
          <input
            type="text"
            value={newTrackName}
            onChange={(e) => setNewTrackName(e.target.value)}
            className="w-full p-2 mb-2 mr-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
            placeholder="New Track Name"
          />
          <button onClick={handleAddTrack} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Add Track</button>
        </div>
      </div>
      <div className="printable">
        <PrintReleaseDetails release={release} />
      </div>
      {/* Checkbox if tracks should be analyzed on safe or not */}
      <label className="block mb-2">
        Analyze Tracks:
        <input
          type="checkbox"
          checked={analysis}
          onChange={(e) => setAnalysis(e.target.checked)}
          className="ml-2"
        />
      </label>
      <button onClick={handleSave} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Save</button>
      <button onClick={() => window.print()} className="p-2 ml-2 bg-green-500 rounded hover:bg-green-600">
        Print Details
      </button>
    </div>
  );
};

export default EditRelease;

