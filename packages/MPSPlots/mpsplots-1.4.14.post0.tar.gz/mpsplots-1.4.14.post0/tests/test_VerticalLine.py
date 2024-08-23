#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import numpy
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_VerticalLine(patch):
    figure = SceneMatrix(unit_size=(4, 4), title='random data simple line')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_vertical_line(
        x=numpy.linspace(0, 10, 10),
        y_min=0,
        y_max=1,
        label='vertical line'
    )

    figure.show()


# -
