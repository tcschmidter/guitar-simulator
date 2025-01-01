import numpy as np
import pyaudio
import time


def generate_guitar_wave(
    frequency, duration, sample_rate=44100, amplitude=0.5
):
    t = np.linspace(0, duration, int(sample_rate * duration), False)

    # fundamental frequency
    wave = amplitude * np.sin(2 * np.pi * frequency * t)

    # harmonics
    wave += (amplitude / 2) * np.sin(2 * np.pi * frequency * 2 * t)
    wave += (amplitude / 4) * np.sin(2 * np.pi * frequency * 3 * t)
    wave += (amplitude / 8) * np.sin(2 * np.pi * frequency * 4 * t)

    # envelope to simulate plucking
    envelope = np.exp(-3 * t)
    wave *= envelope

    wave = np.int16(wave * 32767)
    return wave


def play_wave(wave, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True
    )
    stream.write(wave.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()


def play_note(frequency, duration):
    wave = generate_guitar_wave(frequency, duration)
    play_wave(wave)


if __name__ == "__main__":  # testing
    notes = [
        329.63,
        246.94,
        196.00,
        146.83,
        110.00,
        82.41,
    ]
    duration = 1.0  # 1 second duration for each note

    for note in notes:
        print(f"Playing {note} Hz")
        play_note(note, duration)
        print(f"Finished playing {note} Hz")
        time.sleep(0.5)  # pause between notes

    print("Finished playing all notes")
