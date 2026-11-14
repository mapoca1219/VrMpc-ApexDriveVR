#!/usr/bin/env python3
"""
Apex Drive VR: Cyberpunk Synthwave Soundtrack Synthesizer
Generates an original, high-energy 128 BPM electronic synthwave racing soundtrack
synchronized with the 158-second competition trailer.
"""

import numpy as np
import wave
import os

SAMPLE_RATE = 48000
DURATION = 158.0
BPM = 128.0
BEAT_LEN = 60.0 / BPM
SIXTEENTH = BEAT_LEN / 4.0

num_samples = int(DURATION * SAMPLE_RATE)
left = np.zeros(num_samples, dtype=np.float32)
right = np.zeros(num_samples, dtype=np.float32)

print(f">>> Synthesizing 128 BPM Cyberpunk Racing Anthem ({DURATION}s, {num_samples} samples)...")

# Chord root frequencies (Dm - Bb - F - C)
CHORD_ROOTS = [
    73.42,  # D2
    58.27,  # Bb1
    87.31,  # F2
    65.41   # C2
]

CHORD_PADS = [
    [146.83, 174.61, 220.00, 293.66],  # Dm (D3, F3, A3, D4)
    [116.54, 146.83, 174.61, 233.08],  # Bb (Bb2, D3, F3, Bb3)
    [174.61, 220.00, 261.63, 349.23],  # F  (F3, A3, C4, F4)
    [130.81, 164.81, 196.00, 261.63]   # C  (C3, E3, G3, C4)
]

# 1. KICK DRUM
kick_len = int(0.24 * SAMPLE_RATE)
t_k = np.linspace(0, 0.24, kick_len, endpoint=False)
k_freq = 160.0 * np.exp(-t_k * 28.0) + 40.0
kick_wave = np.sin(2.0 * np.pi * np.cumsum(k_freq) / SAMPLE_RATE) * np.exp(-t_k * 13.0)

# 2. SNARE DRUM
snare_len = int(0.22 * SAMPLE_RATE)
t_s = np.linspace(0, 0.22, snare_len, endpoint=False)
noise = np.random.uniform(-1.0, 1.0, snare_len)
body = np.sin(2.0 * np.pi * 185.0 * t_s) * np.exp(-t_s * 22.0)
snare_wave = (noise * 0.65 + body * 0.35) * np.exp(-t_s * 14.0)

# 3. HI-HATS
hat_len = int(0.06 * SAMPLE_RATE)
t_h = np.linspace(0, 0.06, hat_len, endpoint=False)
hat_wave = np.random.uniform(-1.0, 1.0, hat_len) * np.exp(-t_h * 55.0)

open_hat_len = int(0.18 * SAMPLE_RATE)
t_oh = np.linspace(0, 0.18, open_hat_len, endpoint=False)
open_hat_wave = np.random.uniform(-1.0, 1.0, open_hat_len) * np.exp(-t_oh * 18.0)

# Place Drums across the timeline (starting with intro buildup at 4s, full at 8s, outro fade at 148s)
total_beats = int(DURATION / BEAT_LEN)
for b in range(total_beats):
    t_sec = b * BEAT_LEN
    idx = int(t_sec * SAMPLE_RATE)
    if idx >= num_samples:
        break
    
    # Energy envelope based on video sections
    is_intro = (t_sec < 7.5)
    is_outro = (t_sec > 147.5)
    
    # Kick
    if not is_outro:
        if is_intro and b % 2 == 0:
            k_gain = 0.45 * (t_sec / 7.5)
        elif not is_intro:
            k_gain = 0.68
        else:
            k_gain = 0.0
        
        if k_gain > 0.01:
            end = min(idx + kick_len, num_samples)
            left[idx:end] += kick_wave[:end-idx] * k_gain
            right[idx:end] += kick_wave[:end-idx] * k_gain
    
    # Snare on 2 and 4 (beats 1, 3 in 0-indexed)
    if not is_intro and not is_outro:
        if b % 2 == 1:
            end = min(idx + snare_len, num_samples)
            left[idx:end] += snare_wave[:end-idx] * 0.58
            right[idx:end] += snare_wave[:end-idx] * 0.58
            
        # Snare rolls before major drops (e.g. at 7s, 72s, 138s)
        if (7.0 <= t_sec < 8.0) or (72.0 <= t_sec < 74.0) or (138.0 <= t_sec < 140.0):
            roll_sub = int(SIXTEENTH * SAMPLE_RATE)
            for sub in range(4):
                s_idx = idx + sub * roll_sub
                s_end = min(s_idx + snare_len, num_samples)
                if s_idx < num_samples:
                    left[s_idx:s_end] += snare_wave[:s_end-s_idx] * 0.35
                    right[s_idx:s_end] += snare_wave[:s_end-s_idx] * 0.35

    # Hi-Hats (16th notes)
    if not is_outro:
        for sub in range(4):
            h_idx = idx + int(sub * SIXTEENTH * SAMPLE_RATE)
            if h_idx >= num_samples:
                break
            h_gain = 0.18 if (sub % 2 == 0) else 0.28
            if is_intro:
                h_gain *= (t_sec / 7.5)
            
            # Offbeat open hat
            if sub == 2 and not is_intro:
                h_end = min(h_idx + open_hat_len, num_samples)
                left[h_idx:h_end] += open_hat_wave[:h_end-h_idx] * 0.22
                right[h_idx:h_end] += open_hat_wave[:h_end-h_idx] * 0.22
            else:
                h_end = min(h_idx + hat_len, num_samples)
                left[h_idx:h_end] += hat_wave[:h_end-h_idx] * h_gain
                right[h_idx:h_end] += hat_wave[:h_end-h_idx] * h_gain

# 4. ROLLING SYNTHWAVE BASSLINE (16th notes)
def make_bass_note(freq, length):
    t_n = np.linspace(0, length, int(length * SAMPLE_RATE), endpoint=False)
    # Warm analog bass: fundamental + 2nd + 3rd harmonics + subtle sub-octave
    w = (np.sin(2.0 * np.pi * freq * t_n) * 1.0 +
         np.sin(4.0 * np.pi * freq * t_n) * 0.55 +
         np.sin(6.0 * np.pi * freq * t_n) * 0.25 +
         np.sin(1.0 * np.pi * freq * t_n) * 0.45)
    env = np.exp(-t_n * 9.0)
    return w * env

total_sixteenths = int(DURATION / SIXTEENTH)
for s in range(total_sixteenths):
    t_sec = s * SIXTEENTH
    if t_sec < 7.5 or t_sec > 147.5:
        continue
    
    # Chord changes every 2 bars (8 beats = 32 sixteenths)
    chord_idx = (s // 32) % len(CHORD_ROOTS)
    root_f = CHORD_ROOTS[chord_idx]
    
    # Octave jump rhythm (classic synthwave galloping pattern)
    step_in_beat = s % 4
    if step_in_beat == 0:
        f = root_f
    elif step_in_beat == 1:
        f = root_f * 2.0
    elif step_in_beat == 2:
        f = root_f
    else:
        f = root_f * 2.0
        
    bw = make_bass_note(f, SIXTEENTH * 0.92)
    b_idx = int(t_sec * SAMPLE_RATE)
    b_end = min(b_idx + len(bw), num_samples)
    
    gain = 0.52
    left[b_idx:b_end] += bw[:b_end-b_idx] * gain
    right[b_idx:b_end] += bw[:b_end-b_idx] * gain

# 5. STEREO SYNTH ARPEGGIATOR (16th notes climbing D minor scale)
ARP_SCALES = [
    [293.66, 349.23, 440.00, 587.33, 523.25, 440.00, 349.23, 392.00],  # Dm arp
    [233.08, 293.66, 349.23, 466.16, 440.00, 349.23, 293.66, 329.63],  # Bb arp
    [349.23, 440.00, 523.25, 698.46, 587.33, 523.25, 440.00, 493.88],  # F arp
    [261.63, 329.63, 392.00, 523.25, 493.88, 392.00, 329.63, 349.23]   # C arp
]

def make_arp_note(freq, length):
    t_n = np.linspace(0, length, int(length * SAMPLE_RATE), endpoint=False)
    # Bright pluck: triangle/saw mix
    w = (np.sin(2.0 * np.pi * freq * t_n) * 0.8 +
         np.sin(4.0 * np.pi * freq * t_n) * 0.4 +
         np.sin(6.0 * np.pi * freq * t_n) * 0.2)
    env = np.exp(-t_n * 16.0)
    return w * env

for s in range(total_sixteenths):
    t_sec = s * SIXTEENTH
    if t_sec < 4.0 or t_sec > 152.0:
        continue
    
    chord_idx = (s // 32) % len(ARP_SCALES)
    scale = ARP_SCALES[chord_idx]
    f = scale[s % len(scale)]
    
    aw = make_arp_note(f, SIXTEENTH * 0.85)
    a_idx = int(t_sec * SAMPLE_RATE)
    a_end = min(a_idx + len(aw), num_samples)
    
    # Stereo panning that oscillates smoothly left/right
    pan = np.sin(s * 0.35) * 0.65  # -0.65 (left) to +0.65 (right)
    l_pan = (1.0 - pan) * 0.5
    r_pan = (1.0 + pan) * 0.5
    
    a_gain = 0.32
    if t_sec < 8.0:
        a_gain *= (t_sec - 4.0) / 4.0
    elif t_sec > 147.0:
        a_gain *= (152.0 - t_sec) / 5.0
        
    left[a_idx:a_end] += aw[:a_end-a_idx] * (a_gain * l_pan)
    right[a_idx:a_end] += aw[:a_end-a_idx] * (a_gain * r_pan)

# 6. WARM ANALOG CHORD PADS & DRONES (continuous background warmth)
pad_step_len = int(BEAT_LEN * 8 * SAMPLE_RATE) # 2 bars
num_chords = int(num_samples / pad_step_len) + 1
for c in range(num_chords):
    c_start = c * pad_step_len
    c_end = min(c_start + pad_step_len, num_samples)
    if c_start >= num_samples:
        break
    
    t_pad = np.linspace(0, (c_end - c_start) / SAMPLE_RATE, c_end - c_start, endpoint=False)
    chord_idx = c % len(CHORD_PADS)
    pad_notes = CHORD_PADS[chord_idx]
    
    pad_wave = np.zeros(len(t_pad), dtype=np.float32)
    for f in pad_notes:
        # Subtle detuned chorus
        pad_wave += np.sin(2.0 * np.pi * (f - 0.4) * t_pad) * 0.25
        pad_wave += np.sin(2.0 * np.pi * (f + 0.4) * t_pad) * 0.25
        
    # Attack and release envelope
    fade_len = min(int(0.6 * SAMPLE_RATE), len(t_pad) // 2)
    env = np.ones(len(t_pad), dtype=np.float32)
    env[:fade_len] = np.linspace(0, 1, fade_len)
    env[-fade_len:] = np.linspace(1, 0, fade_len)
    
    pad_gain = 0.24
    t_sec_start = c_start / SAMPLE_RATE
    if t_sec_start > 146.0:
        pad_gain *= max(0.0, (158.0 - t_sec_start) / 12.0)
        
    left[c_start:c_end] += pad_wave * env * pad_gain
    right[c_start:c_end] += pad_wave * env * pad_gain

# 7. RISERS AND IMPACTS
def add_riser(start_sec, dur_sec=3.5):
    idx = int(start_sec * SAMPLE_RATE)
    r_len = int(dur_sec * SAMPLE_RATE)
    end = min(idx + r_len, num_samples)
    t_r = np.linspace(0, dur_sec, end - idx, endpoint=False)
    # Exponential frequency sweep from 150Hz to 1200Hz
    f_sweep = 150.0 * np.exp(t_r * (np.log(1200.0/150.0) / dur_sec))
    r_wave = np.sin(2.0 * np.pi * np.cumsum(f_sweep) / SAMPLE_RATE) * (t_r / dur_sec)**2
    # Add white noise sweep
    r_noise = np.random.uniform(-1.0, 1.0, end - idx) * (t_r / dur_sec)**2
    combined = (r_wave * 0.4 + r_noise * 0.3) * 0.35
    left[idx:end] += combined
    right[idx:end] += combined

add_riser(3.8, 3.7)   # Launch drop at 7.5s
add_riser(70.0, 3.5)  # Police combat drop at 73.5s
add_riser(136.0, 3.5) # Final lap victory sprint at 139.5s

# 8. MASTER LIMITER & NORMALIZATION
print(">>> Mastering and normalizing soundtrack...")
peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 0.001)
print(f">>> Raw Peak Level: {peak:.3f}")
target_peak = 0.88
left = (left / peak) * target_peak
right = (right / peak) * target_peak

# Soft knee limiter
left = np.tanh(left) * 0.85
right = np.tanh(right) * 0.85

int_left = (left * 32767).astype(np.int16)
int_right = (right * 32767).astype(np.int16)
interleaved = np.empty((num_samples * 2,), dtype=np.int16)
interleaved[0::2] = int_left
interleaved[1::2] = int_right

out_path = "scratch/synthwave_racing_soundtrack.wav"
with wave.open(out_path, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(interleaved.tobytes())

file_mb = os.path.getsize(out_path) / (1024 * 1024)
print(f">>> [SUCCESS] Master soundtrack created: {out_path} ({file_mb:.2f} MB)")
