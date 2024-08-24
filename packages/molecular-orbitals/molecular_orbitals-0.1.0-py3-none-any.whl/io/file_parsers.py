# molecular_orbitals/io/file_parsers.py

class XYZParser:
    def __init__(self, filepath: str):
        """
        Initializes the XYZParser with a file path.

        :param filepath: The path to the XYZ file to be parsed.
        """
        self.filepath = filepath

    def parse(self):
        """
        Parses the XYZ file and returns a list of atoms with their coordinates.

        :return: A list of dictionaries, each containing the element and position of an atom.
        """
        atoms = []
        with open(self.filepath, 'r') as file:
            lines = file.readlines()[2:]  # The first two lines in an XYZ file are comments
            for line in lines:
                parts = line.split()
                element = parts[0]
                position = tuple(map(float, parts[1:4]))
                atoms.append({"element": element, "position": position})
        return atoms

