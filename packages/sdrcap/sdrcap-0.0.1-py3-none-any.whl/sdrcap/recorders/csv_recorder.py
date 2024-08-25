"""
Module for handling CSV file operations for recording SDR data.

This module provides an implementation of the `Recorder` base class specifically
for saving SDR (Software-Defined Radio) data to CSV files. It includes methods 
for starting and stopping recordings as well as saving recorded samples in CSV 
format. The `CSVRecorder` class handles file creation, appending data, and 
formatting data appropriately for CSV storage.

Attributes:
    - None: The class does not have additional attributes specific to CSV recording.

Methods:
    - start_recording(start_recording_time): Captures the start time of the recording.
    - stop_recording(stop_recording_time): Captures the stop time of the recording.
    - save(samples, filename): Saves the recorded samples to a CSV file, appending 
      data to the file. The CSV file will contain columns for real and imaginary 
      values along with timestamps.

Usage:
    This module is intended for use with SDR applications where recorded data 
    needs to be saved in the CSV format for easy inspection and processing using 
    tools that handle CSV files.
"""

import time
from datetime import datetime
from .recorder import Recorder


class CSVRecorder(Recorder):
    """Class to record cleartext amount of data into CSV files without
        metadata.

    Args:
        Recorder (ABC): inherited Recording class API.
    """

    def __init__(self):
        """
        Initialize the CSVRecorder.
        """
        super().__init__()
        self.start_recording_time = None
        self.stop_recording_time = None

    def start_recording(self, start_recording_time):
        """Capture the recording stop time.

        Args:
            stop_recording_time (float): time that the hardware interface
            stopped the recording.
        """
        self.start_recording_time = start_recording_time

    def stop_recording(self, stop_recording_time):
        """Capture the recording start time.

        Args:
            start_recording_time (float): time that the hardware interface
            started the recording.
        """
        self.stop_recording_time = stop_recording_time

    def save(self, samples, filename):
        """CSV saving implementation for file.

        Args:
            samples (numpy.ndarray): array of In-phase and Quadrature raw values.
            filename (str): name of the file without extension to save as
        """
        batch_start_time = time.time()
        with open(filename, "a", encoding="utf-8") as out_file:
            out_file.write("Real Value,Imaginary Value,TimeStamp\n")
            for _, sample in enumerate(samples):
                current_time = time.time()
                timestamp_seconds = current_time - batch_start_time
                timestamp = datetime.utcfromtimestamp(current_time).strftime(
                    "%Y-%m-%d %H:%M:%S."
                )
                timestamp += f"{int((timestamp_seconds % 1) * 1_000_000):06d}"
                out_file.write(f"{sample.real},{sample.imag},{timestamp}\n")
