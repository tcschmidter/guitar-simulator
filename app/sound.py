from pydantic import BaseModel
import numpy as np
import pyaudio
import time


class Note(BaseModel):
    name: str
    frequency: float


class Chord(BaseModel):
    name: str
    notes: list[Note]


def generate_guitar_wave(
    frequency, duration, sample_rate=44100, amplitude=0.5
):
    n_samples = int(sample_rate * duration)
    n_period = int(sample_rate / frequency)

    # white noise action
    noise = (2 * np.random.randint(0, 2, n_period) - 1) * amplitude

    # init buffer
    buffer = np.zeros(n_samples)
    buffer[:n_period] = noise

    # karplus-strong algo to make it sound guitary
    for i in range(n_period, n_samples):
        buffer[i] = 0.5 * (buffer[i - n_period] + buffer[i - n_period - 1])

    # envelope to simulate plucking
    envelope = np.exp(-3 * np.linspace(0, duration, n_samples))
    buffer *= envelope

    buffer = np.int16(buffer * 32767)
    return buffer


def play_wave(wave, sample_rate=44100):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True
    )
    stream.write(wave.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()


def play_chord(chord: Chord, duration: float):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    chord_wave = np.zeros(n_samples, dtype=np.float32)

    for note in chord.notes:
        wave = generate_guitar_wave(note.frequency, duration)
        chord_wave += wave.astype(np.float32)

    # normalize chord wave to prevent clipping
    chord_wave = np.int16(chord_wave / np.max(np.abs(chord_wave)) * 32767)
    play_wave(chord_wave)


if __name__ == "__main__":
    notes = {
        "C3": Note(name="C3", frequency=130.81),
        "E4": Note(name="E4", frequency=329.63),
        "G4": Note(name="G4", frequency=392.00),
        "G3": Note(name="G3", frequency=196.00),
        "B3": Note(name="B3", frequency=246.94),
        "D4": Note(name="D4", frequency=293.66),
        "A3": Note(name="A3", frequency=220.00),
        "A4": Note(name="A4", frequency=440.00),
        "F3": Note(name="F3", frequency=174.61),
    }

    chord_progression = [
        Chord(name="C major", notes=[notes["C3"], notes["E4"], notes["G4"]]),
        Chord(name="G major", notes=[notes["G3"], notes["B3"], notes["D4"]]),
        Chord(name="A minor", notes=[notes["A3"], notes["C3"], notes["E4"]]),
        Chord(name="F major", notes=[notes["F3"], notes["A3"], notes["C3"]]),
    ]

    beat_duration = 0.5  # duration of one beat in seconds
    chord_duration = beat_duration * 4  # duration for each chord (four beats)

    start_time = time.time()
    while time.time() - start_time < 10:  # loop for approximately 10 seconds
        for chord in chord_progression:
            print(f"Playing chord: {chord.name}")
            play_chord(chord, chord_duration)
            print(f"Finished playing chord: {chord.name}")

    print("Finished playing chord progression")
