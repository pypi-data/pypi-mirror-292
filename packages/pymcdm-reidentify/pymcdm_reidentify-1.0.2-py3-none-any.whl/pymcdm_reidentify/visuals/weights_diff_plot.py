# Copyright (c) 2024 Bartłomiej Kizielewicz

import matplotlib.pyplot as plt
import numpy as np


def weights_diff_plot(reference,
                      obtained,
                      plot_kwargs=dict(),
                      scatter_kwargs=dict(),
                      text_kwargs=dict(),
                      fill_kwargs=dict(),
                      ax=None):
    """
    Plots the differences between reference weights and obtained weights, providing a visual comparison.

    Parameters
    ----------
    reference : np.ndarray
        An array of reference weights used as the baseline for comparison.

    obtained : np.ndarray
        An array of obtained weights that will be compared against the reference weights.

    plot_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the dashed lines connecting
        reference and obtained weights. Default settings include:
        - `linestyle`: '--'
        - `color`: 'darkblue'
        - `zorder`: 1

    scatter_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the scatter points.
        Defaultoping settings include:
        - `color`: 'black'
        - `s`: 15
        - `zorder`: 3

    text_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the weight labels.
        Default settings include:
        - `textcoords`: "offset points"
        - `xytext`: (0, 10)
        - `ha`: 'center'
        - `fontsize`: 8

    fill_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the filled area between
        the reference and obtained weights. Default settings include:
        - `color`: 'tab:green'
        - `alpha`: 0.5
        - `zorder`: 0

    ax : matplotlib.axes.Axes, optional
        A Matplotlib Axes object on which to plot the graph. If not provided,
        the current active Axes (`plt.gca()`) will be used.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes object with the weights difference plot.

    Example
    -------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> reference = np.array([0.2, 0.3, 0.5])
    >>> obtained = np.array([0.25, 0.35, 0.4])
    >>> fig, ax = plt.subplots()
    >>> weights_diff_plot(reference, obtained, ax=ax)
    >>> plt.show()
    """
    if ax is None:
        ax = plt.gca()

    scatter_kwargs = dict(
        color='black',
        zorder=3,
        s=15
    ) | scatter_kwargs

    plot_kwargs = dict(
        linestyle='--',
        zorder=1,
        color='darkblue'
    ) | plot_kwargs

    text_kwargs = dict(
        textcoords="offset points",
        xytext=(0, 10),
        ha='center',
        fontsize=8
    ) | text_kwargs

    fill_kwargs = dict(
        color='tab:green',
        alpha=0.5,
        zorder=0
    ) | fill_kwargs

    sorted_indexes = np.argsort(reference)
    sorted_reference = reference[sorted_indexes]
    sorted_obtained = obtained[sorted_indexes]

    ax.scatter(reference, obtained, **scatter_kwargs)
    ax.grid(alpha=0.5, linestyle='--')

    diff = 0
    for weight_reference, weight_obtained in zip(sorted_reference, sorted_obtained):
        midpoint = (weight_reference + weight_obtained) / 2
        ax.plot([weight_reference, midpoint], [weight_obtained, midpoint], **plot_kwargs)
        diff += np.sqrt((weight_obtained - weight_reference) ** 2 + (midpoint - midpoint) ** 2)

    weights_start = (sorted_reference[0] + sorted_obtained[0]) / 2
    weights_end = (sorted_reference[-1] + sorted_obtained[-1]) / 2
    sorted_reference = np.hstack([[weights_start], sorted_reference, [weights_end]])
    sorted_obtained = np.hstack([[weights_start], sorted_obtained, [weights_end]])

    ax.fill_between(sorted_reference, sorted_reference, sorted_obtained, **fill_kwargs)

    for i, (x, y) in enumerate(zip(reference, obtained)):
        label = f'$W_{{{i + 1}}}$'
        ax.annotate(label, (x, y), **text_kwargs)

    ax.plot([0.00, sorted_reference.max()], [0.00, sorted_obtained.max()], **plot_kwargs)

    ax.set_ylabel(f'Reference weights')
    ax.set_xlabel(f'Obtained weights')

    ax.text(0.77, 0.05, f'$\sum_{{i=1}}^n d_i$={diff:0.5f}', horizontalalignment='center', verticalalignment='bottom',
            fontsize=10, transform=ax.transAxes)

    return ax
