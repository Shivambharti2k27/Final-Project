# Bearing Mechanics and Signal-Processing Theory

## Rolling-bearing structure

A rolling bearing comprises an inner ring fitted to the shaft, an outer ring fitted to the housing, rolling elements, and a cage that spaces the rolling elements. In a 6205-2RS deep-groove bearing, two elastomer seals protect the lubricant and rolling contact. A localized defect in a raceway or rolling element periodically enters the loaded contact zone and produces an impact. The housing and mounting act as a frequency-dependent transfer path, often making a high-frequency resonance band more visible than the low-frequency impact itself.

All nominal calculations here use SKF 6205-2RS geometry: rolling-element count $n=9$, ball diameter $d=7.938\,\mathrm{mm}$, pitch diameter $D=39.04\,\mathrm{mm}$, and contact angle $\theta=0^\circ$. Confirm dimensions against the exact SKF product variant and catalogue revision before applying to a physical bearing.

## Fault classes

- **Healthy:** baseline shaft-related vibration and noise without a modeled localized defect.
- **Inner-race fault:** impacts recur as the inner race rotates through the stationary load zone. Amplitude can be modulated at shaft frequency.
- **Outer-race fault:** a defect fixed relative to the housing experiences repeated rolling-element passage. A stationary load zone can make this relatively periodic.
- **Ball fault:** a rolling-element defect rotates through contact zones; impact amplitudes are modulated by cage motion and may have slip-related variability.
- **Combined fault:** two or more defect sources are superposed. The simulator supports inner/outer superposition, although the classification benchmark uses the four requested classes above.

## Characteristic frequencies

Let $f_r=\mathrm{RPM}/60$ be shaft rotational frequency in Hz, $n$ the number of rolling elements, $d$ the ball diameter, $D$ the pitch diameter, and $\theta$ the contact angle. For ideal rolling kinematics:

$$
\mathrm{FTF}=\frac{f_r}{2}\left(1-\frac{d}{D}\cos\theta\right)
$$

$$
\mathrm{BPFO}=\frac{n f_r}{2}\left(1-\frac{d}{D}\cos\theta\right),\qquad
\mathrm{BPFI}=\frac{n f_r}{2}\left(1+\frac{d}{D}\cos\theta\right)
$$

$$
\mathrm{BSF}=\frac{D f_r}{2d}\left[1-\left(\frac{d}{D}\cos\theta\right)^2\right]
$$

For the nominal geometry at 1,800 rpm ($f_r=30$ Hz), the simulator calculates BPFO $\approx107.55$ Hz, BPFI $\approx162.45$ Hz, BSF $\approx70.75$ Hz, and FTF $\approx11.95$ Hz. These are kinematic fundamentals. Real spectra can show harmonics, sidebands, slip, load-zone effects, and transfer-path changes; observed peaks need not coincide exactly.

## Envelope analysis

Localized impacts excite high-frequency structural resonances. Envelope analysis band-pass filters vibration around a resonance, computes the analytic signal $z(t)=x_b(t)+j\,\mathcal{H}\{x_b(t)\}$, takes its magnitude $e(t)=|z(t)|$, then inspects the spectrum of the centered envelope. Here $x_b(t)$ denotes the band-passed signal and $\mathcal{H}$ is the Hilbert transform. Demodulation shifts the repetition rate of impacts into a lower-frequency spectrum where BPFO/BPFI/BSF and their harmonics or modulation sidebands can be compared.

## Features

### Time domain

For samples $x_i$ with mean $\bar{x}$, RMS is $\sqrt{N^{-1}\sum_i(x_i-\bar{x})^2}$ and indicates signal energy. Kurtosis describes tail heaviness/impulsiveness; this project uses Fisher excess kurtosis, where a Gaussian reference is near zero. Skewness describes distribution asymmetry. Crest factor is $\max_i|x_i-\bar{x}|/\mathrm{RMS}$ and highlights a large peak relative to average level. Peak-to-peak is $\max(x)-\min(x)$. These statistics are complementary and sensitive to noise, window length, and outliers.

### Frequency domain

The single-sided magnitude spectrum comes from the discrete Fourier transform. Spectral centroid is $\sum_k f_k|X_k|/\sum_k|X_k|$, a magnitude-weighted center frequency. Band energy is the fraction of total spectral power within a selected frequency band. The implementation uses 0–500, 500–1500, 1500–2500, 2500–4000, and 4000–6000 Hz bands. Spectral entropy summarizes the spread of normalized power across bins. Dominant frequency is the bin with maximum magnitude.

### Envelope spectrum

Envelope RMS and centroid summarize demodulated vibration. Fault-frequency band energy sums envelope spectral power near each calculated BPFO/BPFI/BSF/FTF fundamental; harmonic energy does the same near twice the fundamental. A finite resolution/tolerance band is required because a finite record cannot represent every frequency exactly.

## References

1. McFadden, P. D., and Smith, J. D. (1984). "Model for the vibration produced by a single point defect in a rolling element bearing." *Journal of Sound and Vibration*, 96(1), 69–82.
2. Tandon, N., and Choudhury, A. (1999). "A review of vibration and acoustic measurement methods for the detection of defects in rolling element bearings." *Tribology International*, 32(8), 469–480.
3. Randall, R. B., and Antoni, J. (2011). "Rolling element bearing diagnostics: A tutorial." *Mechanical Systems and Signal Processing*, 25(2), 485–520.
4. Antoni, J. (2006). "The spectral kurtosis: a useful tool for characterising non-stationary signals." *Mechanical Systems and Signal Processing*, 20(2), 282–307.
5. SKF. *Rolling Bearings Catalogue*, product data for 6205-2RS1 deep-groove ball bearings. SKF Group.
6. ISO 15243:2017. *Rolling bearings — Damage and failures — Terms, characteristics and causes*. International Organization for Standardization.