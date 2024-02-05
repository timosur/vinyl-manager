from pydub import AudioSegment
import ctypes
import os
import numpy as np

from components.key_detection.notations import key_map, camelot, open_key

# Load the wrapper library
lib = ctypes.CDLL(os.environ.get('LIBFINDER_WRAPPER_PATH', './libkeyfinder/wrapper.dylib'))

# Define the functions
new_keyfinder = lib.new_keyfinder
new_keyfinder.restype = ctypes.c_void_p

delete_keyfinder = lib.delete_keyfinder
delete_keyfinder.argtypes = [ctypes.c_void_p]

analyze_audio = lib.analyze_audio
analyze_audio.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int, ctypes.c_int]
analyze_audio.restype = ctypes.c_int

# Get the key name
def get_key_name(key_id):
    # Returns the key name from the key ID
    return key_map.get(key_id, "Unknown")

# Analyze the audio file
def analyze_audio_file(file_path):
    # Load MP3 file with pydub
    audio = AudioSegment.from_file(file_path, format="mp3")
    
    # Convert to a mono signal, normalize, and get raw audio data
    audio_mono = audio.set_channels(1).set_frame_rate(44100)
    audio_data = np.array(audio_mono.get_array_of_samples(), dtype=np.float32)

    # Initialize KeyFinder
    kf = new_keyfinder()
    
    # Analyze audio
    key = analyze_audio(kf, audio_data.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), len(audio_data), audio_mono.frame_rate, audio_mono.channels)
    
    # Cleanup
    delete_keyfinder(kf)
    
    key_name = get_key_name(key)
    camelot_key = camelot[key_name] if key_name in camelot else None
    open_key_key = open_key[key_name] if key_name in open_key else None

    return key_name, camelot_key, open_key_key