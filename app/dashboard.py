"""Interactive synthetic bearing diagnosis and RUL dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.signal import butter, hilbert, sosfilt

from src.features import extract_features
from src.simulator import FS_HZ, FAULT_TYPES, fault_frequencies, simulate_signal

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"

st.set_page_config(page_title="Bearing Condition Monitor", page_icon="B", layout="wide")
st.title("Rolling Bearing Condition Monitor")
st.caption("Physics-based 6205 bearing simulation | 12 kHz sampling")

with st.sidebar:
    st.header("Operating condition")
    fault = st.selectbox("Simulated fault", FAULT_TYPES)
    speed = st.slider("Shaft speed (rpm)", 1500, 3000, 1800, step=50)
    load = st.slider("Radial load (relative)", 0.2, 2.0, 1.0, step=0.1)
    severity = st.slider("Fault severity", 0.0, 1.0, 0.65, step=0.05)
    noise = st.slider("Signal-to-noise ratio (dB)", 0, 20, 10, step=1)
    seed = st.number_input("Repeatable seed", min_value=0, value=42, step=1)

rng = np.random.default_rng(int(seed))
signal = simulate_signal(fault, speed, load, severity, noise, 4096, FS_HZ, rng)
time_ms = np.arange(len(signal)) / FS_HZ * 1000
spectrum = np.abs(np.fft.rfft(signal - signal.mean()))
frequency_axis = np.fft.rfftfreq(len(signal), 1 / FS_HZ)
resonance = sosfilt(butter(4, [2000, 4000], btype="bandpass", fs=FS_HZ, output="sos"), signal)
envelope = np.abs(hilbert(resonance))
envelope_spectrum = np.abs(np.fft.rfft(envelope - envelope.mean()))
envelope_axis = np.fft.rfftfreq(len(envelope), 1 / FS_HZ)
frequencies = fault_frequencies(speed)

col_wave, col_freq = st.columns(2)
with col_wave:
    st.subheader("Vibration waveform")
    fig, axis = plt.subplots(figsize=(8, 3.0))
    axis.plot(time_ms, signal, color="#176b66", linewidth=0.8)
    axis.set(xlabel="Time (ms)", ylabel="Acceleration (a.u.)")
    axis.grid(alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)
with col_freq:
    st.subheader("Amplitude spectrum")
    fig, axis = plt.subplots(figsize=(8, 3.0))
    axis.plot(frequency_axis, spectrum, color="#c05640", linewidth=0.8)
    axis.set(xlim=(0, 6000), xlabel="Frequency (Hz)", ylabel="Amplitude (a.u.)")
    axis.grid(alpha=0.2)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

st.subheader("Resonance-envelope spectrum")
fig, axis = plt.subplots(figsize=(12, 3.4))
axis.plot(envelope_axis, envelope_spectrum, color="#526e9e", linewidth=0.8)
axis.set(xlim=(0, 500), xlabel="Frequency (Hz)", ylabel="Envelope amplitude (a.u.)")
for marker_name, marker_frequency, marker_color in (
    ("BPFO", frequencies.bpfo, "#198754"), ("BPFI", frequencies.bpfi, "#dc3545"),
    ("BSF", frequencies.bsf, "#d97706"), ("FTF", frequencies.ftf, "#6f42c1"),
):
    axis.axvline(marker_frequency, linestyle="--", linewidth=1,
                 label=f"{marker_name} {marker_frequency:.1f} Hz", color=marker_color)
axis.legend(ncol=4, frameon=False)
axis.grid(alpha=0.2)
fig.tight_layout()
st.pyplot(fig, clear_figure=True)

feature_values = extract_features(signal, speed)
feature_values.update({"rpm": speed, "load": load, "snr_db": noise})
predicted_fault = "Model unavailable"
predicted_rul = None
classifier_path = MODEL_DIR / "fault_classifier.joblib"
columns_path = MODEL_DIR / "fault_feature_columns.json"
if classifier_path.exists() and columns_path.exists():
    classifier = joblib.load(classifier_path)
    columns = json.loads(columns_path.read_text(encoding="utf-8"))
    classifier_input = np.asarray([[feature_values.get(name, 0.0) for name in columns]], dtype=np.float32)
    predicted_fault = FAULT_TYPES[int(classifier.predict(classifier_input)[0])]
preprocessing_path = MODEL_DIR / "rul_preprocessing.joblib"
regressor_path = MODEL_DIR / "rul_regressor.joblib"
if preprocessing_path.exists() and regressor_path.exists():
    preprocessing = joblib.load(preprocessing_path)
    rul_values = {**feature_values, "health_indicator": severity}
    rul_input = np.asarray([[
        rul_values.get(name, preprocessing["median"].get(name, 0.0))
        for name in preprocessing["columns"]
    ]], dtype=np.float32)
    predicted_rul = max(0.0, float(joblib.load(regressor_path).predict(rul_input)[0]))

col_class, col_rul, col_hi = st.columns(3)
col_class.metric("Predicted fault", predicted_fault)
col_rul.metric("Estimated RUL", f"{predicted_rul:.1f} h" if predicted_rul is not None else "Model unavailable")
col_hi.metric("Simulated health indicator", f"{severity:.2f} / 1.00")
st.caption("Predictions are trained on the project's synthetic simulations; they are not validated diagnostic advice.")
