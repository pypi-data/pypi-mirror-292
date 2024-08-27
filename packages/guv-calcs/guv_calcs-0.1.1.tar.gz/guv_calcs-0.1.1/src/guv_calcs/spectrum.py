import csv
import warnings
from importlib import resources
import numpy as np
import matplotlib.pyplot as plt
from ._helpers import load_csv, rows_to_bytes


class Spectrum:
    """
    Attributes:
        wavelengths: 1d arraylike
            wavelength values in nanometers
        intensities: 1d arraylike
            relative intensity values in arbitrary units
        weights: dict
            Dictionary containing spectral weights. Keys are labels for the weighting
            table and values are a tuple of two lists, (wavelengths, intensities).
            Generally loaded from within the package but you can pass your own if you
            really want to.
    """

    def __init__(self, wavelengths, intensities, weights=None):
        self.wavelengths = np.array(wavelengths)
        self.intensities = np.array(intensities)
        if len(self.wavelengths) != len(self.intensities):
            raise ValueError("Number of wavelengths and intensities do not match.")

        self.weights = self._load_spectral_weightings() if weights is None else weights
        self.weighted_intensities = (
            None if self.weights is None else self._weight_spectra()
        )

    @classmethod
    def from_file(cls, filepath):
        """initialize spectrum object from file"""
        csv_data = load_csv(filepath)
        reader = csv.reader(csv_data, delimiter=",")
        # read each line
        spectra = []
        for i, row in enumerate(reader):
            try:
                wavelength, intensity = map(float, row)
                spectra.append((wavelength, intensity))
            except ValueError:
                if i == 0:  # probably a header
                    continue
                else:
                    warnings.warn(f"Skipping invalid datarow: {row}")
        wavelengths = np.array(spectra).T[0]
        intensities = np.array(spectra).T[1]
        return cls(wavelengths, intensities)

    @classmethod
    def from_dict(cls, dct):
        """
        initialize spectrum object from a dictionary where
        the first key contains wavelength values, and the second
        key contains intensity values
        """
        keys = list(dct.keys())
        wavelengths = np.array(dct[keys[0]])
        intensities = np.array(dct[keys[1]])
        return cls(wavelengths, intensities)

    def to_dict(self, as_string=False):
        spec = {}
        spec["Wavelength"] = self.wavelengths
        spec["Unweighted Relative Intensity"] = self.intensities
        if self.weighted_intensities is not None:
            for key, val in self.weighted_intensities.items():
                spec[key] = val
        if as_string:
            for key, val in spec.items():
                spec[key] = ", ".join(map(str, spec[key]))
        return spec

    def to_csv(self, fname=None):
        """"""
        rows = [list(self.to_dict().keys())]
        vals = [self.wavelengths, self.intensities]
        vals += list(self.weighted_intensities.values())
        rows += list(np.array(vals).T)
        csv_bytes = rows_to_bytes(rows)
        if fname is not None:
            with open(fname, "wb") as csvfile:
                csvfile.write(csv_bytes)
        else:
            return csv_bytes

    def _load_spectral_weightings(self):
        """load spectral weightings from within package"""

        fname = "UV Spectral Weighting Curves.csv"
        path = resources.files("guv_calcs.data").joinpath(fname)
        with path.open("rb") as file:
            weights = file.read()

        csv_data = load_csv(weights)
        reader = csv.reader(csv_data, delimiter=",")
        headers = next(reader, None)  # get headers

        data = {}
        for header in headers:
            data[header] = []
        for row in reader:
            for header, value in zip(headers, row):
                data[header].append(float(value))

        spectral_weightings = {}
        for i, (key, val) in enumerate(data.items()):
            if i == 0:
                wavelengths = np.array(val)
            else:
                spectral_weightings[key] = (wavelengths, np.array(val))
        return spectral_weightings

    def _weight_spectra(self):
        """calculate the weighted spectra"""
        weighted_intensities = {}
        maxval = max(self.intensities)
        for key, val in self.weights.items():
            weight_wavelengths, weights_orig = val[0], val[1]
            # update weights to match the spectral wavelengths we've got
            weights = np.interp(self.wavelengths, weight_wavelengths, weights_orig)
            # weight spectra
            weighted_intensity = self.intensities * weights
            ratio = maxval / max(weighted_intensity)
            weighted_intensities[key] = weighted_intensity * ratio
        return weighted_intensities

    def _scale(self, value):
        """scale both the base and weighted intensities by a value"""
        self.intensities *= value
        if self.weighted_intensities is not None:
            for key, val in self.weighted_intensities.items():
                self.weighted_intensities[key] *= value

    def filter(self, minval=None, maxval=None):
        """
        filter the spectra over a wavelength range. returns a tuple of
        the (wavelength, intensity) lists
        """
        if minval is None:
            minval = min(self.wavelengths)
        if maxval is None:
            maxval = max(self.wavelengths)

        # truncate
        idx1 = np.argwhere(self.wavelengths >= minval)
        idx2 = np.argwhere(self.wavelengths <= maxval)
        idx = np.intersect1d(idx1, idx2)
        return self.wavelengths[idx], self.intensities[idx]

    def sum(self, minval=None, maxval=None):
        """sum over the spectra, optionally over a range"""
        wavelengths, intensities = self.filter(minval, maxval)
        return sum_spectrum(wavelengths, intensities)

    def scale(self, power, minval=None, maxval=None):
        """
        scale the spectra to a power value, such that the total spectral
        power is equal tothe value.
        optionally, consider only the power output over a range of wavelengths
        """
        spectral_power = self.sum(minval=minval, maxval=maxval)
        self._scale(power / spectral_power)
        return self

    def normalize(self, normval=1):
        """normalize the maximum intensity to a value"""
        self._scale(normval / max(self.intensities))
        return self

    def plot(self, title="", fig=None, figsize=(6.4, 4.8), yscale="linear"):
        """
        plot the spectra and any weighted spectra.
        `yscale` is generally either "linear" or "log", but any matplotlib scale is permitted
        """

        if fig is None:
            fig, ax = plt.subplots()
        else:
            ax = fig.axes[0]

        ax.plot(
            self.wavelengths, self.intensities, label="Unweighted Relative Intensity"
        )
        for key, val in self.weighted_intensities.items():
            ax.plot(self.wavelengths, val, label=key, alpha=0.7, linestyle="--")
        ax.legend()
        ax.grid(True, which="both", ls="--", c="gray", alpha=0.3)
        ax.set_xlabel("Wavelength [nm]")
        ax.set_ylabel("Relative intensity [%]")
        ax.set_yscale(yscale)
        ax.set_title(title)
        return fig


def sum_spectrum(wavelength, intensity):
    """
    sum across a spectrum.
    ALWAYS use this when summing across a spectra!!!
    """
    weighted_intensity = [
        intensity[i] * (wavelength[i] - wavelength[i - 1])
        for i in range(1, len(wavelength))
    ]
    return sum(weighted_intensity)
