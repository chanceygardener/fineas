#!/usr/bin/env python3
"""Utility functions to 
read volume from audio stream
"""

import audioop
import pyaudio
import wave
from scipy.stats import zscore
from constants import CHUNK, RECORD_SECONDS, RATE


def iter_audio_chunks(stream, window):
    """Summary
    
    Args:
        stream (TYPE): Description
        window (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    return (stream.read(CHUNK)
     for i in range(0, int(RATE / CHUNK * window)))


def get_baseline(stream, window):
	"""Summary
	
	Args:
	    stream (TYPE): Description
	    window (TYPE): Description
	
	Returns:
	    TYPE: Description
	"""
	rms_readings = []
    for chunk in iter_audio_chunks(stream, window):
    	rms = audioop.rms(chunk, 2)
    	rms_readings.append(rms)
    z = stats.zscore(rms_readings)
    # remove any "spikes" or "dips" in
    # volume, here defined as any with 
    # a z-score w/ absolute value > 2
    normed = [v for i, v in enumerate(
    	rms_readings) if -2 < z[i] < 2]
    return sum(normed) / len(normed)


def is_baseline(dat, ub=2, lb=2):
	"""Summary
	
	Args:
	    dat (TYPE): Description
	    ub (int, optional): Description
	    lb (int, optional): Description
	
	Returns:
	    TYPE: Description
	"""
	vol = NotImplemented
	within_range = lb < vol < ub
	return within_range

