import numpy as np


def calculate_snr_f_statistics(truth_f: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Calculate statistics of snr_f truth data.

    For now, includes mean and standard deviation of the raw values (usually energy)
    and mean and standard deviation of the dB values (10 * log10).
    """
    return (
        calculate_snr_mean(truth_f),
        calculate_snr_std(truth_f),
        calculate_snr_db_mean(truth_f),
        calculate_snr_db_std(truth_f),
    )


def calculate_snr_mean(truth_f: np.ndarray) -> np.ndarray:
    """Calculate mean of snr_f truth data."""
    snr_mean = np.zeros(truth_f.shape[1], dtype=np.float32)

    for c in range(truth_f.shape[1]):
        tmp_truth = truth_f[:, c]
        tmp = tmp_truth[np.isfinite(tmp_truth)].astype(np.double)

        if len(tmp) == 0:
            snr_mean[c] = -np.inf
        else:
            snr_mean[c] = np.mean(tmp)

    return snr_mean


def calculate_snr_std(truth_f: np.ndarray) -> np.ndarray:
    """Calculate standard deviation of snr_f truth data."""
    snr_std = np.zeros(truth_f.shape[1], dtype=np.float32)

    for c in range(truth_f.shape[1]):
        tmp_truth = truth_f[:, c]
        tmp = tmp_truth[np.isfinite(tmp_truth)].astype(np.double)

        if len(tmp) == 0:
            snr_std[c] = -np.inf
        else:
            snr_std[c] = np.std(tmp, ddof=1)

    return snr_std


def calculate_snr_db_mean(truth_f: np.ndarray) -> np.ndarray:
    """Calculate dB mean of snr_f truth data."""
    snr_db_mean = np.zeros(truth_f.shape[1], dtype=np.float32)

    for c in range(truth_f.shape[1]):
        tmp_truth = truth_f[:, c]
        tmp = tmp_truth[np.isfinite(tmp_truth)].astype(np.double)

        tmp2 = 10 * np.ma.log10(tmp).filled(-np.inf)
        tmp2 = tmp2[np.isfinite(tmp2)]

        if len(tmp2) == 0:
            snr_db_mean[c] = -np.inf
        else:
            snr_db_mean[c] = np.mean(tmp2)

    return snr_db_mean


def calculate_snr_db_std(truth_f: np.ndarray) -> np.ndarray:
    """Calculate dB standard deviation of snr_f truth data."""
    snr_db_std = np.zeros(truth_f.shape[1], dtype=np.float32)

    for c in range(truth_f.shape[1]):
        tmp_truth = truth_f[:, c]
        tmp = tmp_truth[np.isfinite(tmp_truth)].astype(np.double)

        tmp2 = 10 * np.ma.log10(tmp).filled(-np.inf)
        tmp2 = tmp2[np.isfinite(tmp2)]

        if len(tmp2) == 0:
            snr_db_std[c] = -np.inf
        else:
            snr_db_std[c] = np.std(tmp2, ddof=1)

    return snr_db_std


def calculate_mapped_snr_f(truth_f: np.ndarray, snr_db_mean: np.ndarray, snr_db_std: np.ndarray) -> np.ndarray:
    """Calculate mapped SNR from standard SNR energy per bin/class."""
    import scipy.special as sc

    old_err = np.seterr(divide='ignore', invalid='ignore')
    num = 10 * np.log10(np.double(truth_f)) - np.double(snr_db_mean)
    den = np.double(snr_db_std) * np.sqrt(2)
    q = num / den
    q = np.nan_to_num(q, nan=-np.inf, posinf=np.inf, neginf=-np.inf)
    mapped_snr_f = 0.5 * (1 + sc.erf(q))
    np.seterr(**old_err)

    return mapped_snr_f.astype(np.float32)
