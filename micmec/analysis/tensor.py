#!/usr/bin/env python

#   MicMec 1.0, the first implementation of the micromechanical model, ever.
#               Copyright (C) 2022  Joachim Vandewalle
#                    joachim.vandewalle@hotmail.be
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#                  (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#              GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see https://www.gnu.org/licenses/.


"""Auxiliary routines for tensors."""

import numpy as np

from molmod.units import *
from molmod.constants import *

__all__ = [
    "pretty_3x3x3x3_tensor", 
    "pretty_6x6_matrix", 
    "voigt",
    "voigt_inv", 
    "plot_directional_young_modulus"
]

# The following routines improve the layout of tensors or matrices printed in a console.

def pretty_3x3x3x3_tensor(C):
    """Improve the formatting of a (3 x 3 x 3 x 3) tensor.

    Parameters
    ----------
    C : numpy.ndarray, shape=(3, 3, 3, 3)
        A (3 x 3 x 3 x 3) tensor.

    Returns
    -------
    C_print_new : str
        A nicely formatted string version of the (3 x 3 x 3 x 3) tensor.
    """
    C_print = str(C)
    C_print_new = ""
    C_print_lst = C_print.split("\n")
    C_print_lst_new = [c for c in C_print_lst if c != ""]
    for i, c in enumerate(C_print_lst_new):
        C_print_new += c
        if (i+1)%3 == 0 and i != 0:
            C_print_new += "\n"
        else:
            pass
    return C_print_new


def pretty_6x6_matrix(C):
    """Improve the formatting of a (6 x 6) matrix.

    Parameters
    ----------
    C : numpy.ndarray, shape=(6, 6)
        A (6 x 6) matrix.

    Returns
    -------
    C_print_new : str
        A nicely formatted string version of the (6 x 6) tensor.
    """
    C_print = str(C)
    C_print_new = ""
    C_print_lst = C_print.split("\n")
    C_print_lst_new = [c for c in C_print_lst if c != ""]
    for i, c in enumerate(C_print_lst_new):
        C_print_new += c
        if c[-1] == "]": 
            C_print_new += "\n"
        else: 
            pass
    return C_print_new


V = {
    0: (0,0),
    1: (1,1), 
    2: (2,2), 
    3: (1,2),
    4: (0,2),
    5: (0,1)
}


def voigt(tensor, mode=None):
    """Map a (3 x 3 x 3 x 3) tensor to a (6 x 6) Voigt notation matrix.
    
    Parameters
    ----------
    tensor : numpy.ndarray, shape=(3, 3, 3, 3)
        The tensor to be mapped to a Voigt notation matrix.
    mode : {"compliance", "elasticity"}, optional
        Declare whether the input tensor is a compliance tensor or an elasticity tensor.

    Returns
    -------
    matrix : numpy.ndarray, shape=(6, 6)
        The resulting Voigt notation matrix.

    Notes
    -----
    Voigt notation differs depending on whether the tensor is a compliance tensor or an elasticity tensor,
    hence the (optional) keyword ``mode``.
    """
    matrix = np.zeros((6,6))
    if (mode is None) or (mode == "compliance"):
        for index, _ in np.ndenumerate(matrix):
            matrix[index] = tensor[V[index[0]] + V[index[1]]]
            if index[0] >= 3:
                matrix[index] *= 2.0
            if index[1] >= 3:
                matrix[index] *= 2.0
    elif (mode == "elasticity"):
        for index, _ in np.ndenumerate(matrix):
            matrix[index] = tensor[V[index[0]] + V[index[1]]]
    else:
        raise IOError("Method `voigt_inv` did not receive valid input for keyword `mode`.") 
    return matrix


def voigt_inv(matrix, mode=None):
    """Map a (6 x 6) Voigt notation matrix to a (3 x 3 x 3 x 3) tensor.
    
    Parameters
    ----------
    matrix : numpy.ndarray, shape=(6, 6)
        The Voigt notation matrix to be mapped to a tensor.
    mode : {"compliance", "elasticity"}, optional
        Declare whether the input matrix is a compliance matrix or an elasticity matrix.

    Returns
    -------
    tensor : numpy.ndarray, shape=(3, 3, 3, 3)
        The resulting tensor.

    Notes
    -----
    Voigt notation differs depending on whether the tensor is a compliance tensor or an elasticity tensor,
    hence the (optional) keyword ``mode``.   
    """
    tensor = np.zeros((3,3,3,3))
    if (mode is None) or (mode == "compliance"):
        for index, _ in np.ndenumerate(tensor):
            ij = tuple(sorted(index[0:2]))
            kl = tuple(sorted(index[2:4]))
            for key in V.keys():
                if V[key] == ij:
                    V_ij = key
                if V[key] == kl:
                    V_kl = key
            tensor[index] = matrix[(V_ij, V_kl)]
            if V_ij >= 3:
                tensor[index] *= 0.5
            if V_kl >= 3:
                tensor[index] *= 0.5
    elif (mode == "elasticity"):
        for index, _ in np.ndenumerate(tensor):
            ij = tuple(sorted(index[0:2]))
            kl = tuple(sorted(index[2:4]))
            for key in V.keys():
                if V[key] == ij:
                    V_ij = key
                if V[key] == kl:
                    V_kl = key          
            tensor[index] = matrix[(V_ij, V_kl)]
    else:
        raise ValueError("Method `voigt_inv` did not receive valid input for keyword `mode`.")
    return tensor


def plot_directional_young_modulus(compliance_tensor, fn_png="directional_young_modulus.png"):
    """Plot the three-dimensional directional Young modulus, based on the compliance tensor.

    Parameters
    ----------
    compliance_tensor : numpy.ndarray, shape=(3, 3, 3, 3)
        A (3 x 3 x 3 x 3) compliance tensor, expressed in atomic units.
    fn_png : str, optional
        The PNG filename to write the figure to.
    """
    import matplotlib.pyplot as plt
    gigapascal = 1e9*pascal
    
    # Create the mesh in spherical coordinates and compute corresponding E.
    theta = np.linspace(0, np.pi, 100)
    phi = np.linspace(0, 2*np.pi, 100)
    PHI, THETA = np.meshgrid(phi, theta)
    U = [np.cos(PHI)*np.sin(THETA), np.sin(PHI)*np.sin(THETA), np.cos(THETA)]

    E = np.zeros(THETA.shape)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    E += U[i]*U[j]*U[k]*U[l]*compliance_tensor[i,j,k,l]
    E = np.absolute(1/E)/gigapascal

    # Express the mesh in the cartesian system.
    X, Y, Z = E*np.cos(PHI)*np.sin(THETA), E*np.sin(PHI)*np.sin(THETA), E*np.cos(THETA)


    def set_axes_equal(ax: plt.Axes):
        """Set three-dimensional plot axes to equal scale.

        Make the axes of a three-dimensional plot have equal scale so that spheres appear as spheres and cubes as cubes.  
        Required since ``ax.axis("equal")`` and ``ax.set_aspect("equal")`` don't work on three-dimensional plots.
        """
        limits = np.array([
            ax.get_xlim3d(),
            ax.get_ylim3d(),
            ax.get_zlim3d(),
        ])
        origin = np.mean(limits, axis=1)
        radius = 0.5*np.max(np.abs(limits[:,1] - limits[:,0]))
        _set_axes_radius(ax, origin, radius)

    def _set_axes_radius(ax, origin, radius):
        x, y, z = origin
        # Alter the limits manually if these automatic limits are not to your liking.
        ax.set_xlim3d([x - radius, x + radius])
        ax.set_ylim3d([y - radius, y + radius])
        ax.set_zlim3d([z - radius, z + radius])


    # Plot the surface.
    fig = plt.figure()

    ax = fig.add_subplot(projection="3d")

    ax.set_box_aspect([1,1,1])
    ax.plot_surface(X, Y, Z)
    set_axes_equal(ax)
    ax.set_xlabel(r"$\mathrm{E_x \; [GPa]}$")
    ax.set_ylabel(r"$\mathrm{E_y \; [GPa]}$")
    ax.set_zlabel(r"$\mathrm{E_z \; [GPa]}$")
    
    ax = plt.gca()
    # Delete the tick labels of one or more axes.
    #ax.xaxis.set_ticklabels([])
    #ax.yaxis.set_ticklabels([])
    #ax.zaxis.set_ticklabels([])
    
    # Reduce the number of tick labels for better visibility.
    every_nth = 2
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    for n, label in enumerate(ax.yaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    for n, label in enumerate(ax.zaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)

    # Delete the tick lines of one or more axes.
    #for line in ax.xaxis.get_ticklines():
    #    line.set_visible(False)
    #for line in ax.yaxis.get_ticklines():
    #    line.set_visible(False)
    #for line in ax.zaxis.get_ticklines():
    #    line.set_visible(False)
    
    plt.show()


