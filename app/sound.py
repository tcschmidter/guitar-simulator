from pydantic import BaseModel
import numpy as np
import pyaudio
import time

class Note(BaseModel):
    name: str
    frequency: float

def generate_guitar_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
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
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True)
    stream.write(wave.tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_note(note: Note, duration: float):
    wave = generate_guitar_wave(note.frequency, duration)
    play_wave(wave)

def play_chord(notes, duration):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    chord_wave = np.zeros(n_samples, dtype=np.float32)

    for note in notes:
        wave = generate_guitar_wave(note.frequency, duration)
        chord_wave += wave.astype(np.float32)

    # normalize chord wave to prevent clipping
    chord_wave = np.int16(chord_wave / np.max(np.abs(chord_wave)) * 32767)
    play_wave(chord_wave)

if __name__ == "__main__":
    notes = [
        Note(name="C4", frequency=261.63),
        Note(name="E4", frequency=329.63),
        Note(name="G4", frequency=392.00),
        Note(name="G3", frequency=196.00),
        Note(name="B3", frequency=246.94),
        Note(name="D4", frequency=293.66),
        Note(name="A3", frequency=220.00),
        Note(name="A4", frequency=440.00),
        Note(name="F3", frequency=174.61),
        Note(name="C3", frequency=130.81)
    ]

    chord_progression = [
        ["C3", "E4", "G4"],  # C major
        ["G3", "B3", "D4"],  # G major
        ["A3", "C4", "E4"],  # A minor
        ["F3", "A3", "C4"]   # F major
    ]

    beat_duration = 0.1  # duration of one beat in seconds
    chord_duration = beat_duration * 4  # duration for each chord (four beats)

    start_time = time.time()
    while time.time() - start_time < 10:  # loop for approximately 10 seconds
        for chord in chord_progression:
            print(f"Playing chord: {', '.join(chord)}")
            play_chord([note for note in notes if note.name in chord], chord_duration)
            print(f"Finished playing chord: {', '.join(chord)}")

    print("Finished playing chord progression")