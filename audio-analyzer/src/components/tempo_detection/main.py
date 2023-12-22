import math
import wave
import numpy as np
import os
from pydub import AudioSegment
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor

def convert_mp3_to_wav(mp3_file_path):
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio = audio.set_channels(1)  # Ensure mono sound
    audio = audio.set_frame_rate(44100)  # Standard frame rate
    wav_file_path = mp3_file_path.replace(".mp3", ".wav")
    audio.export(wav_file_path, format="wav")
    return wav_file_path

def read_wav(filename):
    with wave.open(filename, "rb") as wf:
        nsamps = wf.getnframes()
        sampwidth = wf.getsampwidth()
        fs = wf.getframerate()

        if nsamps > 0 and fs > 0:
            # Choosing the right format based on sample width
            if sampwidth == 1:  # 8-bit audio
                fmt = 'b'  # signed char
            elif sampwidth == 2:  # 16-bit audio
                fmt = 'h'  # short
            elif sampwidth == 4:  # 32-bit audio
                fmt = 'i'  # int
            else:
                raise ValueError("Unsupported sample width")

            # Reading frames
            frames = wf.readframes(nsamps)
            samps = np.frombuffer(frames, dtype=np.dtype(fmt))

            # Ensure the array is 1-dimensional
            if samps.ndim != 1:
                samps = np.ravel(samps)

            return samps, fs
        else:
            return None, None

def get_tempo(audio_file_path):
    if audio_file_path.lower().endswith(".mp3"):
        audio_file_path = convert_mp3_to_wav(audio_file_path)

    # Process the beats with the RNN processor
    proc = RNNBeatProcessor()
    act = proc(audio_file_path)

    # Track the beats using a dynamic Bayesian network
    tracker = DBNBeatTrackingProcessor(fps=100)
    beats = tracker(act)

    # Compute the BPM from the interval between beats
    if len(beats) > 1:
        bpms = 60.0 / np.diff(beats)
        bpm = np.median(bpms)
    else:
        bpm = None
    
    # cleanup wav file
    if audio_file_path.lower().endswith(".mp3"):
        os.remove(audio_file_path)
        
    return int(bpm)
