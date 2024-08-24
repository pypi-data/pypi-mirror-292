# molecular_orbitals/core/orbital_calculation.py

import numpy as np

try:
    import psi4
    PSI4_AVAILABLE = True
except ImportError:
    PSI4_AVAILABLE = False

class OrbitalCalculation:
    def __init__(self, molecule):
        """
        Initializes the OrbitalCalculation with a molecule object.

        :param molecule: A Molecule object containing atomic data.
        """
        self.molecule = molecule

    def calculate_orbitals(self, method='HF', use_psi4=False):
        """
        Calculates molecular orbitals using the specified method.

        :param method: Calculation method, default is 'HF' (Hartree-Fock).
        :param use_psi4: If True, uses Psi4 for calculation (if available).
        :return: A numpy array containing orbital data.
        :raises ValueError: If the method is not supported.
        """
        if use_psi4 and PSI4_AVAILABLE:
            return self._calculate_with_psi4(method)
        elif method == 'HF':
            return self._hartree_fock()
        else:
            raise ValueError(f"Method {method} is not supported")

    def _hartree_fock(self):
        """
        Simple Hartree-Fock method example.
        Returns a dummy orbital matrix.

        :return: A numpy array with random values.
        """
        num_atoms = len(self.molecule.get_atoms())
        return np.random.rand(num_atoms, num_atoms)

    def _calculate_with_psi4(self, method):
        """
        Uses Psi4 for orbital calculation.

        :param method: Calculation method, should be supported by Psi4.
        :return: A numpy array containing the calculated orbitals.
        :raises ValueError: If the method is not supported by Psi4.
        """
        geometry = self._create_psi4_geometry()
        psi4.core.set_output_file("output.dat", False)
        psi4.geometry(geometry)
        
        if method == 'HF':
            psi4_energy, psi4_wfn = psi4.energy('SCF', return_wfn=True)
            return psi4_wfn.Ca().to_array()  # Returns the orbital coefficient matrix
        else:
            raise ValueError(f"Method {method} is not supported by Psi4")

    def _create_psi4_geometry(self):
        """
        Creates a geometry string for Psi4 based on the molecule.

        :return: A string representing the molecular geometry in Psi4 format.
        """
        geometry = "molecule {\n"
        for atom in self.molecule.get_atoms():
            geometry += f"  {atom.element} {atom.position[0]} {atom.position[1]} {atom.position[2]}\n"
        geometry += "}"
        return geometry

    def __repr__(self):
        return f"OrbitalCalculation(molecule={self.molecule})"
