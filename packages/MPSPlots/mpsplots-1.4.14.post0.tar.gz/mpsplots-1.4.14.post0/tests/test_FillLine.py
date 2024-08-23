#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import numpy
from MPSPlots.render2D import SceneList, SceneMatrix


@patch("matplotlib.pyplot.show")
def test_FillLine_SceneList(patch=None):
    x = numpy.arange(100)
    y0 = numpy.random.rand(100) + x
    y1 = numpy.random.rand(100)

    figure = SceneList(title='random data simple line')

    ax = figure.append_ax(x_label='x data', y_label='y data', show_legend=True)

    ax.add_fill_line(x=x, y0=y0, y1=y1)

    figure.show()


@patch("matplotlib.pyplot.show")
def test_FillLine_SceneMatrix(patch):
    x = numpy.arange(100)
    y0 = numpy.random.rand(100) + x
    y1 = numpy.random.rand(100)

    figure = SceneMatrix(title='random data simple line')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_fill_line(x=x, y0=y0, y1=y1, label='test label')

    figure.show()


# -
