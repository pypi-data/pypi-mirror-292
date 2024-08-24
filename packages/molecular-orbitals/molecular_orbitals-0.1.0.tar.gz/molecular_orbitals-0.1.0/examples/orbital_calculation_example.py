# examples/orbital_calculation_example.py

from molecular_orbitals.core.molecule import Molecule, Atom
from molecular_orbitals.core.orbital_calculation import OrbitalCalculation

# Create a simple molecule, e.g., H2
atoms = [
    Atom('H', (0.0, 0.0, 0.0)),
    Atom('H', (0.0, 0.0, 0.74))
]
molecule = Molecule(atoms)

# Calculate orbitals using the Hartree-Fock method
orbital_calculation = OrbitalCalculation(molecule)
orbitals = orbital_calculation.calculate_orbitals(method='HF')

# Print the orbital matrix
print("Orbital matrix:")
print(orbitals)
