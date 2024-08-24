# molecular_orbitals/core/molecule.py

class Atom:
    def __init__(self, element: str, position: tuple):
        """
        Initializes an Atom with an element and its position.

        :param element: The chemical element of the atom (e.g., 'H' for hydrogen).
        :param position: A tuple representing the atom's position in 3D space (x, y, z).
        """
        self.element = element
        self.position = position

    def __repr__(self):
        return f"Atom(element='{self.element}', position={self.position})"


class Molecule:
    def __init__(self, atoms: list):
        """
        Initializes a Molecule with a list of atoms.

        :param atoms: A list of Atom objects that make up the molecule.
        """
        self.atoms = atoms

    def __repr__(self):
        return f"Molecule(atoms={self.atoms})"

    def add_atom(self, atom: Atom):
        """
        Adds an Atom to the molecule.

        :param atom: The Atom object to add to the molecule.
        """
        self.atoms.append(atom)

    def get_atom(self, index: int) -> Atom:
        """
        Retrieves an Atom from the molecule by its index.

        :param index: The index of the atom to retrieve.
        :return: The Atom object at the specified index.
        """
        return self.atoms[index]

    def get_atoms(self) -> list:
        """
        Retrieves the list of atoms in the molecule.

        :return: A list of Atom objects.
        """
        return self.atoms
