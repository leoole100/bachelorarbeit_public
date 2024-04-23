"""
common plotting helpers
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker
import colorcet as cc
from .utils import nm_to_ev, ev_to_nm
import numpy as np

def hide_inner_label():
    """
    hides axis labels and ticks in inner axes of subplots
    """
    for ax in plt.gcf().axes:
        try: ax.label_outer()
        except: pass

def energy_ticks(ax = None, locator=True, n_ticks=5):
    """
    Add energy axis ticks to the top of the plot.   
    Assumes that the x-axis is wavelength in nm.   
    To add a label use `energy_ticks(ax).set_xlabel('Energy (eV)')`
    """
    if ax is None:  ax = plt.gca()
    ax.xaxis.set_ticks_position('bottom')

    secax = ax.secondary_xaxis('top', functions=(nm_to_ev, ev_to_nm))
    
    # fix overlapping tick labels
    if locator: 
        secax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=n_ticks, prune='both'))
    return secax




"""
# Stack sub plot layout

after creating everything the figure has to be recalculated.
```python
plt.tight_layout()
plt.subplots_adjust(hspace=0)
```
"""

def stack(n, figsize=None, **kwargs):
    """
    configures ax as plot stack
    """
    fig, ax = plt.subplots(n, 1, sharex=True, figsize=figsize, **kwargs)
    for a in ax[:-1]:
        a.tick_params(labelbottom=False)

    for a in ax:
        a.ticklabel_format(axis="y", style="plain")

    return fig, ax        
  

def rows(df, x, y, name=None, ax=None, **kwargs):
    """
    Plot rows of a dataframe on a stack.

    Parameters
    ----------
    ax : iterable of matplotlib.axes.Axes
        Axes to plot on.
        Creates axes if None.
    df : pandas.DataFrame
    x : str
        Name of column to plot on x-axis.
    y : str
        Name of column to plot on y-axis.
    name: str, optional
        Name of column of additional label.
    """

    if ax == None:
        fig, ax = stack(len(df), **kwargs)
    else:
        fig = plt.gcf()

    for a, (i, row) in zip(ax, df.iterrows()):
        a.plot(row[x], row[y], label=i)
        a.set_ylabel(i)
        if name is not None:
            a.text(0.01, .9, row[name], transform=a.transAxes,
                fontsize=5,
                ha="left", va="top",
            )
    
    return fig, ax

def footnote(ax, notes):
    """
    Adds a footnote to a set of axes
    """
    for a, n in zip(ax, notes):
        a.text(0.01, .9, n, transform=a.transAxes,
            fontsize=5,
            ha="left", va="top",
        )
        a.ticklabel_format(axis="y", style="plain")
        
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)


def spectrum(row, ax=None, normalize=False, **kwargs): 
    """
    plot a pd.Series as a spectrum
    """
    if ax is None:
        ax = plt.gca()
    
    wavelength = row.wavelength.copy()
    intenstiy = row.intensity.copy()

    if normalize: 
        intenstiy /= intenstiy.max()

    ax.plot(wavelength, intenstiy, label=row["name"], **kwargs)

def finish_stack(ax=None):
    """
    finish stack plot
    """
    if ax is None:
        ax = plt.gca()

    for a in ax[:-1]:
        a.tick_params(labelbottom=False)
    
    for a in ax:
        a.ticklabel_format(axis="y", style="plain")
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)


"""
# add Colorbar
"""

def cbar_polar(ax, cmap, xticks=[], xlim=(0, 180), clim=None):
    """
    ax needs to be a polar plot

    ```python
    ax = plt.gca().inset_axes(
        [0.8, 0.01, 0.2, 0.2],
        polar=True
    )
    cbar_polar(ax, cm["CET_C6s"])
    ```
    """
    assert isinstance(ax, plt.PolarAxes), "The axis is not polar."

    if clim is None: 
        clim = xlim

    angles = np.arange(0, 180.1, 1)
    r = np.linspace(.5, 1, 10)
    values = angles * np.ones((len(r), len(angles)))
    ax.pcolormesh(
        angles*np.pi/180.0, r, values, 
        cmap=cmap,
        vmin = clim[0],
        vmax = clim[1]
    )
    ax.set_yticks([])
    ax.set_xticks(xticks)
    ax.set_rlim(None,1)
    ax.grid(None)
    ax.set_xlim(xlim[0], xlim[1]*np.pi/180)

def inset_cbar_polar(cmap, ax = None, position = [0.8, 0.01, 0.2, 0.2], xlim=(0, 180), clim=None):
    """
    ```python
    img = plt.imshow(np.random.rand(10,10))
    inset_cbar_polar(img.cmap)
    """
    if ax is None:  ax = plt.gca()

    ax_child = ax.inset_axes(
        position,
        polar=True
    )
    cbar_polar(ax_child, cmap, xlim=xlim, clim=clim)
    return ax_child
