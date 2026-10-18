"""Selection of measurement rounds by temperature."""

import numpy as np

from measurements.processing import FloatArray, validate_shape


def select_warm_rounds(readings: FloatArray, threshold: float) -> FloatArray:
    """Return independent rows whose north temperature is >= threshold."""
    validate_shape(readings)
    if not np.isfinite(readings).all():
        raise ValueError("Readings must be finite")
    if not np.isfinite(threshold):
        raise ValueError("Threshold must be finite")
    warm = readings[:, 0] >= threshold
    return readings[warm].copy()
