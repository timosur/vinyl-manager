import React, { useState, useEffect } from 'react';

const AudioPlayer = ({ blob }: { blob: Blob }) => {
    const [audioUrl, setAudioUrl] = useState<string | null>(null);

    // This effect will update the audio URL whenever the blob changes
    useEffect(() => {
        if (blob) {
            // Create a URL for the blob
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);

            // Cleanup the URL when the component is unmounted or blob changes
            return () => {
                URL.revokeObjectURL(url);
            };
        }
    }, [blob]);

    return (
        <div>
            {audioUrl && <audio src={audioUrl} controls />}
            {/* You can add a button or other mechanisms to set the blob */}
        </div>
    );
};

export default AudioPlayer;
