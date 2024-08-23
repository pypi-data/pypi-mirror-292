#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import numpy
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_Mesh(patch):
    x, y = numpy.mgrid[-100:100, -100:100]
    scalar = x**2

    figure = SceneMatrix(title='random data simple line')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_mesh(x=x, y=y, scalar=scalar)

    figure.show()

# -
