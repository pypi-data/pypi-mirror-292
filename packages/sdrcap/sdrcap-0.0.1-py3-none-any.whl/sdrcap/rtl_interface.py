"""
Module for interfacing with RTL-SDR hardware and recording data.

This module provides the `RTLSDRInterface` class, which manages the interaction 
with RTL-SDR hardware using the `pyrtlsdr` library. It supports recording SDR data 
in various formats, including CSV and HDF5. The class allows for both single sample 
recording and continuous recording modes.

Attributes:
    AVAILABLE_FILETYPES (tuple): A tuple of supported file types for recording. 
    Options include "csv" and "hdf5".

Methods:
    __init__(sdr=None, center_freq=100700000.0, sample_rate=2.4e6, 
             freq_correction=60, gain="auto", record_delay=2, 
             sample_window=1024*256, filetype="csv", 
             output_dir="outputs"): Initializes the RTLSDRInterface instance with 
             specified parameters. If no SDR object is provided, it sets up a new 
             RTL-SDR device.

    _setup_rtl_sdr(): Configures and returns an RTL-SDR device instance with 
                      the specified parameters.

    record_single_sample(recording_name=None): Records a single sample of SDR data 
                                                and saves it to the specified file. 
                                                If `recording_name` is provided, 
                                                it will be included in the filename.

    record_continuous_sample(): Starts continuous recording of SDR data, saving 
                                samples periodically according to the specified 
                                record delay. Recording continues indefinitely 
                                until manually stopped.

Exceptions:
    ValueError: Raised when an invalid file type is provided during initialization.

Usage:
    This module is intended for use with RTL-SDR hardware for recording SDR data. 
    It allows users to specify recording parameters, choose between different 
    file formats, and manage both single and continuous recording sessions.

Dependencies:
    - rtlsdr: The `pyrtlsdr` library for interacting with RTL-SDR hardware.
    - sdrcap.recorders.hdf5_recorder: Provides functionality for HDF5 file operations.
    - sdrcap.recorders.csv_recorder: Provides functionality for CSV file operations.
"""

import os
import datetime
import time
from rtlsdr import RtlSdr
from sdrcap.recorders.hdf5_recorder import HDF5Recorder
from sdrcap.recorders.csv_recorder import CSVRecorder
from sdrcap import AVAILABLE_FILETYPES


class RTLSDRInterface:
    """Class for PYRTLSDR library to interface with hardware RTL SDR device."""

    def __init__(self, sdr=None, **options):
        """Initialize the RTLSDRInterface with given options.

        Args:
            sdr: Optional RTL-SDR object.
            **options: Configuration options for the RTL-SDR and recording.
        """
        defaults = {
            "center_freq": 100700000.0,
            "sample_rate": 2.4e6,  # type: ignore
            "freq_correction": 60,
            "gain": "auto",
            "record_delay": 2,
            "sample_window": 1024 * 256,
            "filetype": "csv",
            "output_dir": "outputs",
        }
        self.options = {**defaults, **options}

        self.center_freq = self.options["center_freq"]
        self.sample_rate = self.options["sample_rate"]
        self.freq_correction = self.options["freq_correction"]
        self.gain = self.options["gain"]
        self.record_delay = self.options["record_delay"]
        self.sample_window = self.options["sample_window"]
        self.filetype = self.options["filetype"]
        self.output_dir = self.options["output_dir"]

        if self.filetype not in AVAILABLE_FILETYPES:
            raise ValueError(
                f"Invalid file type: {self.filetype}."
                f"Must be one of {AVAILABLE_FILETYPES}."
            )

        if sdr is None:
            self.sdr = self._setup_rtl_sdr()
        else:
            self.sdr = sdr

        os.makedirs(self.output_dir, exist_ok=True)

        if self.filetype == "hdf5":
            self.recorder = HDF5Recorder(
                center_freq=self.center_freq,
                sample_rate=self.sample_rate,
                freq_correction=self.freq_correction,
                gain=self.gain,
            )
        elif self.filetype == "csv":
            self.recorder = CSVRecorder()
        else:
            raise ValueError(
                f"Invalid file type: {self.filetype}."
                f"Must be one of {AVAILABLE_FILETYPES}."
            )

    def _setup_rtl_sdr(self):
        """Initializes the RTL SDR with radio parameters."""
        sdr = RtlSdr()
        sdr.center_freq = self.center_freq
        sdr.freq_correction = self.freq_correction
        sdr.gain = self.gain
        return sdr

    def record_single_sample(self, recording_name=None):
        """Records a single sample, based off the SDR sample size and calls recorder.

        Args:
            recording_name (string for filename addition, optional):
              Specifies filename alongside recording information. Defaults to None.
        """
        if recording_name is not None:
            filename = (f"{self.output_dir}/{recording_name}"
            f"-sample_window{self.sample_window}.{self.filetype}")
        else:
            filename = (
                f"{self.output_dir}/sample_window{self.sample_window}.{self.filetype}"
            )
        if self.sdr is None:
            self.sdr = self._setup_rtl_sdr()
        else:
            samples = self.sdr.read_samples(self.sample_window)
            self.recorder.save(samples=samples, filename=filename)

    def start_recording_continuous_samples(self):
        """Starts a continuous, synchronous, stream of samples. Establishes recording start time."""
        start_record_time = datetime.datetime.now().timestamp()
        self.recorder.start_recording(start_record_time)
        if self.sdr is None:
            self.sdr = self._setup_rtl_sdr()
        while True:
            self.record_single_sample(recording_name=start_record_time)
            time.sleep(int(self.record_delay))
