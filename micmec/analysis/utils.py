#!/usr/bin/env python
# File name: utils.py
# Description: Auxiliary analysis routines.
# Author: Joachim Vandewalle
# Date: 18-11-2021

"""Auxiliary analysis routines."""


import h5py as h5


__all__ = ["get_slice", "get_time"]


def get_time(f, start, end, step):
    """
    Parameters
    ----------
    f : h5py.File object (open)
        A .h5 file, may be None if it is not available. 
    start : int, optional
        The first sample to be considered for analysis. 
        This may be negative to indicate that the analysis should start from the -start last samples.
    end : int, optional
        The last sample to be considered for analysis. 
        This may be negative to indicate that the last -end sample should not be considered.
    step : int, optional
        The spacing between the samples used for the analysis.
    
    Returns
    -------
    time, label : numpy.ndarray, str
        The sliced time axis, with appropriate units, and the label of the time axis.
    
    """
    if "trajectory/time" in f:
        label = "TIME [%s]" % log.time.notation
        time = f["trajectory/time"][start:end:step]/log.time.conversion
    else:
        label = "STEP"
        time = np.arange(len(f["trajectory/epot"][:]), dtype=float)[start:end:step]
    return time, label


def get_slice(f, start=0, end=-1, max_sample=None, step=None):
    """
    Parameters
    ----------
    f : h5py.File object (open)
        A .h5 file, may be None if it is not available. 
        If it contains a trajectory group, this group will be used to determine the number of time steps in 
        the trajectory.
    start : int, optional
        The first sample to be considered for analysis. 
        This may be negative to indicate that the analysis should start from the -start last samples.
    end : int, optional
        The last sample to be considered for analysis. 
        This may be negative to indicate that the last -end sample should not be considered.
    max_sample : int, optional
        When given, step is set such that the number of samples does not exceed max_sample.
    step : int, optional
        The spacing between the samples used for the analysis.
    
    Returns
    -------
    start, end, step : int
        When f is given, start and end are always positive.

    Notes
    -----
    The optional arguments can be given to all of the analysis routines. 
    Just make sure you never specify step and max_sample at the same time. 
    The max_sample argument assures that the step is set such that the number of samples does not exceed max_sample. 
    The max_sample option only works when f is not None, or when end is positive.
    If f is present or start and end are positive, and max_sample and step or not given, max_sample defaults to 1000.

    """
    if f is None or "trajectory" not in f:
        nrow = None
    else:
        nrow = min(ds.shape[0] for ds in f["trajectory"].values() if isinstance(ds, h5.Dataset))
        if end < 0:
            end = nrow + end + 1
        else:
            end = min(end, nrow)
        if start < 0:
            start = nrow + start + 1
    
    if start > 0 and end > 0 and step is None and max_sample is None:
        max_sample = 1000
    
    if step is None:
        if max_sample is None:
            return start, end, 1
        else:
            if end < 0:
                raise ValueError("When max_sample is given and end is negative, a file must be present.")
            step = max(1, (end - start)//max_sample + 1)
    elif max_sample is not None:
        raise ValueError("Both step and max_sample are given at the same time.")
    
    return start, end, step


