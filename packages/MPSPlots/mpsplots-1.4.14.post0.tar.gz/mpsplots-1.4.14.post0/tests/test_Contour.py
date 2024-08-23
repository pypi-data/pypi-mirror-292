#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import numpy
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_Contour(patch):
    x, y = numpy.mgrid[-100:100, -100:100]
    scalar = numpy.sqrt(x**2 + y**2)

    figure = SceneMatrix(unit_size=(4, 4), title='random data simple line')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    iso_values = numpy.linspace(scalar.min(), scalar.max(), 10)

    ax.add_contour(
        x=x,
        y=y,
        scalar=scalar,
        iso_values=iso_values,
        fill_contour=True
    )

    figure.show()

# -
