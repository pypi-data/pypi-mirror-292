"""Docstring for the waveform.py module

This module defines the Waveform class.

"""

from typing import Dict, Tuple

import numpy as np
import numpy.typing as npt

# from scipy.interpolate import InterpolatedUnivariateSpline as IUS
# from scipy.signal import savgol_filter


class Waveform:
    """
    A class to describe the waveform strain (h) in terms of complex multipoles (hlm).

    Attributes
    ----------
    times : npt.NDArray
        The time array that hlms are defined on.
    hlms : Dict[Tuple[int, int], npt.NDArray[np.complex128]]
        A dictionary of complex valued array which are the
        waveform multipole data. The keys of this dictionary are
        equal to the (l, m) multipole label.
    modes : list of Tuple[int, int] which are the keys of hlms.
        This is a list of (l, m) multipole labels that are present in the input hlms dict.
    copy_raw_data : bool
        Whether or not store a copy of the input data in memory.
        This can be used so that the state of the waveform can be reset to the input state.
    _raw_times : npt.NDArray
        If copy_raw_data is True then this is set and is just a copy of the input times.
    _raw_hlms : Dict[Tuple[int, int], npt.NDArray[np.complex128]]
        If copy_raw_data is True then this is set and is just a copy of the input hlms.


    Methods
    -------
    save_raw_data()
        Save a copy of the input times and hlms in memory.
    """

    def __init__(
        self,
        times: npt.NDArray,
        hlms: Dict[Tuple[int, int], npt.NDArray[np.complex128]],
        copy_raw_data: bool = True,
    ):
        """
        Parameters
        ----------
        times : npt.NDArray
            The time array that hlms are defined on.
        hlms : Dict[Tuple[int, int], npt.NDArray[np.complex128]]
            A dictionary of complex valued array which are the
            waveform multipole data. The keys of this dictionary are
            equal to the (l, m) multipole label.
        copy_raw_data : bool, optional
            Whether or not store a copy of the input data in memory.
            This can be used so that the state of the waveform can be reset to the input state.
            (default is True)
        """
        self.times = times
        self.hlms = hlms
        self.modes = list(self.hlms.keys())
        self.copy_raw_data = copy_raw_data

        self.save_raw_data()

    def save_raw_data(self):
        """
        save copy of times and hlms to _raw_times and _raw_hlms
        """
        if self.copy_raw_data is True:
            self._raw_times = self.times.copy()
            self._raw_hlms = self.hlms.copy()

    # def reset_times_and_hlms(self):
    #     """
    #     it is useful to have a copy of the input data
    #     for example if you accidentally mask too much of the
    #     waveform.
    #     """
    #     assert self.copy_raw_data == True, "self.copy_raw_data is False, you can't reset"
    #     self.times = self._raw_times.copy()
    #     self.hlms = self._raw_hlms.copy()
    #
    # def apply_time_shift(self, t0):
    #     """
    #     t0: time shfit
    #     applies a simple timeshift to the time array self.times + t0
    #     and returns self.
    #     """
    #     self.times += t0
    #     return self
    #
    # def apply_phase_shift(self, phi0):
    #     """
    #     phi0: orbital phase shift
    #     applies an orbital phase shift to the self.hlms modes
    #     and returns self.
    #     """
    #     hlms_new = {}
    #     for mode in self.modes:
    #         l = mode[0]
    #         m = mode[1]
    #         hlms_new[mode] = self.hlms[mode] * np.exp(1.0j * m * phi0)
    #     self.hlms = hlms_new
    #     return self
    #
    # def apply_polarisation_shift(self, psi0):
    #     """
    #     psi0: polarisation angle
    #     applies polarisation angle shift to the self.hlms modes
    #     and returns self.
    #     """
    #     hlms_new = {}
    #     for mode in self.modes:
    #         l = mode[0]
    #         m = mode[1]
    #         hlms_new[mode] = self.hlms[mode] * np.exp(1.0j * psi0)
    #     self.hlms = hlms_new
    #     return self
    #
    # def compute_amplitude(self):
    #     amplitudes = {}
    #     for mode in self.modes:
    #         amplitudes[mode] = np.abs(self.hlms[mode])
    #     self.amplitudes = amplitudes
    #     return self
    #
    # def compute_phase(self):
    #     phases = {}
    #     for mode in self.modes:
    #         phases[mode] = np.unwrap(np.angle(self.hlms[mode]))
    #     self.phases = phases
    #     return self
    #
    # def compute_frequency(self, filter_params=None):
    #     """
    #     filter_params: dict with keys: 'window_length' in terms of number of samples
    #     and 'polyorder'
    #     """
    #     # ensure phases are computed
    #     self.compute_phase()
    #     frequencies = {}
    #     for mode in self.modes:
    #         frequencies[mode] = IUS(self.times, self.phases[mode]).derivative()(self.times)
    #         if filter_params != None:
    #             frequencies[mode] = savgol_filter(
    #                 frequencies[mode], filter_params["window_length"], filter_params["polyorder"]
    #             )
    #     self.frequencies = frequencies
    #     return self
    #
    # def compute_time_of_peak(self):
    #     """
    #     computes root-sum-of-squares of mode amplitudes
    #     e.g. equation 38 in http://arxiv.org/abs/1812.07865
    #     returns both time and index of maximum
    #     """
    #     # requires the amplitudes to be calculated first
    #     assert getattr(
    #         self, "amplitudes"
    #     ), "you must calculate amplitudes first self.compute_amplitudes()"
    #     res = []
    #     for mode in self.modes:
    #         res.append(self.amplitudes[mode] ** 2)
    #     res = np.array(res)
    #     res = np.sum(res, axis=0)
    #     res = np.sqrt(res)
    #     idx_of_max = np.argmax(res)
    #     time_of_max = self.times[idx_of_max]
    #     return time_of_max, idx_of_max
    #
    # def mask(self, start_time=None, end_time=None):
    #     """
    #     returns the waveform in the domain self.times \in [start, end]
    #     specifically applies the mask to self.times and self.hlms data
    #     you must then recompute amp, phase, freq if you want.
    #
    #     start_time (float): if None then will use first time sample
    #     end_time (float): if None then will use last time sample
    #     """
    #     if start_time == None:
    #         start_time = self.times[0]
    #     if end_time == None:
    #         end_time = self.times[-1]
    #     mask = (self.times >= start_time) & (self.times <= end_time)
    #     self.times = self.times[mask]
    #     for mode in self.modes:
    #         self.hlms[mode] = self.hlms[mode][mask]
    #     return self
