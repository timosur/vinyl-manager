"use client";
import { Key, useEffect, useReducer, useState } from 'react';
import { releaseService } from '@/service/release';
import { Release, Track } from '@/models/Release';
import { StarRating } from '@/components/StarRating';
import router from 'next/router';
import { formatSecondsToMinutes } from '@/helper/time';
import TrashIcon from '@heroicons/react/24/outline/TrashIcon';
import { CamelotWheel } from '@/components/CamelotWheel';
import AudioPlayer from '@/components/AudioPlayer';
import { AudioVisualizer } from 'react-audio-visualize';
import { AudioRecorder } from '@/components/AudioRecorder';


const EditRelease = ({ params }: { params: { id: string } }) => {
  const [release, setRelease] = useState<Release>({} as Release);
  const [newTrackName, setNewTrackName] = useState('');
  const [, forceUpdate] = useReducer(x => x + 1, 0);

  useEffect(() => {
    const fetchRelease = async () => {
      if (!params.id) return;
      const fetchedRelease = await releaseService.getById(params.id as string);
      setRelease(fetchedRelease);
    };
    fetchRelease();
  }, [params.id]);

  const handleRatingChange = (trackId: string, rating: number) => {
    setRelease({
      ...release,
      tracks: release.tracks.map((track) =>
        track.id === trackId ? { ...track, rating } : track
      ),
    });
  };

  const handleAddTrack = () => {
    if (newTrackName) {
      setRelease({
        ...release,
        tracks: [...release.tracks, { id: Date.now().toString(), name: newTrackName, rating: 0 } as Track],
      });
      setNewTrackName('');
    }
  };

  const handleRemoveTrack = (trackId: string) => {
    setRelease({
      ...release,
      tracks: release.tracks.filter((track) => track.id !== trackId),
    });
  };

  const onSelectKey = (trackId: string, newKey: string) => {
    setRelease({
      ...release,
      tracks: release.tracks.map((track) =>
        track.id === trackId ? { ...track, key: newKey } : track
      ),
    });
  };

  const onAudioChangePerTrack = (trackId: string, audio: Blob) => {
    setRelease({
      ...release,
      tracks: release.tracks.map((track) =>
        track.id === trackId ? { ...track, audio } : track
      ),
    });
    forceUpdate();
  }

  console.log('release track id and audio', release.tracks?.map((track) => {
    return { id: track.id, audio: track.audio }
  }));

  const handleSave = async () => {
    await releaseService.update(params.id as string, release);
    router.push(`/release/${params.id}`);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, field: keyof Release) => {
    setRelease({
      ...release,
      [field]: e.target.value,
    });
  };

  if (!release) return <div>Loading...</div>;

  return (
    <div className="text-white bg-[#0e181a] p-6 rounded-lg shadow-md">
      <h1 className="text-2xl mb-4">Edit Release</h1>
      <input
        type="text"
        value={release.name}
        onChange={(e) => handleChange(e, 'name')}
        className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Name"
      />
      {/* Short Release name */}
      <input
        type="text"
        value={release.short}
        onChange={(e) => handleChange(e, 'short')}
        className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Short Release Name"
      />
      {/* Release notes */}
      <textarea
        value={release.notes}
        onChange={(e) => handleChange(e, 'notes')}
        className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Notes"
      />
      <div>
        <h2 className="text-xl mb-2">Tracks</h2>
        {release.tracks?.map((track) => (
          <div key={track.id} className="mb-4">
            {/* Name */}
            <label className="block">
              Name:
              <input
                type="text"
                value={track.name}
                className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                readOnly
              />
            </label>

            {/* Side */}
            <label className="block">
              Side:
              <input
                type="text"
                value={track.side}
                className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                readOnly
              />
            </label>

            {/* Key Wheel Selector */}
            <label className="block">
              Key:
              <CamelotWheel selectedKey={track.key} onSelectKey={(key: string) => onSelectKey(track.id, key)} />
            </label>

            {/* Audio */}
            <label className="block">
              Audio:
              <AudioRecorder onRecordingComplete={(blob: Blob) => onAudioChangePerTrack(track.id, blob)} />
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
                      <AudioPlayer blob={track.audio} />
                  </>
              )}
            </label>

            {/* Length, convert int seconds to readable 00:00 */}
            <label className="block">
              Length:
              <input
                type="text"
                value={formatSecondsToMinutes(track.length)}
                className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                readOnly
              />
            </label>

            {/* BPM */}
            <label className="block">
              BPM:
              <input
                type="text"
                value={track.bpm}
                className="w-full p-3 mb-4 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                readOnly
              />
            </label>

            {/* Star Rating */}
            <label className="block">
              Rating:
              <StarRating trackId={track.id} initialRating={track.rating || 0} onRating={handleRatingChange} />
            </label>

            {/* Remove Button */}
            <button onClick={() => handleRemoveTrack(track.id)} className="mt-2 text-red-500 hover:text-red-700">
              <TrashIcon className="h-5 w-5" />
            </button>
          </div>
        ))}
        <div className="flex mb-4">
          <input
            type="text"
            value={newTrackName}
            onChange={(e) => setNewTrackName(e.target.value)}
            className="flex-grow p-2"
            placeholder="New Track Name"
          />
          <button onClick={handleAddTrack} className="ml-2">Add Track</button>
        </div>
      </div>
      <button onClick={handleSave} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Save</button>
    </div>
  );
};

export default EditRelease;
