# molecular_orbitals/tests/test_orbital_calculation.py

import unittest
import numpy as np
from molecular_orbitals.core.molecule import Molecule, Atom
from molecular_orbitals.core.orbital_calculation import OrbitalCalculation, PSI4_AVAILABLE

class TestOrbitalCalculation(unittest.TestCase):
    """
    Unit tests for the OrbitalCalculation class.
    """

    def setUp(self):
        """
        Sets up a simple molecule for use in the tests.
        """
        atom1 = Atom(element='H', position=(0.0, 0.0, 0.0))
        atom2 = Atom(element='H', position=(1.0, 0.0, 0.0))
        self.molecule = Molecule(atoms=[atom1, atom2])

    def test_hartree_fock(self):
        """
        Tests the Hartree-Fock calculation method.
        Ensures that the orbital matrix has the correct shape.
        """
        calc = OrbitalCalculation(self.molecule)
        orbitals = calc.calculate_orbitals(method='HF')
        self.assertEqual(orbitals.shape, (2, 2))

    @unittest.skipUnless(PSI4_AVAILABLE, "Psi4 is not available")
    def test_psi4_calculation(self):
        """
        Tests the Psi4 calculation method if Psi4 is available.
        Ensures that the resulting matrix is square.
        """
        calc = OrbitalCalculation(self.molecule)
        orbitals = calc.calculate_orbitals(method='HF', use_psi4=True)
        self.assertTrue(isinstance(orbitals, np.ndarray))
        self.assertEqual(orbitals.shape[0], orbitals.shape[1])  # Should be a square matrix

if __name__ == '__main__':
    unittest.main()
