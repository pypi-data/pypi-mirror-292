#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import numpy
from MPSPlots.render3D import SceneList
import pyvista


def get_random_coordinates(n_points: int) -> numpy.ndarray:
    x = numpy.arange(n_points)
    y = numpy.arange(n_points)
    z = numpy.random.rand(n_points) * 30

    coordinates = numpy.c_[x, y, z].T

    return coordinates


def get_sphere_coordinate(n_points: int) -> numpy.ndarray:
    phi = numpy.linspace(0, 180, n_points)
    theta = numpy.linspace(0, 360, n_points)
    r = numpy.ones(theta.shape) * 100

    coordinates = pyvista.grid_from_sph_coords(
        theta,
        phi,
        r
    )

    return coordinates


@patch("pyvista.Plotter.show")
def test_unstructured(patch):
    figure = SceneList()

    ax = figure.append_ax()
    ax = figure.append_ax()

    coordinates = get_random_coordinates(100)

    ax.add_unstructured_mesh(
        coordinates=coordinates,
        scalar_coloring=coordinates[0]
    )

    ax.add_unit_sphere()

    ax.add_unit_axis()

    figure.show()


@patch("pyvista.Plotter.show")
def test_unit_sphere(patch):
    figure = SceneList()

    ax = figure.append_ax()

    ax.add_unit_sphere()

    figure.show()


@patch("pyvista.Plotter.show")
def test_unit_axis(patch):
    figure = SceneList()

    ax = figure.append_ax()

    ax.add_unit_axis()

    figure.show()


@patch("pyvista.Plotter.show")
def test_multi_axis(patch):
    figure = SceneList()

    ax = figure.append_ax()

    ax.add_unit_axis()

    ax = figure.append_ax()

    ax.add_unit_sphere()

    figure.show()


@patch("pyvista.Plotter.show")
def test_theta_vector(patch):
    figure = SceneList()

    ax = figure.append_ax()

    ax.add_unit_theta_vector()

    figure.show()


@patch("pyvista.Plotter.show")
def test_phi_vector(patch):
    figure = SceneList()

    ax = figure.append_ax()

    ax.add_unit_phi_vector()

    figure.show()


@patch("pyvista.Plotter.show")
def test_radial_vector(patch):
    figure = SceneList()

    ax = figure.append_ax()

    ax.add_unit_radial_vector()

    figure.show()


@patch("pyvista.Plotter.show")
def test_mesh(patch):
    figure = SceneList()

    ax = figure.append_ax()

    coordinates = get_sphere_coordinate(n_points=30)

    ax.add_mesh(
        x=coordinates.x,
        y=coordinates.y,
        z=coordinates.z,
        colormap='viridis',
        scalar_coloring=coordinates.z,
        style='surface',
        color='black',
        symmetric_colormap=True
    )

    figure.show()
# -
