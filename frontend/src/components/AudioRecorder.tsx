import { LiveAudioVisualizer } from 'react-audio-visualize';
import { AudioRecorder as _AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';

export const AudioRecorder = ({ onRecordingComplete }: { onRecordingComplete: (blob: Blob) => void }) => {
    const recorder = useAudioRecorder();

    return (<div>
        <_AudioRecorder
            onRecordingComplete={onRecordingComplete}
            recorderControls={recorder}
            audioTrackConstraints={{
                noiseSuppression: false,
                echoCancellation: false,
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