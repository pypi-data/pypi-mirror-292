#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_polygon(patch):
    figure = SceneMatrix(title='Random text')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_polygon(
        coordinates=[[0.15, 0.15], [0.35, 0.4], [0.2, 0.6]],
        x_scale_factor=2,
    )

    figure.show()

# -
