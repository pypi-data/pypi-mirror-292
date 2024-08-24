# Copyright (c) 2024 Bartłomiej Kizielewicz

import matplotlib.pyplot as plt
import numpy as np


def trfn_plot(trfn,
              a,
              b,
              c,
              d,
              crit=None,
              plot_kwargs=dict(),
              text_kwargs=dict(),
              ax=None):
    """
    Plots a trapezoidal fuzzy number (TrFN) defined by the parameters `a`, `b`, `c`, and `d`.

    Parameters
    ----------
    trfn : callable
        A function that takes an input array `x` and returns the membership values
        (μ(x)) for a trapezoidal fuzzy number.

    a : float
        The lower bound (left endpoint) where the membership function starts to rise.

    b : float
        The lower core value where the membership function reaches 1.

    c : float
        The upper core value where the membership function starts to drop from 1.

    d : float
        The upper bound (right endpoint) where the membership function drops to 0.

    crit : str or None, optional
        An optional label for the critical (core) value `((b+c)/2)` to be displayed on the plot.
        If None, the label will be `C^{core}`. If a string is provided, the label will be
        `C_{crit}^{core}`. Default is None.

    plot_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the plot line.
        Default settings include:
        - `linestyle`: '-'
        - `color`: 'black'

    text_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the text annotations
        on the plot. Default settings include:
        - `color`: 'black'

    ax : matplotlib.axes.Axes, optional
        A Matplotlib Axes object on which to plot the graph. If not provided,
        the current active Axes (`plt.gca()`) will be used.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes object with the TrFN plot.

    Example
    -------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from pymcdm_reidentify.methods.strfn import _TRFN
    >>> trfn = _TRFN(1, 3, 7, 9)
    >>> a, b, c, d = 1, 3, 7, 9
    >>> fig, ax = plt.subplots()
    >>> trfn_plot(trfn, a, b, c, d, crit='2', ax=ax)
    >>> plt.show()
    """

    if ax is None:
        ax = plt.gca()

    plot_kwargs = dict(
        linestyle='-',
        color='black'
    ) | plot_kwargs

    text_kwargs = dict(
        color='black'
    ) | text_kwargs

    x = np.arange(a - abs(d - a) * 0.1, d + abs(d - a) * 0.1, abs(d - a) * 0.1)

    ax.plot(x, trfn(x), **plot_kwargs)
    if crit is not None:
        ax.annotate(f'$C_{crit}^{{core}}$', ((b+c)/2 - abs(d - a) * 0.01, 1.05), **text_kwargs)
        ax.set_title(f'$C_{crit}^{{core}}={((b+c)/2):.2f}$')
    else:
        ax.annotate(f'$C^{{core}}$', ((b+c)/2 - abs(d - a) * 0.01, 1.05), **text_kwargs)
        ax.set_title(f'$C^{{core}}={((b+c)/2):.2f}$')

    ax.grid(True, linestyle='--', alpha=0.2, color='black')
    ax.set_axisbelow(True)
    ax.set_ylim(0, 1.3)

    ax.set_ylabel('$\mu(x)$')
    ax.set_xlabel('x')

    return ax
