# Molecular Orbitals and Reaction Modeling

This project provides tools for modeling molecular orbitals and chemical reactions using quantum chemistry methods. It includes support for both built-in methods and integration with external libraries like Psi4.

## Features

- **Molecular Orbital Calculation:** Supports Hartree-Fock method and integration with Psi4 for more advanced calculations.
- **Reaction Mechanism Analysis:** Analyze chemical reactions, including activation energy and transition states.
- **Visualization:** 2D and 3D visualization of molecular orbitals.
- **Data Parsing and Exporting:** Parse XYZ files and export data in JSON or CSV formats.

## Installation

### Requirements

- Python 3.10+
- Optional: [Psi4](https://psicode.org/) for advanced quantum chemistry calculations

### Installing Dependencies

First, ensure you have Python 3.10+ installed. Then, clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

If you want to use Psi4 for calculations, install it separately:

```bash
conda install psi4 -c psi4
```

## Usage

### Command-Line Interface (CLI)

This project provides a CLI to interact with the core functionalities.

#### Parsing XYZ files

Parse an XYZ file to extract molecular information:

```bash
python cli.py parse_xyz molecule.xyz
```

#### Exporting data

Export molecular data to JSON or CSV:

```bash
python cli.py export_data molecule.xyz output.json --format json
```

#### Visualizing orbitals

Visualize molecular orbitals in 2D or 3D:

```bash
python cli.py visualize_orbitals molecule.xyz
```

### Library Usage

You can also use this project as a Python library. Below is a simple example:

```python
from molecular_orbitals.core.molecule import Molecule, Atom
from molecular_orbitals.core.orbital_calculation import OrbitalCalculation

# Create a molecule
atoms = [Atom('H', (0, 0, 0)), Atom('H', (0, 0, 1))]
molecule = Molecule(atoms)

# Calculate orbitals
calc = OrbitalCalculation(molecule)
orbitals = calc.calculate_orbitals()

# Print the orbital matrix
print(orbitals)
```

### Examples

Here are some example scripts that demonstrate how to use the various features of the project:

- **Example 1:** [Basic Orbital Calculation](examples/orbital_calculation_example.py)
- **Example 2:** [Reaction Mechanism Analysis](examples/reaction_mechanism_example.py)

### FAQ

#### Q: How do I install Psi4 for advanced calculations?
A: You can install Psi4 using Conda with the following command:
```bash
conda install psi4 -c psi4
```

#### Q: Can I extend the project with new calculation methods?
A: Yes, you can add new methods by modifying the `orbital_calculation.py` module and updating the CLI or library interface as needed.

## Running Tests

To run the unit tests, use:

```bash
python -m unittest discover -s molecular_orbitals/tests
```

## Contributing

Feel free to submit issues and pull requests. Contributions are welcome!

### Contributing Guide

1. **Fork the repository** to your GitHub account.
2. **Clone your fork** to your local machine.
3. **Create a new branch** for your changes.
4. **Make your changes** and commit them with descriptive messages.
5. **Push your changes** to your fork on GitHub.
6. **Submit a pull request** to the main repository.

Please ensure that your code follows the existing style and that all tests pass before submitting.

## License

This project is licensed under the MIT License.
