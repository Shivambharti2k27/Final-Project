# Presentation Guide

## 10-Minute Spoken Script

### 0:00–0:45 — Opening and Problem

“Good morning. My project is titled *Physics-Based Simulation and Machine Learning Framework for Rolling Bearing Fault Diagnosis and Remaining Useful Life Estimation*. Bearings support rotating shafts in motors, pumps, gearboxes, and many other machines. A small defect can produce repeated impacts and, if it grows unnoticed, lead to an unplanned shutdown. I built a reproducible simulation and machine-learning workflow to study two tasks: identifying a fault class and estimating time remaining to a simulated failure threshold.”

### 0:45–1:45 — Mechanics and Fault Frequencies

“The reference geometry is a nominal 6205 deep-groove bearing: nine balls, 7.938 millimetre ball diameter, 39.04 millimetre pitch diameter, and zero contact angle. A defect on the outer race, inner race, or a ball is struck repeatedly as the bearing rotates. The expected rates are BPFO, BPFI, and BSF, with FTF describing cage motion. At 1,800 rpm, my code calculates about 107.55 Hz BPFO, 162.45 Hz BPFI, 70.72 Hz BSF, and 11.95 Hz FTF. Those are ideal kinematic values; slip and real transfer paths can move or spread actual peaks.”

### 1:45–2:40 — Signal Processing

“A defect impact excites a structural resonance. My simulator models a damped 2-to-4-kilohertz ringing response, adds 1.5-percent timing jitter, speed-related modulation, and white plus colored Gaussian noise. To look for the lower impact rate, the feature extractor band-passes the resonance, calculates the Hilbert envelope, then takes its spectrum. In the seeded five-second check at 1,800 rpm, measured envelope peaks were 162.6, 107.6, and 70.8 Hz for inner-race, outer-race, and ball faults respectively, all close to their calculated fundamentals.”

### 2:40–3:35 — Data and Assumptions

“The project uses its own synthetic signals, not CWRU or laboratory measurements. It generated 4,000 classification windows, 1,000 per class, with 4,096 samples at 12 kilohertz. The classes are Healthy, Inner Race, Outer Race, and Ball. There are 80 simulated runs. The RUL dataset has 30 simulated lives with 40 observations each. Each life has a random duration from 40 to 100 simulated hours, and an exponential severity curve approaches a threshold of 0.90. These assumptions are documented; the values are not estimates of actual bearing lifetime.”

### 3:35–4:35 — Features and Splits

“For diagnosis I extract six time statistics, eight FFT statistics and band-energy ratios, and ten envelope features. These summarize amplitude, impulsiveness, frequency distribution, and energy around the bearing characteristic frequencies. I split by complete run: 56 training, 12 validation, and 12 test runs. For RUL I split by complete bearing life: 21, 4, and 5 lives. This prevents adjacent windows from a single simulated unit appearing on both sides of the test.”

### 4:35–5:40 — Diagnosis Models and Results

“The classical models are an RBF SVM, Random Forest, KNN, and Gradient Boosting, compared with a compact one-dimensional CNN trained on raw vibration. In the held-out synthetic runs, all four classical models scored 1.000 accuracy and weighted F1. The raw CNN scored 0.825 accuracy and 0.821 weighted F1. Its confusion matrix shows most mistakes between inner and outer race, with some outer-to-ball and ball-to-healthy errors. The result is unusually strong for the feature models, so I interpret it as evidence that the simulator’s labels are separable, not as evidence of real-world diagnostic accuracy.”

### 5:40–6:25 — Robustness

“The selected classical model scored weighted F1 1.000 across the five simulated noise settings from zero to 20 dB. A separate low-speed/load-to-high-speed/load test scored 0.9125 accuracy and 0.9097 weighted F1. This domain result is separate from the main 56/12/12 grouped test. The noise curve is for the selected feature-based model, not for the CNN.”

### 6:25–7:35 — RUL Results

“For RUL, I compared Random Forest and Gradient Boosting on engineered features with a temporal CNN using the last eight feature observations from each life. The validation-selected classical regressor was Gradient Boosting, with test RMSE 10.22 hours and MAE 7.70 hours. Random Forest had test RMSE 9.92 hours and MAE 7.37 hours, but model selection was done on validation RMSE, not the test set. The temporal CNN scored RMSE 12.72 hours and MAE 9.51 hours. The test set contains just five simulated lives, so the 200 observations are correlated and the uncertainty is substantial.”

### 7:35–8:25 — RUL Score Caveat

“I also report an asymmetric score. During review I found that its code contradicts the stated intention: with error equal to prediction minus true RUL, overestimated RUL is the late and risky error, but the code divides that error by 13 while underestimates use 10. This makes an equal overestimate less costly in the formula. I would not claim the score rewards the intended maintenance risk until its definition is corrected and the results are regenerated.”

### 8:25–9:15 — Dashboard and Real-Data Status

“The dashboard lets a user choose a simulated fault, speed, load, severity, noise, and seed. It displays the waveform, FFT, envelope spectrum with characteristic-frequency markers, and saved model outputs. It generates synthetic input on every interaction; it does not read a real sensor. The optional official CWRU archive attempt returned HTTP 404, so real-data validation was not done.”

### 9:15–10:00 — Conclusion

“In conclusion, this project demonstrates a full, grouped-split simulation workflow that ran end to end and passed six tests. Its strongest result is reproducible synthetic separability and a working RUL comparison, not validated field performance. The next steps are to obtain verified real vibration data, calibrate the simulator, resolve the RUL penalty direction, increase independent run-to-failure units, and report uncertainty. Thank you.”

## 5-Minute Spoken Script

“Good morning. My project uses a physics-based simulator and machine learning to study rolling-bearing fault diagnosis and remaining useful life. Bearings in motors and pumps can develop local race or ball defects. Repeated impacts create vibration that can be analyzed to identify a fault and estimate time to a failure condition.

The simulator uses nominal 6205 geometry: nine balls, 7.938 millimetre ball diameter, 39.04 millimetre pitch diameter, and zero contact angle. From standard ideal-rolling formulas, at 1,800 rpm it computes BPFO 107.55 Hz, BPFI 162.45 Hz, BSF 70.72 Hz, and FTF 11.95 Hz. Impacts excite a damped 2-to-4-kilohertz resonance. The signal has 1.5-percent timing jitter, modulation, and Gaussian plus colored noise. Envelope analysis band-passes the resonance, takes the Hilbert envelope, and reveals the lower impact repetition rate.

All data in this project are synthetic. I generated 4,000 4,096-sample windows at 12 kilohertz across Healthy, Inner Race, Outer Race, and Ball classes, plus 30 run-to-failure lives with 40 observations each. Classification was split by simulated run: 56 train, 12 validation, 12 test. RUL was split by life: 21, 4, and 5. This avoids window leakage between neighboring observations from one simulated unit.

The classifier comparison used SVM, Random Forest, KNN, Gradient Boosting, and a one-dimensional CNN. All four classical methods achieved 1.000 accuracy on held-out synthetic runs; the CNN achieved 0.825. These near-perfect feature scores reveal that the hand-designed simulator makes classes easy to separate. They are not real-world bearing performance. The selected classical model also scored 1.000 weighted F1 at each simulated SNR, while a separate low-to-high operating-domain test scored 0.9125 accuracy.

For RUL, the validation-selected Gradient Boosting regressor achieved test RMSE 10.22 hours and MAE 7.70 hours. Random Forest had 9.92-hour RMSE and 7.37-hour MAE on test; the temporal CNN had 12.72 and 9.51. There are only five held-out synthetic lives, so the result is preliminary. The custom asymmetric score also has a direction bug: the implementation penalizes equally sized underestimates more than dangerous RUL overestimates.

The Streamlit dashboard visualizes a new synthetic condition and model outputs. CWRU download returned HTTP 404, so real-data validation was not done. The project pipeline ran successfully in a temporary verification copy and all six tests passed. The next essential step is evaluation on documented real measurements. Thank you.”

## Dashboard Demo Script

1. Say: “This is a simulator demonstration, not a sensor feed.” Point to the synthetic-only warning before interpreting outputs.
2. Select **Inner Race**, set speed to 1,800 rpm, load to 1.0, severity to 0.8, and SNR to 15 dB. Keep a fixed seed so the displayed waveform is repeatable.
3. Point to the waveform and explain each impact excites the high-frequency structure response.
4. Point to the amplitude FFT and clarify that the resonance itself is high frequency; defect repetition is easier to see after demodulation.
5. Point to the envelope spectrum. Read the marker labels: at 1,800 rpm the inner-race marker is about 162.4 Hz. Explain that marker locations are calculated from ideal geometry, not estimated from a measured bearing.
6. Point to “Predicted fault,” “Estimated RUL,” and the HI. Explain the classifier predicts from engineered synthetic features; the classical regressor estimates RUL from the simulator-like feature vector; the HI shown is the slider severity, not a field health score.
7. Change SNR to 0 dB and note that this is a generated noise setting. Do not claim robustness beyond the plotted synthetic test.
8. Close by stating that CWRU download failed with HTTP 404 and the model has not been validated on real sensor data.

## 30 Tough Examiner Questions and Evidence-Grounded Answers

1. **What is your central contribution?** An executable synthetic workflow joining bearing kinematics, impulse/resonance signal generation, envelope and statistical features, grouped diagnosis/RUL models, metrics, and a dashboard. The whole copy pipeline exited 0.
2. **Is this a physical experiment?** No. Every reported signal and failure label is generated by `src/simulator.py` and `src/degradation.py`; CWRU returned 404.
3. **Why did you choose the 6205 bearing?** It is a common deep-groove bearing with simple standard characteristic-frequency relations. I assume nine balls and the listed nominal diameters; I still need an edition/page-level SKF source for those exact dimensions.
4. **How do you derive BPFO?** The outer race sees `n/2` times shaft rate times the cage/ball geometry factor: `n fr/2 * (1 - d/D cos(theta))`.
5. **How does BPFI differ?** Its geometry factor has a plus sign: `n fr/2 * (1 + d/D cos(theta))`.
6. **What is BSF?** The approximate spin rate of a rolling ball: `D fr/(2d) * (1 - (d/D cos(theta))^2)` in this model.
7. **What is FTF?** Cage rotation rate relative to the bearing: `fr/2 * (1 - d/D cos(theta))`.
8. **What exact 1,800-rpm values did you calculate?** BPFO 107.550461 Hz, BPFI 162.449539 Hz, BSF 70.721782 Hz, FTF 11.950051 Hz. The theory prose's BSF 70.75 is rounded incorrectly.
9. **How did you test the fault peaks?** A 5-second seeded simulation was band-passed 2–4 kHz, Hilbert envelope calculated, then the envelope FFT peak searched around each fundamental. Measured values were 162.6, 107.6, and 70.8 Hz with relative errors 0.093%, 0.046%, and 0.111%.
10. **Why use envelope analysis?** Defect impacts excite high-frequency resonance; the envelope reveals their lower repetition rate, where the characteristic frequencies can be compared.
11. **What is the window frequency resolution?** For 4,096 samples at 12 kHz, the FFT bin spacing is about 2.93 Hz. The unit test uses a longer 5-second window for tighter peak resolution.
12. **Does shaft speed vary inside a window?** No. RPM varies across windows, but `simulate_signal` uses one fixed RPM through a window. Order-tracked variable-speed signals are future work.
13. **How is the noise made?** A 0.72 white Gaussian plus 0.28 low-pass filtered Gaussian mixture is normalized to requested clean-signal SNR; SNR values in the dataset are 0, 5, 10, 15, and 20 dB.
14. **Why do all classical models score 100%?** The synthetic label directly controls characteristic impact periodicity, and the feature extraction explicitly measures relevant spectrum/envelope structure. The result demonstrates simulator separability, not field accuracy.
15. **Could the perfect score be window leakage?** The primary split is by unique run ID. There are 56/12/12 train/validation/test runs, and the main test has 150 windows per class. I did not identify group overlap in that split logic.
16. **Does any preprocessing touch test data?** The StandardScaler is fit through training-only pipelines or on RUL training rows. Medians are computed before split, which is a risk if NaNs appear; both generated feature CSVs had zero numeric NaNs, so no held-out median was used in this run.
17. **What is in the classifier feature vector?** 24 signal features plus RPM and load. It excludes run ID, target, severity, SNR, and domain.
18. **What does the CNN confuse?** It confuses inner with outer race (57 inner windows as outer), outer with ball (33), and 11 ball windows as healthy. The tested CNN F1 is 0.821.
19. **Is the noise curve for every model?** No, it is for the validation-selected classical model, SVM. Its measured weighted F1 was 1.0 across the five SNR groups.
20. **How was the separate domain test made?** Fit the selected model on 1,400 low-speed/load windows from primary training runs, then score 2,000 windows from the high-speed/load domain; accuracy 0.9125, weighted F1 0.9097.
21. **What is your simulated failure law?** Severity starts around 0.025 and increases exponentially toward 0.90 over a random 40–100 hour life, with log-normal perturbation. This is a label generator, not a discovered bearing physics law.
22. **How is true RUL defined?** Simulated failure duration minus current simulated age, clipped at zero at the last observation.
23. **What is the HI?** Severity plus Gaussian noise, clipped between zero and one. It is generated from hidden simulator state, so it is a privileged synthetic input rather than a real sensor-derived health index.
24. **Why do you exclude age and severity?** To avoid directly handing the model the target trajectory or hidden fault parameter; HI is retained as a derived condition proxy. The proxy itself is still favorable to the model.
25. **How many independent test lives do you have?** Five; 200 rows arise from their 40 time points each. Those 200 rows are correlated and are not 200 independent bearings.
26. **Why is Gradient Boosting “best” when Random Forest has lower test RMSE?** It was selected on validation RMSE (13.3968 vs RF 14.0829 h). The test result is reserved for final evaluation; RF happens to score better on the test and should not be selected post hoc.
27. **What is wrong with the asymmetric score?** For error `predicted - actual`, positive means overestimated RUL (late/dangerous), but code divides positive errors by 13 and negative errors by 10. Equal positive errors receive a smaller penalty than negative ones, contrary to the stated intention.
28. **What did the temporal CNN receive?** Life-local rolling contexts up to the latest eight feature observations, padded at the start; no sequence crosses a life boundary. It uses two convolution layers and a scalar output.
29. **Was CWRU validation done?** No. The ZIP URL returned HTTP 404. The project saved the failure status and still completed.
30. **What must happen before maintenance use?** Calibrate and test on measured bearings, hold out complete physical units, document sensor placement/loads/speeds and ground truth, correct the risk score, quantify uncertainty, and validate decision costs. Current point estimates are not maintenance advice.

## 10 Things You Must Be Able to Explain Yourself

1. Derive BPFO, BPFI, BSF, and FTF and explain each geometry term.
2. Explain why defect impacts excite high-frequency resonance and how the Hilbert envelope exposes a repetition frequency.
3. Defend every simulator assumption: resonance band/decay, jitter, noise mix, severity/load scaling, and constant speed per window.
4. Explain the 80-run class dataset and why each run ID stays wholly within one split.
5. Define each feature in physical terms, especially kurtosis, crest factor, band-energy ratios, and envelope fault bands.
6. Explain why 1.000 accuracy is plausible for this synthetic generator and why it is not a real bearing claim.
7. Read the CNN confusion matrix without hiding the inner/outer race overlap.
8. Explain how each of the 30 synthetic lives is generated and why 5 test lives provide weak population evidence.
9. Identify the reversed direction in the asymmetric RUL penalty and explain how you would validate a corrected score.
10. State clearly what the failed CWRU attempt means, what is still manual, and what evidence a real-world claim would require.
