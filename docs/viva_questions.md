# Viva Questions and Answers

1. **What are the main components of a rolling bearing?** Inner and outer rings, rolling elements, a cage, and (in sealed variants) seals and lubricant.
2. **What do BPFO and BPFI represent?** The ideal rolling-element passage frequencies at the outer and inner raceways respectively.
3. **What is FTF?** Fundamental train frequency, the cage rotational frequency relative to the bearing geometry.
4. **What is BSF?** Ball spin frequency, the approximate rotation rate of a rolling element about its own axis.
5. **Why do calculated fault frequencies vary with RPM?** The kinematic formulas scale linearly with shaft frequency $f_r=\mathrm{RPM}/60$.
6. **Why can measured peaks differ from theoretical values?** Slip, speed fluctuation, geometry tolerance, contact-angle variation, load zone, finite resolution, and transfer-path effects.
7. **Why use envelope analysis?** It demodulates repeated impacts that excite a high-frequency resonance and exposes their lower repetition frequency.
8. **What does the Hilbert transform provide?** The quadrature component used to form the analytic signal; its magnitude is the signal envelope.
9. **Why band-pass before envelope detection?** To isolate an impact-excited resonance and reduce unrelated components before demodulation.
10. **What does RMS measure?** The effective amplitude or energy level of a vibration window.
11. **How does kurtosis help detect damage?** Impulsive faults can create heavy-tailed amplitude distributions and raise excess kurtosis, though noise and outliers also affect it.
12. **What is crest factor?** Peak absolute amplitude divided by RMS; it indicates whether a few peaks dominate the signal.
13. **What does spectral centroid indicate?** The magnitude-weighted average frequency, often reflecting where spectral content is concentrated.
14. **What is band energy?** The fraction or amount of spectral power inside a defined frequency interval.
15. **Why use multiple feature families?** Time statistics, raw spectra, and envelope spectra capture different aspects of amplitude, resonance, and impact repetition.
16. **Why include colored noise?** Real vibration noise is not perfectly white; filtering introduces frequency-dependent noise energy.
17. **What is the effect of timing jitter?** It spreads ideal spectral lines and makes the synthetic impacts less perfectly periodic.
18. **Why split by simulated run rather than by window?** Windows from one run share operating conditions and random characteristics; grouping reduces train/test leakage.
19. **Why maintain a validation split?** It supports model selection without using the final held-out test set.
20. **How is the synthetic health indicator generated?** It is a noisy clipped version of the simulated severity, not a sensor-derived real-world index.
21. **What does RUL mean here?** Simulated hours remaining from the current observation until severity reaches the specified failure threshold.
22. **Why group RUL splits by bearing life?** Neighboring observations within one degradation trajectory are strongly related and must not cross splits.
23. **Why use an asymmetric RUL score?** Late predictions may carry greater maintenance risk than early predictions, so error direction matters.
24. **What is the most important limitation?** All results use synthetic signals and simulated failure labels; they do not establish physical machine performance.
25. **What is the next validation step?** Evaluate the fixed pipeline on documented real bearing data, then independently on rig data with known operating and fault conditions.