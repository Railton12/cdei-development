"""
Helper functions for computing various fairness measures
"""
import numpy as np
from fairlearn.metrics import (
    demographic_parity_difference,
    demographic_parity_ratio,
)


def accuracy(labels, scores, threshold=0.5):
    """
    Computes accuracy from scores and labels. Assumes binary classification.
    """
    return ((scores >= threshold) == labels).mean()


def demographic_parity_prob(scores, attr):
    """
    Computes demographic parity on probability level.
    """
    a_mask = attr == 1
    return np.abs(scores[~a_mask].mean() - scores[a_mask].mean())


def conditional_demographic_parity_difference(labels, pred, attr, groups):
    """
    Calculate conditional demographic parity by calculating the average
    demographic parity difference across bins defined by `groups`.
    """
    diffs = []

    for group in set(groups):
        mask = groups == group

        diffs.append(
            demographic_parity_difference(
                labels[mask], pred[mask], sensitive_features=attr[mask]
            )
        )

    return np.mean(diffs)


def conditional_demographic_parity_ratio(labels, pred, attr, groups):
    """
    Calculate conditional demographic parity by calculating the average
    demographic parity ratio across bins defined by `groups`.
    """
    ratios = []

    for group in set(groups):
        mask = groups == group

        ratios.append(
            demographic_parity_ratio(
                labels[mask], pred[mask], sensitive_features=attr[mask]
            )
        )

    return np.mean(ratios)


def equal_opportunity_prob(labels, scores, attr):
    """
    Computes equal opportunity on probability level
    """
    y_mask = labels == 1
    return demographic_parity_prob(scores[y_mask], attr[y_mask])


def equalised_odds_prob(labels, scores, attr):
    """
    Computes equalised odds on probability level
    """
    a_mask = attr == 1
    y_mask = labels == 1

    eo_0 = demographic_parity_prob(scores[~y_mask], a_mask[~y_mask])
    eo_1 = demographic_parity_prob(scores[y_mask], a_mask[y_mask])
    return np.mean([eo_0, eo_1])


def calibration(labels, scores, attr, n_bins=10):
    """
    Computes calibration
    """
    a_mask = attr == 1
    y_mask = labels == 1

    # Count differences between two groups within bins
    bins = np.linspace(0, 1, n_bins + 1)

    proportions = {
        "y1_in_a0": [],
        "y1_in_a1": [],
    }

    for i in range(len(bins) - 1):
        y1_a0 = (
            (scores[~a_mask & y_mask] > bins[i])
            & (scores[~a_mask & y_mask] < bins[i + 1])
        ).sum()
        if y1_a0 > 0:
            proportions["y1_in_a0"].append(
                y1_a0
                / (
                    (scores[~a_mask] > bins[i])
                    & (scores[~a_mask] < bins[i + 1])
                ).sum()
            )
        else:
            proportions["y1_in_a0"].append(0.0)

        y1_a1 = (
            (scores[a_mask & y_mask] > bins[i])
            & (scores[a_mask & y_mask] < bins[i + 1])
        ).sum()
        if y1_a1 > 0:
            proportions["y1_in_a1"].append(
                y1_a1
                / (
                    (scores[a_mask] > bins[i]) & (scores[a_mask] < bins[i + 1])
                ).sum()
            )
        else:
            proportions["y1_in_a1"].append(0.0)
    cal_y1 = np.abs(
        np.array(proportions["y1_in_a0"]) - np.array(proportions["y1_in_a1"])
    ).sum()

    return 1.0 - cal_y1 / n_bins, proportions