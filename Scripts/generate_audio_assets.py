import os
import wave
import math
import struct
import random

def generate_audio():
    audio_dir = "/Users/marcopolo/Documents/Unreal Projects/VrMpc/Content/Audio"
    os.makedirs(audio_dir, exist_ok=True)
    sample_rate = 44100

    # 1. ENGINE LOOP (2.0s seamless loop)
    engine_file = os.path.join(audio_dir, "Engine_Loop.wav")
    duration = 2.0
    num_samples = int(sample_rate * duration)
    base_freq = 55.0  # 55 Hz = A1 (low idling/revving V8 fundamental)

    with wave.open(engine_file, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            # Combustion cylinder firing harmonics
            h1 = math.sin(2.0 * math.pi * base_freq * t)
            h2 = 0.6 * math.sin(2.0 * math.pi * base_freq * 2.0 * t)
            h3 = 0.4 * math.sin(2.0 * math.pi * base_freq * 3.0 * t)
            h4 = 0.25 * math.sin(2.0 * math.pi * base_freq * 4.0 * t)
            h5 = 0.15 * math.sin(2.0 * math.pi * base_freq * 5.0 * t)
            
            # 4-cylinder firing pulse envelope
            pulse = 0.7 + 0.3 * math.sin(2.0 * math.pi * (base_freq / 2.0) * t)
            
            # Exhaust rumble
            sub = 0.5 * math.sin(2.0 * math.pi * (base_freq / 2.0) * t)
            
            val = (h1 + h2 + h3 + h4 + h5) * pulse + sub
            val = val * 0.45  # Normalize volume
            
            sample = int(max(-1.0, min(1.0, val)) * 32767.0)
            frames.extend(struct.pack('<h', sample))
            
        wav.writeframes(frames)
    print(f"Generated: {engine_file}")

    # 2. POLICE SIREN (2.0s seamless wail loop)
    siren_file = os.path.join(audio_dir, "Police_Siren.wav")
    duration = 2.0
    num_samples = int(sample_rate * duration)

    with wave.open(siren_file, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        phase = 0.0
        for i in range(num_samples):
            t = float(i) / sample_rate
            # 1 Hz modulation cycle: sweeps from 700 Hz to 1350 Hz and back
            mod = 0.5 * (1.0 + math.sin(2.0 * math.pi * 1.0 * t - math.pi / 2.0))
            inst_freq = 700.0 + mod * 650.0
            
            phase += 2.0 * math.pi * inst_freq / sample_rate
            if phase > 2.0 * math.pi:
                phase -= 2.0 * math.pi
                
            val = 0.7 * math.sin(phase) + 0.25 * math.sin(phase * 2.0) + 0.1 * math.sin(phase * 3.0)
            val = val * 0.55
            
            sample = int(max(-1.0, min(1.0, val)) * 32767.0)
            frames.extend(struct.pack('<h', sample))
            
        wav.writeframes(frames)
    print(f"Generated: {siren_file}")

    # 3. COPILOT RADIO BEEP (0.3s chirp)
    beep_file = os.path.join(audio_dir, "Copilot_Radio.wav")
    duration = 0.35
    num_samples = int(sample_rate * duration)

    with wave.open(beep_file, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            if t < 0.12:
                # First tone: 880 Hz
                val = 0.6 * math.sin(2.0 * math.pi * 880.0 * t)
            elif t < 0.24:
                # Second tone: 1320 Hz
                val = 0.6 * math.sin(2.0 * math.pi * 1320.0 * t)
            else:
                # Squelch noise burst
                val = (random.random() * 2.0 - 1.0) * 0.15 * (1.0 - (t - 0.24) / 0.11)
                
            sample = int(max(-1.0, min(1.0, val)) * 32767.0)
            frames.extend(struct.pack('<h', sample))
            
        wav.writeframes(frames)
    print(f"Generated: {beep_file}")

if __name__ == "__main__":
    generate_audio()

