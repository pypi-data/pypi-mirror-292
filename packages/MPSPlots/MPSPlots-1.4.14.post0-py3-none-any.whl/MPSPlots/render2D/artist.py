#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Union, Optional, List, Tuple
from dataclasses import field
from pydantic.dataclasses import dataclass as _dataclass
from pydantic import ConfigDict

# Matplotlib imports
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from matplotlib.pyplot import axis as MPLAxis
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
import matplotlib.colors as colors

# Other imports
import numpy
import shapely.geometry as geo
from itertools import cycle

from MPSPlots import colormaps

linecycler = cycle(["-", "--", "-.", ":"])


__all__ = [
    'Colorbar',
    'Contour',
    'Mesh',
    'Polygon',
    'FillLine',
    'STDLine',
    'Line',
    'VerticalLine',
    'Scatter',
    'Text',
    'AxAnnotation',
    'PatchPolygon',
    'PatchCircle',
    'PatchEllipse',

]


config_dict = ConfigDict(extra='forbid', arbitrary_types_allowed=True, strict=True)


@_dataclass(slots=True, config=config_dict)
class Colorbar():
    """
    A class to represent a colorbar for a plot.

    Attributes:
        artist (numpy.ndarray): The artist to map. Default is None.
        discreet (bool): Flag for a discreet colorbar. Buggy feature. Default is False.
        position (str): Position of the colorbar. Default is 'right'.
        colormap (str): Colormap to be used for the plot. Default is 'blue_black_red'.
        orientation (str): Orientation of the colorbar. Default is 'vertical'.
        symmetric (bool): Flag to set a symmetric colormap. Default is False.
        log_norm (bool): Flag to apply log normalization to the colorbar. Default is False.
        numeric_format (str): Format for the ticks on the colorbar. Default is None.
        n_ticks (int): Number of ticks for the colorbar. Default is None.
        label_size (int): Size of the colorbar labels. Default is None.
        width (str): Width of the colorbar. Default is '10%'.
        padding (float): Padding between the plot and the colorbar. Default is 0.10.
        norm (object): Matplotlib norm object. Default is None.
        label (str): Text label for the colorbar. Default is an empty string.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """
    artist: Optional[object] = None
    discreet: Optional[bool] = False
    position: Optional[str] = 'right'
    colormap: Optional[str | object] = field(default_factory=lambda: colormaps.blue_black_red)
    orientation: Optional[str] = "vertical"
    symmetric: Optional[bool] = False
    log_norm: Optional[bool] = False
    numeric_format: Optional[str] = None
    n_ticks: Optional[int] = None
    label_size: Optional[int] = None
    width: Optional[str] = "10%"
    padding: Optional[float] = 0.10
    norm: Optional[object] = None
    label: Optional[str] = ""

    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        self.norm = self.get_norm()

        if self.artist is None:
            self.mappable = None
        else:
            self.mappable = plt.cm.ScalarMappable(cmap=self.colormap, norm=self.norm)

            self.mappable.set_array(self.artist.scalar)

    def get_norm(self):
        if self.norm is not None:
            return self.norm

        if self.symmetric:
            return colors.CenteredNorm()

    def create_sub_ax(self, ax) -> object:
        divider = make_axes_locatable(ax.mpl_ax)

        colorbar_ax = divider.append_axes(
            self.position,
            size=self.width,
            pad=self.padding
        )

        return colorbar_ax

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if self.mappable is None:
            return None

        colorbar_ax = self.create_sub_ax(ax=ax)

        colorbar = plt.colorbar(
            mappable=self.mappable,
            norm=self.norm,
            ax=ax.mpl_ax,
            cax=colorbar_ax,
            orientation=self.orientation,
            format=self.numeric_format,
            extend='both',
            label=self.label
        )

        if self.n_ticks is not None:
            colorbar.ax.locator_params(nbins=self.n_ticks)
            colorbar.ax.tick_params(labelsize=self.label_size)


@_dataclass(slots=True, config=config_dict)
class Contour():
    """
    A class to represent a contour plot.

    Attributes:
        x (Union[List[float], List[List[float]]]): x-axis values, can be a vector or 2D grid.
        y (Union[List[float], List[List[float]]]): y-axis values, can be a vector or 2D grid.
        scalar (List[List[float]]): Scalar 2D field.
        iso_values (List[float]): Level values for plotting the iso contours.
        colormap (Optional[Union[str, object]]): Colormap to use for plotting. Default is 'blue_black_red'.
        x_scale_factor (Optional[float]): Scaling factor for the x-axis. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y-axis. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        fill_contour (Optional[bool]): Flag to fill the contour lines with color. Default is False.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    x: Union[numpy.ndarray, float]
    y: Union[numpy.ndarray, float]
    scalar: Union[numpy.ndarray, float]
    iso_values: Union[numpy.ndarray, float]
    colormap: Optional[Union[str, object]] = field(default_factory=lambda: colormaps.blue_black_red)
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    fill_contour: Optional[bool] = False
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> matplotlib.contour.ContourLabeler:
        """
        Renders the contour plot on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: Contour plot object.
        :rtype: matplotlib.contour.ContourLabeler
        """
        self.mappable = ax.mpl_ax.contour(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            levels=self.iso_values,
            colors="black",
            zorder=self.layer_position
        )

        if self.fill_contour:
            ax.mpl_ax.contourf(
                self.x * self.x_scale_factor,
                self.y * self.y_scale_factor,
                self.scalar,
                levels=self.iso_values,
                cmap=self.colormap,
                zorder=self.layer_position
            )

        return self.mappable


@_dataclass(slots=True, config=config_dict)
class Mesh():
    """
    A class to represent a mesh plot.

    Attributes:
        scalar (List[List[float]]): 2D array representing the mesh to be plotted.
        x (Optional[Union[List[float], List[List[float]]]]): Array representing the x-axis. If not defined, a numpy arange is used instead.
        y (Optional[Union[List[float], List[List[float]]]]): Array representing the y-axis. If not defined, a numpy arange is used instead.
        x_scale_factor (Optional[float]): Scaling factor for the x-axis. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y-axis. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    scalar: Union[numpy.ndarray, float]
    x: Optional[Union[numpy.ndarray, float]] = None
    y: Optional[Union[numpy.ndarray, float]] = None
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(self.scalar.shape[1])

        if self.y is None:
            self.y = numpy.arange(self.scalar.shape[0])

        self.x = numpy.asarray(self.x)
        self.y = numpy.asarray(self.y)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        self.mappable = ax.mpl_ax.pcolormesh(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            shading='auto',
            zorder=self.layer_position,
            norm=ax.colorbar.norm,
            cmap=ax.colorbar.colormap,
        )

        self.mappable.set_edgecolor('face')

        return self.mappable


@_dataclass(slots=True, config=config_dict)
class Polygon():
    """
    A class to represent a polygon plot.

    Attributes:
        instance (object): Shapely geo instance representing the polygon to be plotted.
        name (Optional[str]): Name to be added to the plot next to the polygon. Default is an empty string.
        alpha (Optional[float]): Opacity of the polygon to be plotted. Default is 0.4.
        facecolor (Optional[str]): Color for the interior of the polygon. Default is 'lightblue'.
        edgecolor (Optional[str]): Color for the border of the polygon. Default is 'black'.
        x_scale_factor (Optional[float]): Scaling factor for the x-axis. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y-axis. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    instance: object
    name: Optional[str] = ''
    alpha: Optional[float] = 0.4
    facecolor: Optional[str] = 'lightblue'
    edgecolor: Optional[str] = 'black'
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the polygon on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        if isinstance(self.instance, geo.MultiPolygon):
            for polygon in self.instance.geoms:
                self.add_polygon_to_ax(polygon, ax)
        else:
            self.add_polygon_to_ax(self.instance, ax)

    def add_polygon_to_ax(self, polygon, ax, add_name: Optional[str] = None) -> None:
        """
        Adds a polygon to the given axis.

        :param polygon: Shapely polygon instance
        :type polygon: shapely.geometry.Polygon
        :param ax: Matplotlib axis
        :type ax: MPLAxis
        :param add_name: Optional name to add next to the polygon
        :type add_name: Optional[str]

        :returns: None
        """
        collection = self.get_polygon_path(polygon)

        ax.mpl_ax.add_collection(collection, autolim=True)

        ax.mpl_ax.autoscale_view()

        if add_name:
            ax.mpl_ax.scatter(polygon.centroid.x, polygon.centroid.y)
            ax.mpl_ax.text(polygon.centroid.x, polygon.centroid.y, self.name)

    def get_polygon_path(self, polygon) -> PatchCollection:
        """
        Generates a PathCollection for the given polygon.

        :param polygon: Shapely polygon instance
        :type polygon: shapely.geometry.Polygon

        :returns: PathCollection for the polygon
        :rtype: matplotlib.collections.PatchCollection
        """
        exterior_coordinate = numpy.asarray(polygon.exterior.coords)

        exterior_coordinate[:, 0] *= self.x_scale_factor
        exterior_coordinate[:, 1] *= self.y_scale_factor

        path_exterior = Path(exterior_coordinate)

        path_interior = []
        for ring in polygon.interiors:
            interior_coordinate = numpy.asarray(ring.coords)
            path_interior.append(Path(interior_coordinate))

        path = Path.make_compound_path(
            path_exterior,
            *path_interior
        )

        patch = PathPatch(path)

        collection = PatchCollection(
            [patch],
            alpha=self.alpha,
            facecolor=self.facecolor,
            edgecolor=self.edgecolor
        )

        return collection


@_dataclass(slots=True, config=config_dict)
class FillLine():
    """
    A class to represent a filled line plot.

    Attributes:
        x (List[float]): Array representing the x-axis.
        y0 (List[float]): Array representing the inferior y-axis to be filled with color.
        y1 (List[float]): Array representing the superior y-axis to be filled with color.
        label (Optional[str]): Label for the filled area. Default is an empty string.
        color (Optional[str]): Color for the fill. Default is None.
        line_style (Optional[str]): Line style for the outline. Default is next in cycle.
        line_width (Optional[float]): Line width of the outline. Default is 1.
        show_outline (Optional[bool]): Flag to show the outline of the filling. Default is True.
        x_scale_factor (Optional[float]): Scaling factor for the x-axis. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y-axis. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    x: Union[numpy.ndarray, float]
    y0: Union[numpy.ndarray, float]
    y1: Union[numpy.ndarray, float]
    label: Optional[str] = ""
    color: Optional[str] = None
    line_style: Optional[str] = None
    line_width: Optional[float] = 1
    show_outline: Optional[bool] = True
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if self.line_style is None:
            self.line_style = next(linecycler)

        self.mappable = ax.mpl_ax.fill_between(
            self.x * self.x_scale_factor,
            self.y0 * self.y_scale_factor,
            self.y1 * self.y_scale_factor,
            color=self.color,
            linestyle=self.line_style,
            alpha=0.7,
            label=self.label,
            zorder=self.layer_position
        )

        if self.show_outline:
            ax.mpl_ax.plot(
                self.x * self.x_scale_factor,
                self.y1 * self.y_scale_factor,
                color='k',
                linestyle='-',
                linewidth=self.line_width,
                zorder=self.layer_position
            )

            ax.mpl_ax.plot(
                self.x * self.x_scale_factor,
                self.y0 * self.y_scale_factor,
                color='k',
                linestyle='-',
                linewidth=self.line_width,
                zorder=self.layer_position
            )

        return self.mappable


@_dataclass(slots=True, config=config_dict)
class STDLine():
    """
    A class to represent a line plot with standard deviation shading.

    Attributes:
        x (List[float]): Array representing the x-axis.
        y_mean (List[float]): Array representing the mean value of the y-axis.
        y_std (List[float]): Array representing the standard deviation value of the y-axis.
        label (Optional[str]): Label to be added to the plot. Default is an empty string.
        color (Optional[str]): Color for the artist to be plotted. Default is None.
        line_style (Optional[str]): Line style for the y_mean line. Default is straight lines '-'.
        line_width (Optional[float]): Line width of the artists. Default is 1.
        x_scale_factor (Optional[float]): Scaling factor for the x-axis. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y-axis. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    x: Union[numpy.ndarray, List[float]]
    y_mean: Union[numpy.ndarray, List[float]]
    y_std: Union[numpy.ndarray, List[float]]
    label: Optional[str] = ""
    color: Optional[str] = None
    line_style: Optional[str] = '-'
    line_width: Optional[float] = 1
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the line plot with standard deviation shading on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        y0 = numpy.array(self.y_mean) - numpy.array(self.y_std) / 2
        y1 = numpy.array(self.y_mean) + numpy.array(self.y_std) / 2

        line = ax.mpl_ax.plot(
            numpy.array(self.x) * self.x_scale_factor,
            numpy.array(self.y_mean) * self.y_scale_factor,
            color=self.color,
            linestyle=self.line_style,
            linewidth=self.line_width,
            zorder=self.layer_position
        )

        self.mappable = ax.mpl_ax.fill_between(
            self.x * self.x_scale_factor,
            y0 * self.y_scale_factor,
            y1 * self.y_scale_factor,
            color=line[-1].get_color(),
            linestyle='-',
            alpha=0.3,
            label=self.label,
            zorder=self.layer_position
        )

        return self.mappable


@_dataclass(slots=True, config=config_dict)
class Line():
    """
    A class to represent a line plot.

    Attributes:
        y (List[Any]): Array representing the y-axis.
        x (Optional[List[float]]): Array representing the x-axis. If not defined, a numpy arange is used instead.
        label (Optional[str]): Label to be added to the plot. Default is an empty string.
        color (Optional[str]): Color for the artist to be plotted. Default is None.
        line_style (Optional[str]): Line style for the line. Default is straight lines '-'.
        line_width (Optional[float]): Line width of the artist. Default is 1.
        x_scale_factor (Optional[float]): Scaling factor for the x-axis. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y-axis. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    y: Union[numpy.ndarray, List[float]]
    x: Optional[Union[numpy.ndarray, List[float]]] = None
    label: Optional[str] = ""
    color: Optional[str] = None
    line_style: Optional[str] = '-'
    line_width: Optional[float] = 1
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(len(self.y))

        self.y = numpy.asarray(self.y) * self.y_scale_factor
        self.x = numpy.asarray(self.x) * self.x_scale_factor

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if isinstance(self.line_style, str) and self.line_style.lower() == 'random':
            self.line_style = next(linecycler)

        if numpy.iscomplexobj(self.y):
            if ax.y_scale in ['log', 'logarithmic'] and (self.y.real.min() < 0 or self.y.imag.min() < 0):
                raise ValueError('Cannot plot negative value data on logarithmic scale!')

            ax.mpl_ax.plot(
                self.x,
                self.y.real,
                label=self.label + "[real]",
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width,
                zorder=self.layer_position
            )

            ax.mpl_ax.plot(
                self.x,
                self.y.imag,
                label=self.label + "[imag]",
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width,
                zorder=self.layer_position
            )

        else:
            x = self.x * self.x_scale_factor
            y = self.y * self.y_scale_factor

            if ax.y_scale in ['log', 'logarithmic'] and self.y.real.min() < 0:
                raise ValueError('Cannot plot negative value data on logarithmic scale!')

            self.mappable = ax.mpl_ax.plot(
                x,
                y,
                label=self.label,
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width,
                zorder=self.layer_position
            )

            return self.mappable


@_dataclass(slots=True)
class Table():
    """
    A class to represent a table plot.

    Attributes:
        table_values (List): 2D list representing the values in the table.
        column_labels (Optional[List]): List of column labels. Default is None.
        row_labels (Optional[List]): List of row labels. Default is None.
        position (Optional[str]): Position of the table. Default is 'top'.
        cell_color (Optional[str]): Color for the table cells. Default is None.
        text_position (Optional[str]): Text position within the cells. Default is 'center'.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    table_values: List
    column_labels: Optional[List] = None
    row_labels: Optional[List] = None
    position: Optional[str] = 'top'
    cell_color: Optional[str] = None
    text_position: Optional[str] = 'center'
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        self.table_values = numpy.array(self.table_values, dtype=object)
        self.table_values = numpy.atleast_2d(self.table_values)
        n_rows, n_columns = numpy.shape(self.table_values)

        if self.row_labels is None:
            self.row_labels = [''] * n_rows

        if self.column_labels is None:
            self.column_labels = [''] * n_columns

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        self.mappable = ax.mpl_ax.table(
            cellText=self.table_values,
            rowLabels=self.row_labels,
            colLabels=self.column_labels,
            loc=self.position,
            cellColours=self.cell_color,
            cellLoc=self.text_position,
        )

        return self.mappable


@_dataclass(slots=True, config=ConfigDict(extra='forbid', arbitrary_types_allowed=True))
class VerticalLine():
    """
    A class to represent vertical lines on a plot.

    Attributes:
        x (Union[List[float], List]): Array representing the x positions for the vertical lines.
        y_min (Optional[float]): Minimum y value for the vertical lines. Default is None.
        y_max (Optional[float]): Maximum y value for the vertical lines. Default is None.
        label (Optional[str]): Label to be added to the plot. Default is None.
        color (Optional[str]): Color for the lines. Default is None.
        line_style (Optional[str]): Line style for the lines. Default is straight lines '-'.
        line_width (Optional[float]): Line width of the lines. Default is 1.
        x_scale_factor (Optional[float]): Scaling factor for the x positions. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y positions. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    x: numpy.ndarray
    y_min: Optional[float] = None
    y_max: Optional[float] = None
    label: Optional[str] = None
    color: Optional[str] = None
    line_style: Optional[str] = '-'
    line_width: Optional[float] = 1
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the vertical lines on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        if isinstance(self.line_style, str) and self.line_style.lower() == 'random':
            self.line_style = next(linecycler)

        self.mappable = ax.mpl_ax.vlines(
            x=self.x * self.x_scale_factor,
            ymin=self.y_min,
            ymax=self.y_max,
            colors=self.color,
            label=self.label,
            linestyle=self.line_style,
            linewidth=self.line_width,
            zorder=self.layer_position
        )

        return self.mappable


@_dataclass(slots=True, config=ConfigDict(extra='forbid', arbitrary_types_allowed=True))
class HorizontalLine():
    """
    A class to represent horizontal lines on a plot.

    Attributes:
        y (Union[List[float], List]): Array representing the y positions for the horizontal lines.
        x_min (Optional[float]): Minimum x value for the horizontal lines. Default is None.
        x_max (Optional[float]): Maximum x value for the horizontal lines. Default is None.
        label (Optional[str]): Label to be added to the plot. Default is None.
        color (Optional[str]): Color for the lines. Default is 'black'.
        line_style (Optional[str]): Line style for the lines. Default is straight lines '-'.
        line_width (Optional[float]): Line width of the lines. Default is 1.
        x_scale_factor (Optional[float]): Scaling factor for the x positions. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y positions. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    y: numpy.ndarray
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    label: Optional[str] = None
    color: Optional[str] = 'black'
    line_style: Optional[str] = '-'
    line_width: Optional[float] = 1
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the horizontal lines on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        if isinstance(self.line_style, str) and self.line_style.lower() == 'random':
            self.line_style = next(linecycler)

        self.mappable = ax.mpl_ax.hlines(
            y=self.y * self.y_scale_factor,
            xmin=self.x_min,
            xmax=self.x_max,
            colors=self.color,
            label=self.label,
            linestyle=self.line_style,
            linewidth=self.line_width,
            zorder=self.layer_position
        )

        return self.mappable


@_dataclass(slots=True, config=ConfigDict(extra='forbid', arbitrary_types_allowed=True, strict=True))
class Scatter():
    """
    A class to represent a scatter plot.

    Attributes:
        y (List[float]): Array representing the y-axis.
        x (Optional[List[float]]): Array representing the x-axis. If not defined, a numpy arange is used instead.
        label (Optional[str]): Label to be added to the plot. Default is None.
        color (Optional[str]): Color for the points. Default is 'black'.
        marker (Optional[str]): Marker style for the points. Default is 'o'.
        marker_size (Optional[float]): Size of the markers. Default is 4.
        line_style (Optional[str]): Line style for the markers. Default is 'None'.
        line_width (Optional[float]): Line width of the markers. Default is 1.
        alpha (Optional[float]): Opacity of the points. Default is 0.7.
        edge_color (Optional[str]): Edge color for the markers. Default is 'black'.
        x_scale_factor (Optional[float]): Scaling factor for the x positions. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y positions. Default is 1.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    y: Union[numpy.ndarray, float, List[float]]
    x: Optional[Union[numpy.ndarray, float, List[float]]] = None
    label: Optional[str] = None
    color: Optional[str] = 'black'
    marker: Optional[str] = 'o'
    marker_size: Optional[float] = 4
    line_style: Optional[str] = 'None'
    line_width: Optional[float] = 1
    alpha: Optional[float] = 0.7
    edge_color: Optional[str] = 'black'
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    layer_position: Optional[int] = 1
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(len(self.y))

        self.y = numpy.asarray(self.y)
        self.x = numpy.asarray(self.x)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the scatter plot on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        self.mappable = ax.mpl_ax.scatter(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            label=self.label,
            color=self.color,
            marker=self.marker,
            s=self.marker_size,
            edgecolor=self.edge_color,
            linestyle=self.line_style,
            linewidth=self.line_width,
            alpha=self.alpha,
            zorder=self.layer_position
        )

        return self.mappable


@_dataclass(slots=True)
class Text:
    """
    A class to represent a text annotation on a plot.

    Attributes:
        text (str): String to be plotted.
        position (Optional[Tuple[float, float]]): Box position of the text. Default is (0.0, 0.0).
        font_size (Optional[int]): Font size of the text. Default is 8.
        weight (Optional[str]): Weight of the text. Default is 'normal'.
        color (Optional[str]): Color of the text. Default is 'black'.
        add_box (Optional[bool]): Boolean to enable a box around the text. Default is False.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        localisation (Optional[str]): Localisation of the text. Default is 'lower right'.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    text: str
    position: Optional[Tuple[float, float]] = (0.0, 0.0)
    font_size: Optional[int] = 8
    weight: Optional[str] = 'normal'
    color: Optional[str] = 'black'
    add_box: Optional[bool] = False
    layer_position: Optional[int] = 1
    localisation: Optional[str] = 'lower right'
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the text annotation on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        self.mappable = AnchoredText(
            self.text,
            loc=self.localisation,
            prop=dict(size=self.font_size, color=self.color, weight=self.weight, position=(0, 0)),
            frameon=self.add_box,
            bbox_to_anchor=self.position,
            bbox_transform=ax.mpl_ax.transData,  # ax.mpl_ax.transAxes,
            borderpad=0,
        )

        ax.mpl_ax.get_figure().add_artist(self.mappable)

        return self.mappable


@_dataclass(slots=True)
class WaterMark:
    """
    A class to represent a watermark on a plot.

    Attributes:
        text (str): String to be plotted.
        position (Optional[Tuple[float, float]]): Box position of the text. Default is (0.5, 0.1).
        font_size (Optional[int]): Font size of the text. Default is 30.
        weight (Optional[str]): Weight of the text. Default is 'normal'.
        color (Optional[str]): Color of the text. Default is 'black'.
        add_box (Optional[bool]): Boolean to enable a box around the text. Default is False.
        layer_position (Optional[int]): Position of the layer. Default is 1.
        localisation (Optional[str]): Localisation of the text. Default is 'lower right'.
        alpha (Optional[float]): Transparency of the text. Default is 0.2.
        rotation (Optional[float]): Rotation of the text. Default is 45.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    text: str
    position: Optional[Tuple[float, float]] = (0.5, 0.1)
    font_size: Optional[int] = 30
    weight: Optional[str] = 'normal'
    color: Optional[str] = 'black'
    add_box: Optional[bool] = False
    layer_position: Optional[int] = 1
    localisation: Optional[str] = 'lower right'
    alpha: Optional[float] = 0.2
    rotation: Optional[float] = 45
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the watermark on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        self.mappable = ax.mpl_ax.text(
            *self.position,
            self.text,
            transform=ax.mpl_ax.transAxes,
            fontsize=self.font_size,
            color=self.color,
            alpha=self.alpha,
            rotation=self.rotation,
            ha='center',
            va='baseline',
            zorder=-2
        )

        return self.mappable


@_dataclass(slots=True)
class AxAnnotation():
    """
    A class to represent an annotation on a plot axis.

    Attributes:
        text (Optional[str]): The text of the annotation. Default is an empty string.
        font_size (Optional[int]): Font size of the annotation text. Default is 18.
        font_weight (Optional[str]): Font weight of the annotation text. Default is 'bold'.
        position (Optional[Tuple[float, float]]): Position of the annotation in axis coordinates. Default is (-0.08, 1.08).
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    text: Optional[str] = ""
    font_size: Optional[int] = 18
    font_weight: Optional[str] = 'bold'
    position: Optional[Tuple[float, float]] = (-0.08, 1.08)
    mappable: object = field(init=False, repr=False)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the annotation on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        self.mappable = ax.mpl_ax.text(
            *self.position,
            self.text,
            transform=ax.mpl_ax.transAxes,
            size=self.font_size,
            weight=self.font_weight
        )

        return self.mappable


@_dataclass(slots=True)
class PatchPolygon:
    """
    A class to represent a polygon patch on a plot.

    Attributes:
        coordinates (np.ndarray): Coordinates of the vertices of the polygon.
        name (Optional[str]): Name to be added to the plot next to the polygon. Default is an empty string.
        alpha (Optional[float]): Opacity of the polygon to be plotted. Default is 0.4.
        facecolor (Optional[str]): Color for the interior of the polygon. Default is 'lightblue'.
        edgecolor (Optional[str]): Color for the border of the polygon. Default is 'black'.
        x_scale_factor (Optional[float]): Scaling factor for the x positions. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y positions. Default is 1.
        label (Optional[str]): Label to be added to the plot. Default is None.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    coordinates: List[List] = None
    name: Optional[str] = ''
    alpha: Optional[float] = 0.4
    facecolor: Optional[str] = 'lightblue'
    edgecolor: Optional[str] = 'black'
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    label: Optional[str] = None
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        self.coordinates = numpy.asarray(self.coordinates)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the polygon patch on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        if self.coordinates.size == 0:
            return

        self.coordinates[:, 0] *= self.x_scale_factor
        self.coordinates[:, 1] *= self.y_scale_factor

        self.mappable = matplotlib.patches.Polygon(
            self.coordinates,
            facecolor=self.facecolor,
            alpha=self.alpha,
            edgecolor=self.edgecolor,
            label=self.label
        )

        ax.mpl_ax.add_patch(self.mappable)

        ax.mpl_ax.autoscale_view()

        return self.mappable


@_dataclass(slots=True)
class PatchCircle():
    """
    A class to represent a circular patch on a plot.

    Attributes:
        position (Tuple[float, float]): Position of the center of the circle.
        radius (float): Radius of the circle.
        name (Optional[str]): Name to be added to the plot next to the circle. Default is an empty string.
        alpha (Optional[float]): Opacity of the circle to be plotted. Default is 0.4.
        facecolor (Optional[str]): Color for the interior of the circle. Default is 'lightblue'.
        edgecolor (Optional[str]): Color for the border of the circle. Default is 'black'.
        x_scale_factor (Optional[float]): Scaling factor for the x positions. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y positions. Default is 1.
        label (Optional[str]): Label to be added to the plot. Default is None.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    position: Tuple[float, float]
    radius: float
    name: Optional[str] = ''
    alpha: Optional[float] = 0.4
    facecolor: Optional[str] = 'lightblue'
    edgecolor: Optional[str] = 'black'
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    label: Optional[str] = None
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        self.position = numpy.asarray(self.position)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the circular patch on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        self.position[0] *= self.x_scale_factor
        self.position[1] *= self.y_scale_factor

        self.mappable = matplotlib.patches.Circle(
            self.position,
            self.radius,
            facecolor=self.facecolor,
            alpha=self.alpha,
            edgecolor=self.edgecolor,
            label=self.label
        )

        ax.mpl_ax.add_patch(self.mappable)

        ax.mpl_ax.autoscale_view()

        return self.mappable


@_dataclass(slots=True)
class PatchEllipse():
    """
    A class to represent a circular patch on a plot.

    Attributes:
        position (Tuple[float, float]): Position of the center of the circle.
        width (float):
        height (float):
        name (Optional[str]): Name to be added to the plot next to the circle. Default is an empty string.
        alpha (Optional[float]): Opacity of the circle to be plotted. Default is 0.4.
        facecolor (Optional[str]): Color for the interior of the circle. Default is 'lightblue'.
        edgecolor (Optional[str]): Color for the border of the circle. Default is 'black'.
        x_scale_factor (Optional[float]): Scaling factor for the x positions. Default is 1.
        y_scale_factor (Optional[float]): Scaling factor for the y positions. Default is 1.
        label (Optional[str]): Label to be added to the plot. Default is None.
        mappable (object): Matplotlib mappable object. Initialized in __post_init__.
    """

    position: Tuple[float, float]
    width: float
    height: float
    angle: float = 0
    name: Optional[str] = ''
    alpha: Optional[float] = 0.4
    facecolor: Optional[str] = 'lightblue'
    edgecolor: Optional[str] = 'black'
    x_scale_factor: Optional[float] = 1
    y_scale_factor: Optional[float] = 1
    label: Optional[str] = None
    mappable: object = field(init=False, repr=False)

    def __post_init__(self):
        self.position = numpy.asarray(self.position)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the circular patch on the given axis.

        :param ax: Matplotlib axis
        :type ax: MPLAxis

        :returns: None
        """
        self.position[0] *= self.x_scale_factor
        self.position[1] *= self.y_scale_factor

        self.mappable = matplotlib.patches.Ellipse(
            self.position,
            width=self.width,
            height=self.height,
            angle=self.angle,
            facecolor=self.facecolor,
            alpha=self.alpha,
            edgecolor=self.edgecolor,
            label=self.label
        )

        ax.mpl_ax.add_patch(self.mappable)

        ax.mpl_ax.autoscale_view()

        return self.mappable


# -
