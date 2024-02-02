// ignore typescript errors
// @ts-nocheck
import { LiveAudioVisualizer } from 'react-audio-visualize';
import { AudioRecorder as _AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';

export const AudioRecorder = ({ onRecordingComplete }: { onRecordingComplete: (blob: Blob) => void }) => {
    const recorder = useAudioRecorder();

    return (<div>
        <_AudioRecorder
            onRecordingComplete={onRecordingComplete}
            recorderControls={recorder}
            audioTrackConstraints={{
                autoGainControl: false,
                noiseSuppression: false,
                echoCancellation: false,
                channelCount: 1,
                sampleRate: 44100,
                sampleSize: 16,
            }} 
        />

        {recorder.mediaRecorder && (
            <LiveAudioVisualizer
                mediaRecorder={recorder.mediaRecorder}
                width={200}
                height={75}
            />
        )}
    </div>)
};