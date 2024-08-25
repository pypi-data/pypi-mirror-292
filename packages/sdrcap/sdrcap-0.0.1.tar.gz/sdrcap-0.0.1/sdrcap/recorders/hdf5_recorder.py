"""
Module for handling HDF5 file operations for recording SDR data.

This module provides an implementation of the `Recorder` base class specifically
for saving SDR (Software-Defined Radio) data to HDF5 files. It includes methods 
for starting and stopping recordings as well as saving recorded samples in HDF5 
format. The `HDF5Recorder` class handles file creation, appending data, and 
managing metadata related to the recording process.

Attributes:
    - center_freq (float): The center frequency used for recording.
    - sample_rate (float): The sample rate at which data is recorded.
    - freq_correction (float): Frequency correction applied to the recorded data.
    - gain (float): Gain setting used for recording.

Methods:
    - start_recording(start_recording_time): Captures the start time of the recording.
    - stop_recording(stop_recording_time): Captures the stop time of the recording.
    - save(samples, filename): Saves the recorded samples to an HDF5 file, appending 
      data to existing datasets or creating new ones as necessary.

Usage:
    This module is intended for use with SDR applications where recorded data 
    needs to be saved in the HDF5 format for further analysis or processing.
"""

import time
from datetime import datetime
import h5py
import numpy as np
from .recorder import Recorder


class HDF5Recorder(Recorder):
    """Class to record large volumes of data into hdf5 datasets with appropriate
        metadata.

    Args:
        Recorder (ABC): inherited Recording class API.
    """

    def __init__(self, center_freq, sample_rate, freq_correction, gain):
        super().__init__()
        self.start_recording_time = None
        self.stop_recording_time = None
        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.freq_correction = freq_correction
        self.gain = gain

    def start_recording(self, start_recording_time):
        """Capture the recording start time.

        Args:
            start_recording_time (float): time that the hardware interface
            started the recording.
        """
        self.start_recording_time = start_recording_time

    def stop_recording(self, stop_recording_time):
        """Capture the recording stop time.

        Args:
            stop_recording_time (float): time that the hardware interface
            stopped the recording.
        """
        self.stop_recording_time = stop_recording_time

    def save(self, samples, filename):
        """HDF5 saving implementation for file.

        Args:
            samples (numpy.ndarray): array of In-phase and Quadrature raw values.
            filename (str): name of the file without extension to save as
        """
        current_time = time.time()
        batch_timestamps = [
            datetime.utcfromtimestamp(current_time + (i / len(samples))).strftime(
                "%Y-%m-%d %H:%M:%S."
            )
            + f"{int(((current_time +
                                    (i / len(samples))) % 1) *
                                    1_000_000):06d}"
            for i in range(len(samples))
        ]
        batch_timestamps = np.array(
            batch_timestamps, dtype="S26"
        )  # Store as bytes with max length of 26

        with h5py.File(filename, "a") as f:
            group_name = "recording_data"
            if group_name not in f:
                group = f.create_group(group_name)
            else:
                group = f[group_name]

            if "real" in group:
                real_data = group["real"]
                imag_data = group["imag"]
                timestamp_data = group["timestamps"]

                if isinstance(real_data, h5py.Dataset):
                    real_data.resize((real_data.shape[0] + len(samples),))
                if isinstance(imag_data, h5py.Dataset):
                    imag_data.resize((imag_data.shape[0] + len(samples),))
                if isinstance(timestamp_data, h5py.Dataset):
                    timestamp_data.resize((timestamp_data.shape[0] + len(samples),))

                real_data[-len(samples) :] = samples.real
                imag_data[-len(samples) :] = samples.imag
                timestamp_data[-len(samples) :] = batch_timestamps

            else:
                group.create_dataset("real", data=samples.real, maxshape=(None,))
                group.create_dataset("imag", data=samples.imag, maxshape=(None,))
                group.create_dataset(
                    "timestamps", data=batch_timestamps, maxshape=(None,)
                )

            if "center_freq" not in group.attrs:
                group.attrs["center_freq"] = self.center_freq
            if "sample_rate" not in group.attrs:
                group.attrs["sample_rate"] = self.sample_rate
            if "freq_correction" not in group.attrs:
                group.attrs["freq_correction"] = self.freq_correction
            if "gain" not in group.attrs:
                group.attrs["gain"] = self.gain
