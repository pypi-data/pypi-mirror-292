# Copyright (c) 2024 Bartłomiej Kizielewicz

import matplotlib.pyplot as plt


def fitness_plot(method,
                 plot_kwargs=dict(),
                 ax=None):
    """
    Plots the evolution of the global best fitness over the epochs of an optimization process.

    Parameters
    ----------
    method : object
        An object representing the optimization method, which should contain
        the attribute `history.list_global_best_fit` – a list of fitness values
        representing the best global fitness at each epoch.

    plot_kwargs : dict, optional
        A dictionary of keyword arguments passed to the `ax.plot` function
        to customize the appearance of the line plot (e.g., `color`, `linestyle`).
        Default settings include:
        - `linestyle`: '-'
        - `color`: 'tab:blue'
        - `zorder`: 1

    ax : matplotlib.axes.Axes, optional
        A Matplotlib Axes object on which to plot the graph. If not provided,
        the current active Axes (`plt.gca()`) will be used.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes object with the plot.

    Example
    -------
    >>> import matplotlib.pyplot as plt
    >>> # Assuming 'optimizer' is an object with the appropriate 'history' attribute
    >>> fig, ax = plt.subplots()
    >>> fitness_plot(optimizer, ax=ax)
    >>> plt.show()
    """

    if ax is None:
        ax = plt.gca()

    plot_kwargs = dict(
        linestyle='-',
        color='tab:blue',
        zorder=1
    ) | plot_kwargs

    ax.plot(method.history.list_global_best_fit, **plot_kwargs)
    ax.grid(True, linestyle='--', alpha=0.2, color='black')
    ax.set_axisbelow(True)
    ax.set_ylabel('Fitness')
    ax.set_xlabel('No. of epoch')

    return ax
