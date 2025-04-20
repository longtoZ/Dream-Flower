from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import which
import os

import numpy as np
from pedalboard import Pedalboard, LowpassFilter, HighpassFilter, Reverb, Chorus, PitchShift, Compressor, NoiseGate, Distortion
from pedalboard.io import AudioFile
import io

def digital_theme(input_audio):
    """
    Apply a clean, polished digital style to piano audio.

    Args:
        input_audio (str or AudioSegment): Path to input audio file or AudioSegment object.

    Returns:
        AudioSegment: Processed audio with digital style.
    """
    # Load audio
    if isinstance(input_audio, str):
        audio = AudioSegment.from_file(input_audio)
    else:
        audio = input_audio

    # Convert to pedalboard-compatible format
    temp_path = "temp_digital_input.wav"
    audio.export(temp_path, format="wav")
    with AudioFile(temp_path, "r") as f:
        samples = f.read(f.frames)
        sample_rate = f.samplerate

    # Create digital effect chain
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=80),  # Remove low-end rumble
        Compressor(threshold_db=-20, ratio=3, attack_ms=5, release_ms=50),  # Polish dynamics
        Reverb(room_size=0.2, wet_level=0.15)  # Subtle spaciousness
    ])

    # Apply effects
    processed_samples = board(samples, sample_rate)

    # Save intermediate audio
    temp_out_path = "temp_digital.wav"
    with AudioFile(temp_out_path, "w", sample_rate, processed_samples.shape[0]) as f:
        f.write(processed_samples)

    # Load with pydub for stereo widening and normalization
    processed_audio = AudioSegment.from_file(temp_out_path)
    processed_audio = processed_audio.normalize()  # Maximize clarity
    left = processed_audio.pan(-0.2)  # Slightly left
    right = processed_audio.pan(0.2)  # Slightly right
    final_audio = left.overlay(right) + 3  # Boost gain

    # Clean up
    os.remove(temp_path)
    os.remove(temp_out_path)

    return final_audio

def lofi_theme(input_audio, crackle_path="../sound_effects/vinyl-crackle.mp3"):
    """
    Apply a warm, nostalgic lo-fi style to piano audio.

    Args:
        input_audio (str or AudioSegment): Path to input audio file or AudioSegment object.
        crackle_path (str): Path to vinyl crackle audio file (optional).

    Returns:
        AudioSegment: Processed audio with lo-fi style.
    """
    # Load audio
    if isinstance(input_audio, str):
        audio = AudioSegment.from_file(input_audio)
    else:
        audio = input_audio

    # Convert to pedalboard-compatible format
    temp_path = "temp_lofi_input.wav"
    audio.export(temp_path, format="wav")
    with AudioFile(temp_path, "r") as f:
        samples = f.read(f.frames)
        sample_rate = f.samplerate

    # Create lo-fi effect chain
    board = Pedalboard([
        LowpassFilter(cutoff_frequency_hz=4000),  # Reduce high frequencies
        Reverb(room_size=0.3, damping=0.5, wet_level=0.2),  # Warm ambiance
        NoiseGate(threshold_db=-30, ratio=2, attack_ms=1, release_ms=100)  # Control dynamics
    ])

    # Apply effects
    processed_samples = board(samples, sample_rate)

    # Save intermediate audio
    temp_out_path = "temp_lofi.wav"
    with AudioFile(temp_out_path, "w", sample_rate, processed_samples.shape[0]) as f:
        f.write(processed_samples)

    # Load with pydub
    processed_audio = AudioSegment.from_file(temp_out_path) - 10  # Lower volume

    # Add crackle if available
    if os.path.exists(crackle_path):
        crackle = AudioSegment.from_file(crackle_path) - 20  # Reduce crackle volume
        processed_audio = processed_audio.overlay(crackle, loop=True)

    # Simulate reduced fidelity in-memory
    mp3_buffer = io.BytesIO()
    processed_audio.export(mp3_buffer, format="mp3", bitrate="64k")
    mp3_buffer.seek(0)
    final_audio = AudioSegment.from_file(mp3_buffer, format="mp3")

    # Clean up
    os.remove(temp_path)
    os.remove(temp_out_path)
    mp3_buffer.close()

    return final_audio

def synth_theme(input_audio):
    """
    Apply an electronic, wavy synth style to piano audio.

    Args:
        input_audio (str or AudioSegment): Path to input audio file or AudioSegment object.

    Returns:
        AudioSegment: Processed audio with synth style.
    """
    # Load audio
    if isinstance(input_audio, str):
        audio = AudioSegment.from_file(input_audio)
    else:
        audio = input_audio

    # Convert to pedalboard-compatible format
    temp_path = "temp_synth_input.wav"
    audio.export(temp_path, format="wav")
    with AudioFile(temp_path, "r") as f:
        samples = f.read(f.frames)
        sample_rate = f.samplerate

    # Create synth effect chain
    board = Pedalboard([
        Chorus(rate_hz=0.5, depth=0.7, mix=0.5),  # Wavy, thick sound
        PitchShift(semitones=0.1),  # Subtle detuning
        Reverb(room_size=0.5, wet_level=0.3)  # Spacious feel
    ])

    # Apply effects
    processed_samples = board(samples, sample_rate)

    # Save intermediate audio
    temp_out_path = "temp_synth.wav"
    with AudioFile(temp_out_path, "w", sample_rate, processed_samples.shape[0]) as f:
        f.write(processed_samples)

    # Load with pydub for detuning and panning
    processed_audio = AudioSegment.from_file(temp_out_path)
    sped_up = processed_audio.speedup(playback_speed=1.02)  # Slight pitch shift
    synth_audio = processed_audio.overlay(sped_up) + 5  # Layer and boost gain
    left = synth_audio.pan(-0.3)  # Wide stereo
    right = synth_audio.pan(0.3)
    final_audio = left.overlay(right)

    # Clean up
    os.remove(temp_path)
    os.remove(temp_out_path)

    return final_audio

def vhs_theme(input_audio, noise_path="../sound_effects/vinyl-crackle.mp3"):
    """
    Apply a retro, degraded VHS-style to piano audio with tape warble and noise.

    Args:
        input_audio (str or AudioSegment): Path to input audio file or AudioSegment object.
        noise_path (str): Path to noise audio file (optional).

    Returns:
        AudioSegment: Processed audio with VHS style.
    """
    # Load audio
    if isinstance(input_audio, str):
        audio = AudioSegment.from_file(input_audio)
    else:
        audio = input_audio

    # Convert to pedalboard-compatible format
    temp_path = "temp_vhs_input.wav"
    audio.export(temp_path, format="wav")
    with AudioFile(temp_path, "r") as f:
        samples = f.read(f.frames)
        sample_rate = f.samplerate

    # Create VHS effect chain
    board = Pedalboard([
        LowpassFilter(cutoff_frequency_hz=3000),  # Muffled tape sound
        Distortion(drive_db=6),  # Slight tape saturation
        Chorus(rate_hz=0.2, depth=0.4, mix=0.3),  # Tape warble
        Reverb(room_size=0.4, wet_level=0.2)  # Subtle ambiance
    ])

    # Apply effects
    processed_samples = board(samples, sample_rate)

    # Custom numpy distortion for tape-like clipping
    processed_samples = np.clip(processed_samples * 1.3, -1.0, 1.0)

    # Save intermediate audio
    temp_out_path = "temp_vhs.wav"
    with AudioFile(temp_out_path, "w", sample_rate, processed_samples.shape[0]) as f:
        f.write(processed_samples)

    # Load with pydub
    processed_audio = AudioSegment.from_file(temp_out_path) - 12  # Lower volume

    # Add noise if available
    if os.path.exists(noise_path):
        noise = AudioSegment.from_file(noise_path) - 15  # Softer noise
        processed_audio = processed_audio.overlay(noise, loop=True)

    # Simulate tape degradation in-memory
    mp3_buffer = io.BytesIO()
    processed_audio.export(mp3_buffer, format="mp3", bitrate="48k")
    mp3_buffer.seek(0)
    final_audio = AudioSegment.from_file(mp3_buffer, format="mp3")

    # Clean up
    os.remove(temp_path)
    os.remove(temp_out_path)
    mp3_buffer.close()

    return final_audio

AudioSegment.converter = "../ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "../ffmpeg-build/bin/ffmpeg.exe"
AudioSegment.ffprobe = "../ffmpeg-build/bin/ffprobe.exe"

note_sounds = {
    "A1": AudioSegment.from_mp3("../sounds_modify/A1.mp3"),
}

a1 = AudioSegment.from_mp3("../sounds_modify/A1.mp3")
a1_lofi = lofi_theme(a1)
a1_digital = digital_theme(a1)
a1_synth = synth_theme(a1)
a1_vhs = vhs_theme(a1)

# Play the processed audio
a1_lofi.export("A1_lofi.mp3", format="mp3")
a1_digital.export("A1_digital.mp3", format="mp3")
a1_synth.export("A1_synth.mp3", format="mp3")
a1_vhs.export("A1_vhs.mp3", format="mp3")