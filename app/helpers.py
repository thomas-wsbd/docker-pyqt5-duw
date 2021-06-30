import os, pickle

import branca.colormap as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib import colors as colors
from rasterio import features


def getclasarray():
    array = np.load(os.path.join("..", "data", "clas-array.npy"))
    array[array == 0] = np.nan
    return array


def getbounds():
    with open(os.path.join("..", "data", "bounds.pickle"), "rb") as handle:
        bounds = pickle.load(handle)
    return bounds


def getcolormap():

    vmin = 1
    vmax = 7

    colormap = cm.linear.RdYlBu_11.scale(vmin, vmax)

    def reversed_colormap(existing):
        return cm.LinearColormap(
            colors=list(reversed(existing.colors)),
            vmin=existing.vmin,
            vmax=existing.vmax,
            caption="1: heel koude - tot 7: heel warme plek",
        )

    return reversed_colormap(colormap)


def mapvalue2color(value, cmap):
    """
    Map a pixel value of image to a color in the rgba format.
    As a special case, nans will be mapped totally transparent.

    Inputs
        -- value - pixel value of image, could be np.nan
        -- cmap - a linear colormap from branca.colormap.linear
    Output
        -- a color value in the rgba format (r, g, b, a)
    """
    if np.isnan(value):
        return (1, 0, 0, 0)
    else:
        return colors.to_rgba(cmap(value), 0.7)


def getpoly():
    from shapely.geometry import Polygon

    with open(os.path.join("..", "data", "temp.pickle"), "rb") as infile:
        coords = pickle.load(infile)
    return Polygon(coords)


def plotframe():
    # based on last saved geom create plotframe
    array = np.load(os.path.join("..", "data", "numpy-ndarray-l8-sd-25.npy"))
    shape = (array.shape[0], array.shape[1])  # shape row, cols
    with open(os.path.join("..", "data", "affine.pickle"), "rb") as handle:
        affine = pickle.load(handle)
    with open(os.path.join("..", "data", "index-25.pickle"), "rb") as handle:
        index = pickle.load(handle)  # contains date for each image
    poly = getpoly()
    mask = features.geometry_mask([poly], shape, affine, all_touched=True, invert=True)
    array[~mask] = float("nan")
    df = pd.DataFrame(
        np.nanmean(array, axis=(0, 1)),
        index=pd.to_datetime(list(index.values())),
        columns=["std-waarden"],
    )
    return df


def shapes():
    return [
        dict(
            type="rect",
            xref="paper",
            yref="y",
            x0=0,
            y0=y0,
            x1=1,
            y1=y1,
            fillcolor=color,
            opacity=0.3,
            layer="below",
            line_width=0,
        )
        for y0, y1, color in zip(
            [5, 2, 1, 0.5, -0.5, -1, -2],
            [2, 1, 0.5, -0.5, -1, -2, -5],
            [
                "red",
                "orange",
                "gold",
                "lightyellow",
                "lightblue",
                "blue",
                "navy",
            ],
        )
    ]
