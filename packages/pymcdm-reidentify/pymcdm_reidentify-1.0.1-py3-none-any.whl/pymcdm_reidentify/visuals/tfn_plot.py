# Copyright (c) 2024 Bartłomiej Kizielewicz

import matplotlib.pyplot as plt
import numpy as np


def tfn_plot(tfn,
             a,
             m,
             b,
             crit=None,
             plot_kwargs=dict(),
             text_kwargs=dict(),
             ax=None):
    """
    Plots a triangular fuzzy number (TFN) defined by the parameters `a`, `m`, and `b`.

    Parameters
    ----------
    tfn : callable
        A function that takes an input array `x` and returns the membership values
        (μ(x)) for a triangular fuzzy number.

    a : float
        The lower bound (left endpoint) of the triangular fuzzy number.

    m : float
        The peak (core) value where the membership function reaches 1.

    b : float
        The upper bound (right endpoint) of the triangular fuzzy number.

    crit : str or None, optional
        An optional label for the critical (core) value `m` to be displayed on the plot.
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
        The Axes object with the TFN plot.

    Example
    -------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from pymcdm.methods.comet import _TFN
    >>> tfn = _TFN(1, 5, 9)
    >>> a, m, b = 1, 5, 9
    >>> fig, ax = plt.subplots()
    >>> tfn_plot(tfn, a, m, b, crit='1', ax=ax)
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

    x = np.arange(a - abs(b - a) * 0.1, b + abs(b - a) * 0.1, abs(b - a) * 0.1)

    ax.plot(x, tfn(x), **plot_kwargs)
    if crit is not None:
        ax.annotate(f'$C_{crit}^{{core}}$',(m - abs(b - a) * 0.01, 1.05), **text_kwargs)
        ax.set_title(f'$C_{crit}^{{core}}={m:.2f}$')
    else:
        ax.annotate(f'$C^{{core}}$', (m - abs(b - a) * 0.01, 1.05), **text_kwargs)
        ax.set_title(f'$C^{{core}}={m:.2f}$')

    ax.grid(True, linestyle='--', alpha=0.2, color='black')
    ax.set_axisbelow(True)
    ax.set_ylim(0, 1.3)

    ax.set_ylabel('$\mu(x)$')
    ax.set_xlabel('x')

    return ax
