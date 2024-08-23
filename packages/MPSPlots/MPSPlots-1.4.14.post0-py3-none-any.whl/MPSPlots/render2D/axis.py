#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from functools import wraps
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import axis as MPLAxis
from matplotlib import ticker
from MPSPlots.render2D.artist import (
    Line, FillLine, STDLine, Mesh, Scatter, Contour,
    VerticalLine, HorizontalLine, Text, PatchPolygon,
    Colorbar, AxAnnotation, Table, WaterMark, PatchCircle, PatchEllipse
)


@dataclass(slots=True)
class Axis:
    """
    Represents a plot axis with various customizable properties and artist support.

    Attributes:
        row (int): Row index of the axis in a grid.
        col (int): Column index of the axis in a grid.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        title (str): Title of the axis.
        show_grid (bool): Whether to show grid lines.
        show_legend (bool): Whether to show legend.
        legend_position (str): Position of the legend.
        x_scale (str): Scale of the x-axis.
        y_scale (str): Scale of the y-axis.
        x_limits (list): Limits for the x-axis.
        y_limits (list): Limits for the y-axis.
        equal_limits (bool): Whether to enforce equal x and y limits.
        projection (str): Projection type of the plot (e.g., 'polar').
        font_size (int): Font size for text elements.
        tick_size (int): Font size for tick labels.
        y_tick_position (str): Position of y-axis ticks ('left' or 'right').
        x_tick_position (str): Position of x-axis ticks ('top' or 'bottom').
        show_ticks (bool): Whether to show ticks.
        show_colorbar (bool): Whether to show a colorbar.
        legend_font_size (int): Font size for legend text.
        line_width (float): Line width for artists.
        line_style (str): Line style for artists.
        x_scale_factor (float): Scaling factor for the x-axis.
        y_scale_factor (float): Scaling factor for the y-axis.
        aspect_ratio (str): Aspect ratio of the axis.
        _artist_list (list): List of artists added to the axis.
        mpl_ax (MPLAxis): Matplotlib axis object.
        colorbar (Colorbar): Colorbar object for the axis.
    """
    row: int
    col: int
    x_label: str = None
    y_label: str = None
    title: str = ''
    show_grid: bool = True
    show_legend: bool = False
    legend_position: str = 'best'
    x_scale: str = 'linear'
    y_scale: str = 'linear'
    x_limits: list = None
    y_limits: list = None
    equal_limits: bool = False
    projection: str = None
    font_size: int = 16
    tick_size: int = 14
    y_tick_position: str = 'left'
    x_tick_position: str = 'bottom'
    show_ticks: bool = True
    show_colorbar: bool = None
    legend_font_size: int = 14
    line_width: float = None
    line_style: str = None
    x_scale_factor: float = None
    y_scale_factor: float = None
    aspect_ratio: str = 'auto'
    _artist_list: list = field(default_factory=list, init=False)
    mpl_ax: MPLAxis = field(default=None, init=False)
    colorbar: Colorbar = field(default_factory=Colorbar, init=False)

    def __getitem__(self, idx):
        return self._artist_list[idx]

    def __add__(self, other):
        self._artist_list += other._artist_list
        return self

    def add_artist_to_ax(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            artist = function(self, *args, **kwargs)
            self._artist_list.append(artist)
            return artist
        return wrapper

    @property
    def style(self):
        """
        Get the style attributes of the axis.

        Returns:
            dict: Dictionary of style attributes.
        """
        return {
            'x_label': self.x_label,
            'y_label': self.y_label,
            'title': self.title,
            'show_grid': self.show_grid,
            'show_legend': self.show_legend,
            'x_scale': self.x_scale,
            'y_scale': self.y_scale,
            'x_limits': self.x_limits,
            'y_limits': self.y_limits,
            'equal_limits': self.equal_limits,
            'aspect_ratio': self.aspect_ratio,
            'projection': self.projection,
            'font_size': self.font_size,
            'legend_font_size': self.legend_font_size,
            'tick_size': self.tick_size
        }

    def get_y_max(self) -> float:
        """
        Get the maximum y value among all artists in the current axis.

        Returns:
            float: The maximum y value.
        """
        y_max = -np.inf
        for artist in self._artist_list:
            if hasattr(artist, 'y'):
                artist_y_max = np.max(artist.y)
                y_max = max(y_max, artist_y_max)
        return y_max

    def get_y_min(self) -> float:
        """
        Get the minimum y value among all artists in the current axis.

        Returns:
            float: The minimum y value.
        """
        y_min = np.inf
        for artist in self._artist_list:
            if hasattr(artist, 'y'):
                artist_y_min = np.min(artist.y)
                y_min = min(y_min, artist_y_min)
        return y_min

    def get_x_max(self) -> float:
        """
        Get the maximum x value among all artists in the current axis.

        Returns:
            float: The maximum x value.
        """
        x_max = -np.inf
        for artist in self._artist_list:
            if hasattr(artist, 'x'):
                artist_x_max = np.max(artist.x)
                x_max = max(x_max, artist_x_max)
        return x_max

    def get_x_min(self) -> float:
        """
        Get the minimum x value among all artists in the current axis.

        Returns:
            float: The minimum x value.
        """
        x_min = np.inf
        for artist in self._artist_list:
            if hasattr(artist, 'x'):
                artist_x_min = np.min(artist.x)
                x_min = min(x_min, artist_x_min)
        return x_min

    def copy_style(self, other) -> None:
        """
        Copy the style from another Axis object.

        Args:
            other (Axis): The Axis object to copy the style from.
        """
        assert isinstance(other, Axis), f"Cannot copy style from different class {other.__class__}"
        for element, value in other.style.items():
            setattr(self, element, value)

    def add_artist(self, *artists) -> None:
        """
        Add one or more artists to the axis.

        Args:
            artists (Artist): The artists to add.
        """
        self._artist_list.extend(artists)

    def set_style(self, **style_dict):
        """
        Set multiple style attributes for the axis.

        Args:
            style_dict (dict): Dictionary of style attributes to set.

        Returns:
            Axis: The updated Axis object.
        """
        for element, value in style_dict.items():
            setattr(self, element, value)
        return self

    def set_ax_limits(self) -> None:
        """
        Set the limits of the axis.
        """
        self.mpl_ax.set_xlim(self.x_limits)
        self.mpl_ax.set_ylim(self.y_limits)

        if self.equal_limits:
            xy_limits = [*self.mpl_ax.get_xlim(), *self.mpl_ax.get_ylim()]
            min_xy_limit = np.min(xy_limits)
            max_xy_limit = np.max(xy_limits)
            self.mpl_ax.set_xlim([min_xy_limit, max_xy_limit])
            self.mpl_ax.set_ylim([min_xy_limit, max_xy_limit])

        ticker.ScalarFormatter(useOffset=False)

    def set_artist_parameter_value(self, parameter_str: str, value) -> None:
        """
        Set a parameter value for all artists in the axis.

        Args:
            parameter_str (str): The parameter name.
            value: The value to set.
        """
        if value is None:
            return

        for artist in self._artist_list:
            if hasattr(artist, parameter_str):
                setattr(artist, parameter_str, value)

    def scale_artist_x_axis(self, scale_factor: float) -> None:
        """
        Scale the x-axis of all artists by the given factor.

        Args:
            scale_factor (float): The scale factor.
        """
        self.set_artist_parameter_value('x_scale_factor', scale_factor)

    def scale_artist_y_axis(self, scale_factor: float) -> None:
        """
        Scale the y-axis of all artists by the given factor.

        Args:
            scale_factor (float): The scale factor.
        """
        self.set_artist_parameter_value('y_scale_factor', scale_factor)

    def set_artist_line_width(self, line_width: float) -> None:
        """
        Set the line width for all artists.

        Args:
            line_width (float): The line width.
        """
        self.set_artist_parameter_value('line_width', line_width)

    def set_artist_line_style(self, line_style: str) -> None:
        """
        Set the line style for all artists.

        Args:
            line_style (str): The line style.
        """
        self.set_artist_parameter_value('line_style', line_style)

    def render_artists(self) -> None:
        """
        Render all artists in the axis.
        """
        for artist in self._artist_list:
            artist._render_(self)

    def _render_(self) -> None:
        """
        Render the axis with its artists and decorations.
        """
        self.scale_artist_x_axis(self.x_scale_factor)
        self.scale_artist_y_axis(self.y_scale_factor)
        self.set_artist_line_width(self.line_width)
        self.set_artist_line_style(self.line_style)
        self.render_artists()
        self.decorate_axis()

        if self.show_colorbar:
            self.colorbar._render_(ax=self)

        self.set_ax_limits()

    def generate_legend(self) -> None:
        """
        Generate the legend for the axis.
        """
        if self.show_legend:
            handles, labels = self.mpl_ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            self.mpl_ax.legend(
                by_label.values(),
                by_label.keys(),
                edgecolor='k',
                facecolor='white',
                fancybox=True,
                fontsize=self.legend_font_size - 4,
                loc=self.legend_position,
            )

    def set_x_ticks_position(self, position: str) -> None:
        """
        Set the x-axis tick position.

        Args:
            position (str): The tick position ('top' or 'bottom').
        """
        position = position.lower()
        mpl_ticks = self.mpl_ax.xaxis
        mpl_ticks.set_label_position(position)
        tick_position_function = getattr(mpl_ticks, f"tick_{position}")
        tick_position_function()
        mpl_ticks.set_visible(self.show_ticks)
        self.x_tick_position = position

    def set_y_ticks_position(self, position: str) -> None:
        """
        Set the y-axis tick position.

        Args:
            position (str): The tick position ('left' or 'right').
        """
        position = position.lower()
        mpl_ticks = self.mpl_ax.yaxis
        mpl_ticks.set_label_position(position)
        tick_position_function = getattr(mpl_ticks, f"tick_{position}")
        tick_position_function()
        mpl_ticks.set_visible(self.show_ticks)
        self.y_tick_position = position

    def set_title(self, title: str, font_size: int = None) -> None:
        """
        Set the title of the axis.

        Args:
            title (str): The title text.
            font_size (int, optional): The font size for the title.
        """
        font_size = self.font_size if font_size is None else font_size
        self.title = title
        self.mpl_ax.set_title(self.title, fontsize=font_size)

    def set_tick_size(self, tick_size: int = None) -> None:
        """
        Set the tick label size.

        Args:
            tick_size (int, optional): The font size for the ticks.
        """
        tick_size = self.tick_size if tick_size is None else tick_size
        self.mpl_ax.tick_params(labelsize=tick_size)

    def set_aspect(self, aspect: str = None) -> None:
        """
        Set the aspect ratio for the plot.

        Args:
            aspect (str, optional): The aspect ratio.
        """
        aspect_ratio = self.aspect_ratio if aspect is None else aspect
        self.mpl_ax.set_aspect(aspect_ratio)

    def set_show_grid(self, show_grid: bool = None) -> None:
        """
        Set whether to show the grid.

        Args:
            show_grid (bool, optional): Whether to show the grid.
        """
        show_grid = self.show_grid if show_grid is None else show_grid
        self.mpl_ax.grid(show_grid)
        self.show_grid = show_grid

    def set_x_label(self, label: str, font_size: int = None) -> None:
        """
        Set the x-axis label.

        Args:
            label (str): The label text.
            font_size (int, optional): The font size for the label.
        """
        font_size = self.font_size if font_size is None else font_size
        self.mpl_ax.set_xlabel(label, fontsize=font_size)

    def set_y_label(self, label: str, font_size: int = None) -> None:
        """
        Set the y-axis label.

        Args:
            label (str): The label text.
            font_size (int, optional): The font size for the label.
        """
        font_size = self.font_size if font_size is None else font_size
        self.mpl_ax.set_ylabel(label, fontsize=font_size)

    def set_y_scale(self, scale: str = None) -> None:
        """
        Set the y-axis scale.

        Args:
            scale (str, optional): The scale type.
        """
        scale = self.y_scale if scale is None else scale
        self.mpl_ax.set_yscale(scale)

    def set_x_scale(self, scale: str = None) -> None:
        """
        Set the x-axis scale.

        Args:
            scale (str, optional): The scale type.
        """
        scale = self.x_scale if scale is None else scale
        self.mpl_ax.set_xscale(scale)

    def decorate_axis(self) -> None:
        """
        Add decorations to the axis (labels, title, grid, etc.).
        """
        self.generate_legend()
        self.set_x_label(self.x_label)
        self.set_y_label(self.y_label)
        self.set_x_ticks_position(position=self.x_tick_position)
        self.set_y_ticks_position(position=self.y_tick_position)
        self.set_title(title=self.title)
        self.set_x_scale()
        self.set_y_scale()
        self.set_tick_size()
        self.set_aspect()
        self.set_show_grid()

    @add_artist_to_ax
    def add_fill_line(self, **kwargs: dict) -> FillLine:
        """
        Add a FillLine artist to the axis.

        Args:
            kwargs (dict): Arguments for the FillLine artist.

        Returns:
            FillLine: The added FillLine artist.
        """
        return FillLine(**kwargs)

    @add_artist_to_ax
    def add_std_line(self, **kwargs: dict) -> STDLine:
        """
        Add a STDLine artist to the axis.

        Args:
            kwargs (dict): Arguments for the STDLine artist.

        Returns:
            STDLine: The added STDLine artist.
        """
        return STDLine(**kwargs)

    @add_artist_to_ax
    def add_scatter(self, **kwargs: dict) -> Scatter:
        """
        Add a Scatter artist to the axis.

        Args:
            kwargs (dict): Arguments for the Scatter artist.

        Returns:
            Scatter: The added Scatter artist.
        """
        return Scatter(**kwargs)

    def add_table(self, **kwargs: dict) -> Table:
        """
        Add a Table artist to the axis.

        Args:
            kwargs (dict): Arguments for the Table artist.

        Returns:
            Table: The added Table artist.
        """
        return Table(**kwargs)

    @add_artist_to_ax
    def add_mesh(self, **kwargs: dict) -> Mesh:
        """
        Add a Mesh artist to the axis.

        Args:
            kwargs (dict): Arguments for the Mesh artist.

        Returns:
            Mesh: The added Mesh artist.
        """
        return Mesh(**kwargs)

    @add_artist_to_ax
    def add_contour(self, **kwargs: dict) -> Contour:
        """
        Add a Contour artist to the axis.

        Args:
            kwargs (dict): Arguments for the Contour artist.

        Returns:
            Contour: The added Contour artist.
        """
        return Contour(**kwargs)

    @add_artist_to_ax
    def add_line(self, **kwargs: dict) -> Line:
        """
        Add a Line artist to the axis.

        Args:
            kwargs (dict): Arguments for the Line artist.

        Returns:
            Line: The added Line artist.
        """
        return Line(**kwargs)

    @add_artist_to_ax
    def add_vertical_line(self, **kwargs: dict) -> VerticalLine:
        """
        Add a VerticalLine artist to the axis.

        Args:
            kwargs (dict): Arguments for the VerticalLine artist.

        Returns:
            VerticalLine: The added VerticalLine artist.
        """
        return VerticalLine(**kwargs)

    @add_artist_to_ax
    def add_horizontal_line(self, **kwargs: dict) -> HorizontalLine:
        """
        Add a HorizontalLine artist to the axis.

        Args:
            kwargs (dict): Arguments for the HorizontalLine artist.

        Returns:
            HorizontalLine: The added HorizontalLine artist.
        """
        return HorizontalLine(**kwargs)

    @add_artist_to_ax
    def add_text(self, **kwargs: dict) -> Text:
        """
        Add a Text artist to the axis.

        Args:
            kwargs (dict): Arguments for the Text artist.

        Returns:
            Text: The added Text artist.
        """
        return Text(**kwargs)

    @add_artist_to_ax
    def add_watermark(self, **kwargs: dict) -> WaterMark:
        """
        Add a WaterMark artist to the axis.

        Args:
            kwargs (dict): Arguments for the WaterMark artist.

        Returns:
            WaterMark: The added WaterMark artist.
        """
        return WaterMark(**kwargs)

    @add_artist_to_ax
    def add_polygon(self, **kwargs: dict) -> PatchPolygon:
        """
        Add a PatchPolygon artist to the axis.

        Args:
            kwargs (dict): Arguments for the PatchPolygon artist.

        Returns:
            PatchPolygon: The added PatchPolygon artist.
        """
        return PatchPolygon(**kwargs)

    @add_artist_to_ax
    def add_ellipse(self, **kwargs: dict) -> PatchEllipse:
        """
        Add a PatchEllipse artist to the axis.

        Args:
            kwargs (dict): Arguments for the PatchEllipse artist.

        Returns:
            PatchEllipse: The added PatchEllipse artist.
        """
        return PatchEllipse(**kwargs)

    @add_artist_to_ax
    def add_circle(self, **kwargs: dict) -> PatchCircle:
        """
        Add a PatchCircle artist to the axis.

        Args:
            kwargs (dict): Arguments for the PatchCircle artist.

        Returns:
            PatchCircle: The added PatchCircle artist.
        """
        return PatchCircle(**kwargs)

    def add_colorbar(self, **kwargs: dict) -> Colorbar:
        """
        Add a Colorbar artist to the axis.

        Args:
            kwargs (dict): Arguments for the Colorbar artist.

        Returns:
            Colorbar: The added Colorbar artist.
        """
        self.colorbar = Colorbar(**kwargs)
        self.show_colorbar = True
        return self.colorbar

    @add_artist_to_ax
    def add_ax_annotation(self, text: str, **kwargs: dict) -> AxAnnotation:
        """
        Add an AxAnnotation artist to the axis.

        Args:
            text (str): The annotation text.
            kwargs (dict): Arguments for the AxAnnotation artist.

        Returns:
            AxAnnotation: The added AxAnnotation artist.
        """
        return AxAnnotation(text, **kwargs)


def Multipage(filename, figs=None, dpi=200):
    """
    Save multiple figures to a single PDF file.

    Args:
        filename (str): The name of the PDF file.
        figs (list, optional): List of figures to save.
        dpi (int, optional): The resolution in dots per inch.
    """
    pp = PdfPages(filename)
    for fig in figs:
        fig._mpl_figure.savefig(pp, format='pdf', dpi=dpi)
    pp.close()
