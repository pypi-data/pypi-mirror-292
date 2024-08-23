#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_annotation(patch):
    figure = SceneMatrix(title='Random text')

    _ = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    _ = figure.append_ax(
        row=1,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    _ = figure.append_ax(
        row=0,
        column=1,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    figure.annotate_axis()

    figure.show()


# -
