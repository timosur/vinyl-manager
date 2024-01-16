"use client";
import { useEffect, useState } from 'react';
import { releaseService } from '@/service/release';
import { Release } from '@/models/Release';
import { StarRating } from '@/components/StarRating';
import { formatMinutesToSeconds, formatSecondsToMinutes } from '@/helper/time';
import TrashIcon from '@heroicons/react/24/outline/TrashIcon';
import { CamelotWheel } from '@/components/CamelotWheel';
import AudioPlayer from '@/components/AudioPlayer';
// ignore TS error for now
// @ts-ignore
import { AudioVisualizer } from 'react-audio-visualize';
import { AudioRecorder } from '@/components/AudioRecorder';
import { PrintReleaseDetails } from '@/components/release/PrintReleaseDetails';
import Image from 'next/image';

const EditRelease = ({ params }: { params: { id: string } }) => {
  const [release, setRelease] = useState<Release>({} as Release);
  const [analysis, setAnalysis] = useState<boolean>(true);
  const [newTrackName, setNewTrackName] = useState('');
  const [newArtistName, setNewArtistName] = useState('');
  const [newLabelName, setNewLabelName] = useState('');

  useEffect(() => {
    const fetchRelease = async () => {
      if (!params.id) return;
      const fetchedRelease = await releaseService.getById(params.id as string);
      setRelease(fetchedRelease);
    };
    fetchRelease();
  }, [params.id]);

  // Add new item to item of type (artist, label, track)
  const handleItemAdd = async (type: 'artist' | 'label' | 'track', name: string) => {
    const newEntity = await releaseService.addItem(type, release.id, name);

    if (!newEntity) return;

    setRelease({
      ...release,
      [type + 's']: [...release[type + 's'], newEntity],
    });
  }

  // Remove item from item of type (artist, label, track)
  const handleItemRemove = async (type: 'artist' | 'label' | 'track', id: string) => {
    await releaseService.deleteItem(type, release.id, id);

    setRelease({
      ...release,
      [type + 's']: release[type + 's'].filter((item: any) => item.id !== id),
    });
  }

  // Change item of type (artist, label, track)
  const handleItemChange = (type: 'track' | 'label' | 'artist', entityId: string, value: any, field: string) => {
    setRelease({
      ...release,
      [type + 's']: release[type + 's'].map((entity: any) =>
        entity.id === entityId ? { ...entity, [field]: value } : entity
      ),
    });
  };

  // Change release field
  const handleChange = (value: any, field: keyof Release) => {
    setRelease({
      ...release,
      [field]: value,
    });
  }

  // Save release
  const handleSave = async () => {
    const updatedRelease = await releaseService.update(params.id as string, release, analysis);

    setRelease(updatedRelease);
  };

  if (!release) return <div>Loading...</div>;

  return (
    <div className="text-white bg-[#0e181a] p-6 rounded-lg shadow-md">
      {/* Buttons to the right */}
      <div className="flex justify-end mb-4">
        {/* Checkbox if tracks should be analyzed on safe or not */}
        <label className="flex items-center mr-2">
          <input
            type="checkbox"
            checked={analysis}
            onChange={(e) => setAnalysis(e.target.checked)}
            className="mr-2"
          />
          Analyze Tracks
        </label>
        {/* Save button */}
        <button onClick={handleSave} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Save</button>
        {/* Print button */}
        <button onClick={() => window.print()} className="p-2 ml-2 bg-green-500 rounded hover:bg-green-600">
          Print Details
        </button>
      </div>
      <h1 className="text-2xl mb-2">Edit Release</h1>
      {/* Release thumbnail image readonly display */}
      <div className="flex mb-2">
        <Image src={release.thumb} width={64} height={64} alt={release.name} />
      </div>
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
      {/* Release genres */}
      <input
        type="text"
        value={release.genre}
        onChange={(e) => handleChange(e.target.value, 'genres')}
        className="w-full p-2 mb-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Genres"
      />
      {/* Release styles */}
      <input
        type="text"
        value={release.styles}
        onChange={(e) => handleChange(e.target.value, 'styles')}
        className="w-full p-2 mb-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Styles"
      />
      {/* Release year */}
      <input
        type="number"
        value={release.year}
        onChange={(e) => handleChange(e.target.value, 'year')}
        className="w-full p-2 mb-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
        placeholder="Release Year"
      />
      {/* Release artists */}
      <h2 className="text-xl mb-2">Artists</h2>
      <div className="flex flex-wrap -mx-2">
        {release.artists?.map((artist, index) => (
          <div key={index} className="w-full md:w-1/2 px-2 mb-4">
            <div className="card bg-gray-800 border border-gray-600 rounded p-4">
              <label className="block mb-2">
                Name:
                <input
                  type="text"
                  value={artist.name}
                  onChange={(e) => handleItemChange('artist', artist.id, e.target.value, 'name')}
                  className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                  placeholder="Artist Name"
                />
              </label>
              {/* Remove */}
              <div>
                <button onClick={() => handleItemRemove('artist', artist.id)} className="text-red-500 hover:text-red-700">
                  <TrashIcon className="w-6 h-6" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      {/* Add new artist */}
      <div className="flex">
        <input
          type="text"
          value={newArtistName}
          onChange={(e) => setNewArtistName(e.target.value)}
          className="w-full p-2 mb-2 mr-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
          placeholder="New Artist Name"
        />
        <button onClick={(e) => handleItemAdd('artist', newArtistName)} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Add Artist</button>
      </div>
      {/* Release labels */}
      <h2 className="text-xl mb-2">Labels</h2>
      <div className="flex flex-wrap -mx-2">
        {release.labels?.map((label, index) => (
          <div key={index} className="w-full md:w-1/2 px-2 mb-4">
            <div className="card bg-gray-800 border border-gray-600 rounded p-4">
              <label className="block mb-2">
                Name:
                <input
                  type="text"
                  value={label.name}
                  onChange={(e) => handleItemChange('label', label.id, e.target.value, 'name')}
                  className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                  placeholder="Label Name"
                />
              </label>
              {/* Remove */}
              <div>
                <button onClick={() => handleItemRemove('label', label.id)} className="text-red-500 hover:text-red-700">
                  <TrashIcon className="w-6 h-6" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      {/* Add label */}
      <div className="flex">
        <input
          type="text"
          value={newLabelName}
          onChange={(e) => setNewLabelName(e.target.value)}
          className="w-full p-2 mb-2 mr-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
          placeholder="New Label Name"
        />
        <button onClick={(e) => handleItemAdd('label', newLabelName)} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Add Label</button>
      </div>
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
                    onChange={(e) => handleItemChange('track', track.id, e.target.value, 'name')}
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
                    onChange={(e) => handleItemChange('track', track.id, e.target.value, 'genre')}
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
                    onChange={(e) => handleItemChange('track', track.id, e.target.value, 'side')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="Track Side"
                  />
                </label>

                {/* Key Wheel Selector */}
                <label className="block mb-2">
                  Key:
                  <CamelotWheel
                    selectedKey={track.key}
                    onSelectKey={(newKey: string) => handleItemChange('track', track.id, newKey, 'key')}
                  />
                </label>

                {/* Audio Section */}
                <label className="block mb-2">
                  Audio:
                  <AudioRecorder onRecordingComplete={(blob: Blob) => handleItemChange('track', track.id, blob, 'audio')} />
                  {track.audio && (
                    <>
                      <AudioVisualizer
                        blob={track.audio}
                        width={300}
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
                    onChange={(e) => handleItemChange('track', track.id, formatMinutesToSeconds(e.target.value), 'length')}
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
                    onChange={(e) => handleItemChange('track', track.id, e.target.value, 'bpm')}
                    className="w-full p-2 bg-gray-800 border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                    placeholder="BPM"
                  />
                </label>

                {/* Star Rating */}
                <label className="block mb-2">
                  Rating:
                  <StarRating
                    initialRating={track.rating || 0}
                    onRating={(newRating: number) => handleItemChange('track', track.id, newRating, 'rating')}
                  />
                </label>

                {/* Remove Button */}
                <div>
                  <button onClick={() => handleItemRemove('track', track.id)} className="text-red-500 hover:text-red-700">
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
          <button onClick={(e) => handleItemAdd('track', newTrackName)} className="p-2 bg-blue-500 rounded hover:bg-blue-600 transition duration-300 ease-in-out">Add Track</button>
        </div>
      </div>
      <div className="printable">
        <PrintReleaseDetails release={release} />
      </div>
    </div>
  );
};

export default EditRelease;

