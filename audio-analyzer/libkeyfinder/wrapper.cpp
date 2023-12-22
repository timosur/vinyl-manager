// keyfinder_wrapper.cpp
#include "keyfinder/keyfinder.h"

extern "C" {
    KeyFinder::KeyFinder* new_keyfinder() {
        return new KeyFinder::KeyFinder();
    }

    void delete_keyfinder(KeyFinder::KeyFinder* kf) {
        delete kf;
    }

    int analyze_audio(KeyFinder::KeyFinder* kf, float* audio_data, int length, int frame_rate, int channels) {
        KeyFinder::AudioData a;
        a.setFrameRate(frame_rate);
        a.setChannels(channels);
        a.addToSampleCount(length);

        for (int i = 0; i < length; i++) {
            a.setSample(i, audio_data[i]);
        }

        return kf->keyOfAudio(a);
    }
}
