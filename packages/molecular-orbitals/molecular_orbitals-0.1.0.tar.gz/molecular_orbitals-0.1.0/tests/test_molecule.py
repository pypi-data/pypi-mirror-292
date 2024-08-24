# molecular_orbitals/tests/test_molecule.py

import unittest
from molecular_orbitals.core.molecule import Molecule, Atom

class TestMolecule(unittest.TestCase):
    """
    Unit tests for the Molecule class.
    """

    def test_add_atom(self):
        """
        Test that an Atom can be added to a Molecule.
        """
        molecule = Molecule(atoms=[])
        atom = Atom(element='H', position=(0.0, 0.0, 0.0))
        molecule.add_atom(atom)
        self.assertEqual(len(molecule.get_atoms()), 1)
        self.assertEqual(molecule.get_atom(0), atom)

    def test_get_atom(self):
        """
        Test that an Atom can be retrieved by index from a Molecule.
        """
        atom1 = Atom(element='H', position=(0.0, 0.0, 0.0))
        atom2 = Atom(element='O', position=(1.0, 0.0, 0.0))
        molecule = Molecule(atoms=[atom1, atom2])
        self.assertEqual(molecule.get_atom(1), atom2)

if __name__ == '__main__':
    unittest.main()
