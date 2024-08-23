#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
from MPSPlots.render2D import SceneMatrix


@patch("matplotlib.pyplot.show")
def test_text(patch):
    figure = SceneMatrix(title='Random text')

    ax = figure.append_ax(
        row=0,
        column=0,
        x_label='x data',
        y_label='y data',
        show_legend=True
    )

    ax.add_text(
        text='this is a text',
        position=(0.5, 0.5),
    )

    figure.show()

# -
