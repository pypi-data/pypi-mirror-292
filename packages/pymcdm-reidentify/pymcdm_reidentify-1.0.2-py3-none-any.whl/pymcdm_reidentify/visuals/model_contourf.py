# Copyright (c) 2024 Bartłomiej Kizielewicz

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def model_contourf(model,
                   bounds,
                   num=10,
                   cmap='Greens',
                   colorbar=False,
                   esp=False,
                   model_kwargs=dict(),
                   contourf_kwargs=dict(),
                   scatter_kwargs=dict(),
                   text_kwargs=dict(),
                   ax=None):
    """
    Plots a contour plot for the model's preferences over a defined 𝑥-𝑦 grid.

    Parameters
    ----------
    model : callable
        A function or model that takes a 2D grid of points as input and returns
        a 1D array of preferences for each point.

    bounds : np.ndarray
        A 2x2 array defining the bounds of the x-y grid. The first row contains
        the min and max values for the x-axis, and the second row contains the
        min and max values for the y-axis.

    num : int, optional
        Number of points to generate along each axis, determining the resolution of the grid.
        Default is 10.

    cmap : str, optional
        The colormap used for the contour plot. Default is 'Greens'.

    colorbar : bool, optional
        Whether to add a colorbar to the plot. Default is False.

    esp : tuple or bool, optional
        Coordinates of a special point to be highlighted on the plot. If False, no point is plotted.
        Default is False.

    model_kwargs : dict, optional
        Additional keyword arguments to pass to the model. It must contain the keys 'weights'
        and 'types'.

    contourf_kwargs : dict, optional
        Additional keyword arguments to customize the `ax.contourf` function, which creates
        the filled contour plot.

    scatter_kwargs : dict, optional
        Additional keyword arguments to customize the appearance of the special point,
        if `esp` is provided. Default settings include:
        - `color`: 'tab:orange'
        - `marker`: '*'
        - `s`: 50
        - `zorder`: 3

    text_kwargs : dict, optional
        Additional keyword arguments to customize the annotation of the special point,
        if `esp` is provided. Default settings include:
        - `color`: 'tab:orange'
        - `fontsize`: 8
        - `zorder`: 3
        - `text`: '$ESP$'
        - `xy`: coordinates of the annotation adjusted slightly from `esp`

    ax : matplotlib.axes.Axes, optional
        A Matplotlib Axes object on which to plot the graph. If not provided,
        the current active Axes (`plt.gca()`) will be used.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The Axes object with the contour plot.

    cax : matplotlib.axes.Axes, optional
        The Axes object containing the colorbar if `colorbar=True`. Otherwise, only `ax` is returned.

    Raises
    ------
    KeyError
        If the required keys 'weights' or 'types' are missing from `model_kwargs`.

    Example
    -------
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> from pymcdm.methods import SPOTIS
    >>> bounds = np.array([[0, 1], [0, 1]])
    >>> model = SPOTIS(bounds)
    >>> model_kwargs = {'weights': np.array([0.5, 0.5]), 'types': np.array([1, -1])}
    >>> fig, ax = plt.subplots()
    >>> model_contourf(model, bounds, num=50, model_kwargs=model_kwargs, ax=ax)
    >>> plt.show()
    """
    if ax is None:
        ax = plt.gca()

    x = np.linspace(bounds[0][0], bounds[0][-1], num=num)
    y = np.linspace(bounds[1][0], bounds[1][-1], num=num)

    x, y = np.meshgrid(x, y)

    grid = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))

    required_keys = ['weights', 'types']
    for key in required_keys:
        if key not in model_kwargs:
            raise KeyError(f"Missing required key: '{key}' in model_kwargs")

    preference = model(grid, **model_kwargs).reshape(num, num)

    contourf = ax.contourf(x, y, preference, cmap=cmap, **contourf_kwargs)

    ax.set_xlabel('$C_{1}$')
    ax.set_ylabel('$C_{2}$')

    const_x = 0.02 / np.sum(bounds[0, :])
    const_y = 0.02 / np.sum(bounds[1, :])

    text_kwargs = dict(
        color='tab:orange',
        fontsize=8,
        zorder=3,
        text='$ESP$',
        xy=(esp[0] + const_x, esp[1] + const_y)
    ) | text_kwargs

    scatter_kwargs = dict(
        color='tab:orange',
        marker='*',
        s=50,
        zorder=3
    ) | scatter_kwargs

    if esp is not False:
        ax.scatter(esp[0], esp[1], **scatter_kwargs)
        ax.annotate(**text_kwargs)

    const_x_lim = 0.05 / np.sum(bounds[0, :])
    const_y_lim = 0.05 / np.sum(bounds[1, :])

    ax.set_xlim(bounds[0, 0] - const_x_lim, bounds[0, 1] + const_x_lim)
    ax.set_ylim(bounds[1, 0] - const_y_lim, bounds[1, 1] + const_y_lim)

    ax.grid(True, linestyle='--', alpha=0.2, color='black')
    ax.set_axisbelow(True)

    ax.plot([bounds[0, 0], bounds[0, 1]], [bounds[1, 0], bounds[1, 0]], linestyle='--', color='black')
    ax.plot([bounds[0, 0], bounds[0, 1]], [bounds[1, 1], bounds[1, 1]], linestyle='--', color='black')
    ax.plot([bounds[0, 0], bounds[0, 0]], [bounds[1, 0], bounds[1, 1]], linestyle='--', color='black')
    ax.plot([bounds[0, 1], bounds[0, 1]], [bounds[1, 0], bounds[1, 1]], linestyle='--', color='black')

    if colorbar:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        cbar = plt.colorbar(contourf, cax=cax)
        return ax, cax

    return ax