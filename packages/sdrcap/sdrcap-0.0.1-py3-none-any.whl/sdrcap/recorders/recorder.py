""" Recording interface for each SDR device 
    interface regardless of filetype 
"""

from abc import ABC, abstractmethod


class Recorder(ABC):
    """Abstract class defining methods for each file logic to implement"""

    def __init__(self):
        self.start_recording_time = None
        self.stop_recording_time = None

    @abstractmethod
    def start_recording(self, start_recording_time):
        """Start the recording process."""

    @abstractmethod
    def stop_recording(self, stop_recording_time):
        """Stop the recording process."""


    @abstractmethod
    def save(self, samples, filename):
        """Saves the samples to the filename specified in append mode
           where file creation occurs in file not created yet.

        Args:
            samples (numpy.ndarray): array of In-phase and Quadrature raw values.
            filename (str): name of the file without extension to save as
        """
