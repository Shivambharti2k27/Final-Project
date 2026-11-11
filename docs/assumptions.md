# Project Assumptions

1. The reference bearing is an SKF 6205-2RS deep-groove ball bearing. The nominal geometry used in calculations is nine rolling elements, 7.938 mm ball diameter, 39.04 mm pitch diameter, and zero-degree contact angle. SKF catalogue variants can differ; verify against the exact product revision used in a physical test.
2. The nominal sampling rate is 12,000 samples/s, each classification or degradation observation is 4,096 samples, and the simulator can use longer windows in physical-frequency regression tests.
3. Fault frequencies use ideal rolling kinematics with no gross slip. Timing jitter approximates 1.5% impact-to-impact variability; it is not a contact mechanics simulation.
4. Fault impacts excite a damped 2–4 kHz structural resonance with approximately 1.5 ms decay. Amplitudes scale with normalized severity and square root of relative load. These are engineering assumptions, not identified parameters from an instrumented rig.
5. Colored noise is a low-pass filtered Gaussian component mixed with white Gaussian noise, scaled to the requested nominal SNR. SNR is measured against the clean synthetic waveform.
6. Classification has four labels: Healthy, Inner Race, Outer Race, and Ball. Combined faults are supported by the signal API but omitted from the requested four-class training benchmark.
7. There are 1,000 windows per class by default, twenty independent simulated runs per class, with 10 runs in each of two speed/load domains. Windows from a run are grouped in one split.
8. Thirty degradation histories have 40 samples each by default. Fault severity grows exponentially from approximately 0.025 to the 0.90 failure threshold, with random life duration and multiplicative variation. The resulting hours and RUL are simulated units, not empirical bearing-life estimates.
9. A noisy severity-derived health indicator is supplied to the RUL model, but direct severity and age are excluded. This remains a favorable synthetic prognostic setup.
10. The deep models are compact CPU-capable PyTorch networks. Fixed random seeds improve repeatability; exact bitwise determinism can still depend on library and hardware implementations.
11. The official CWRU download is optional and may fail because the source URL changes or the environment blocks network access. Successful download inspection does not count as real-data model validation.
12. No output from the simulator is real bearing data. Results must be reported as synthetic-only until a separate, documented real-data evaluation is completed.