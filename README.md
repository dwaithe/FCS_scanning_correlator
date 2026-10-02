## FoCuS-scan

### Python scanning FCS  data visualiser. 


This is source code repository for FoCuS-scan software.

[![DOI](https://zenodo.org/badge/30016621.svg)](https://zenodo.org/badge/latestdoi/30016621)

This software is associated with the following Methods journal article:

**Optimized processing and analysis of conventional confocal microscopy generated scanning FCS data.**

Dominic Waithe, Falk Schneider, Jakub Chojnacki, Dilip Shrestha, Jorge Bernardino de la Serna, and Christian Eggeling
Corresponding author: dominic.waithe@imm.ox.ac.uk
[https://doi.org/10.1016/j.ymeth.2017.09.010](https://doi.org/10.1016/j.ymeth.2017.09.010)



This software is also associated with the Biorxiv journal article:
BIORXIV/2017/163766
Advanced processing and analysis of conventional confocal microscopy generated scanning FCS data
Dominic Waithe , Falk Schneider, Jakub Chojnacki , Dilip Shrestha, Jorge Bernardino de la Serna , and Christian Eggeling

The latest and historical releases of the software and manual for Windows are available through the following link and allows immediate access to FoCuS-scan technique: [Click for Releases](https://github.com/dwaithe/FCS_scanning_correlator/releases/)

### FoCuS-scan now continues as FoCuS-fit-JS

FoCuS-scan's scanning FCS analysis now continues in **FoCuS-fit-JS**, which runs in any web browser with nothing to install:

- **Use it online:** [https://dwaithe.github.io/FCSfitJS/](https://dwaithe.github.io/FCSfitJS/)
- **Source code:** [https://github.com/dwaithe/FCSfitJS](https://github.com/dwaithe/FCSfitJS)

Its Carpets view opens .lsm, .czi, .tif, .msr and .lif line scans, correlates them column by column, and sends the curves to the fitter, with crop, intervals and spatial binning as in FoCuS-scan. It also includes FoCuS-point's correlation of raw photon files. Its readers and correlation were tested against the results of this Python code, and it fixes the issues listed under [Known issues](#known-issues-fixed-in-focus-fit-js) below.

This repository is kept so that FoCuS-scan continues to run on current versions of Python. It has only been updated to work with newer Python and libraries; what it calculates is unchanged.

### Installation

FoCuS-scan needs Python 3.9 or newer (tested with Python 3.11 and 3.13). It uses the fitting window of [FoCuS-point](https://github.com/dwaithe/FCS_point_correlator), which is installed with the other requirements.

It is best installed in its own virtual environment, so that it does not change the packages other software relies on (FoCuS-scan needs NumPy 2, for example, which some older packages cannot use). In a terminal, from a copy of this repository:

```
python3 -m venv focus-env
source focus-env/bin/activate        # Windows: focus-env\Scripts\activate
pip install -r requirements.txt
cd focusscan
python scanningFCScorr.py
```

The next time, activate the environment again (`source focus-env/bin/activate`) and run the last two lines.

**Troubleshooting.** `ValueError: numpy.dtype size changed, may indicate binary incompatibility` means a package built for NumPy 1 (often pandas, which lmfit uses if it is present) was found alongside NumPy 2: install FoCuS-scan in a new virtual environment as above. An error that mentions `focuspoint-0.1` or `QtWebEngineWidgets` comes from an old installation of FoCuS-point in that Python; remove it with `pip uninstall focuspoint`, or use a new virtual environment.

### Updates for current Python (2026)

The code was last changed for Python 3.6-era libraries, and a number of things had stopped working. They have been fixed without changing what the software calculates; the .lsm, .tif and .czi readers return the same arrays as with the older tifffile and czifile versions.

- **matplotlib 3.5+:** the Qt4 backend was removed, so FoCuS-scan stopped at start-up with `No module named 'matplotlib.backends.backend_qt4agg'`. It now uses the Qt5 backend throughout.
- **matplotlib 3.5+:** the correlation carpets are drawn with `pcolormesh`, which now raises an error where older matplotlib silently left out the row and column beyond the grid. The carpet is trimmed in the same way before drawing, so it looks as it did. `SpanSelector`'s renamed options (`props`, `interactive`) are used for the selections.
- **lmfit 1.0+:** `report_errors` no longer exists in lmfit; the unused import was removed.
- **NumPy 1.24+:** `np.int` was removed; `int` is used instead.
- **Python 3.10+ / PyQt5:** spin boxes no longer accept decimal numbers, which stopped the crop window from opening. The values are now passed as whole numbers.
- **Python 3.13:** the .msr import window builds its list of stacks with `exec`, which could no longer see the names it had created. The `exec` calls now share one namespace, as they did before.
- **tifffile:** `tifffile.imsave` was removed; `tifffile.imwrite` is used for the TIFF exports. Newer tifffile versions also store the .lsm metadata differently, so the line frequency was no longer suggested when an .lsm file was opened; it is read from the new location again.
- **czifile:** newer czifile versions drop the axes of length one from the array they return, so .czi files no longer loaded. The full array is requested, as before.
- **Requirements:** a `requirements.txt` is included, which installs FoCuS-point as well.

### Known issues (fixed in FoCuS-fit-JS)

These were found while porting FoCuS-scan to JavaScript. They are left as they are here, so that FoCuS-scan gives the same results as it always has. FoCuS-fit-JS fixes them.

1. **The last lags of the multiple-tau correlator.** For some numbers of lines (about one line count in m; for m = 30: 240–247, 480–495, …, 61440–63487 lines), the last level of the correlator has too few points for its last lag. The autocorrelation then keeps its full length, with the last-but-one point left unnormalised (a raw sum of products, often large and of either sign) and the last point set to 0. The cross-correlation is shortened instead, so the two curves no longer have the same length and two-channel files with such line counts cannot be loaded. FoCuS-fit-JS ends both curves two lags early, as the original `multipletau` package does.
2. **Spatial binning.** Binning adds up neighbouring pixels along the line before each column is correlated. FoCuS-scan adds up one pixel too few, and not centred: with binning 3, column *i* is pixels *i*−1 and *i*, while the count rate and N&B brightness are still divided by 3 (so they come out at 2/3 of the true value; 4/5 with binning 5). Even values give empty curves (2) or repeat the next odd value. FoCuS-fit-JS adds up the pixels centred on each column and accepts odd values only.
3. **Crop.** For two-channel TIFF files the crop's line and column range is applied twice, so every interval after the first, and any column range not starting at pixel 0, comes out wrong or empty (one-channel files and the other formats are correct). For .lsm files the default column range can stop at the number of lines rather than the number of pixels. FoCuS-fit-JS crops once, for every format, with all pixels by default.

Also noted while testing, and not affecting the results: moving to the last display pane of a carpet (the next-pane button) can reach a pane that is empty or, for two-channel files, only partly filled, and an error is shown instead of the intensity carpet. Two-channel carpets shorter than one pane (about 150 lines for every 64 pixels along the line) show the same error when they are opened.
