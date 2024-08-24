# molecular_orbitals/visualization/orbital_visualization.py

import matplotlib.pyplot as plt
import numpy as np

class OrbitalVisualizer:
    def __init__(self, orbital_data: np.ndarray):
        """
        Initializes the OrbitalVisualizer with orbital data.

        :param orbital_data: A numpy array containing the orbital data.
        """
        self.orbital_data = orbital_data

    def plot_2d(self, title: str = "Molecular Orbital 2D Plot", save_to: str = None):
        """
        Visualizes the molecular orbital in 2D.

        :param title: The title of the plot.
        :param save_to: If specified, saves the image to a file instead of displaying it.
        """
        plt.imshow(self.orbital_data, cmap='viridis')
        plt.colorbar(label='Orbital Value')
        plt.title(title)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')

        if save_to:
            plt.savefig(save_to)
            plt.close()
        else:
            plt.show()

    def plot_3d(self, title: str = "Molecular Orbital 3D Plot", save_to: str = None):
        """
        Visualizes the molecular orbital in 3D.

        :param title: The title of the plot.
        :param save_to: If specified, saves the image to a file instead of displaying it.
        """
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x, y = np.meshgrid(range(self.orbital_data.shape[0]), range(self.orbital_data.shape[1]))
        ax.plot_surface(x, y, self.orbital_data, cmap='viridis')
        ax.set_title(title)

        if save_to:
            plt.savefig(save_to)
            plt.close()
        else:
            plt.show()
