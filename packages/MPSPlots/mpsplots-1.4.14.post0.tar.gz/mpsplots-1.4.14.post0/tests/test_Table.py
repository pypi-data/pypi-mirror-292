#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_table(patch):
    figure = SceneMatrix()

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_table(
        table_values=['1', '2', '3', '4'],
    )

    figure.show()


# -
