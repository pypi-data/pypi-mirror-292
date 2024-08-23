#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_scatter(patch):
    figure = SceneMatrix(title='Random text')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_scatter(
        x=[0, 1, 2, 3],
        y=[0, 1, 2, 3],
        marker='o',
        label='test',
        color='black',
        marker_size=100,
        edge_color='red',
        line_width=3
    )

    figure.show()

# -
