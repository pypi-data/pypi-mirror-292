# examples/reaction_mechanism_example.py

from molecular_orbitals.core.molecule import Molecule, Atom
from molecular_orbitals.core.reaction_mechanism import ReactionMechanism

# Create reactants and products
reactant1 = Molecule([Atom('H', (0.0, 0.0, 0.0)), Atom('Cl', (0.0, 0.0, 1.0))])  # HCl
reactant2 = Molecule([Atom('Na', (0.0, 0.0, 0.0))])  # Na
product1 = Molecule([Atom('Na', (0.0, 0.0, 0.0)), Atom('Cl', (0.0, 0.0, 1.0))])  # NaCl
product2 = Molecule([Atom('H', (0.0, 0.0, 0.0))])  # H

# Analyze the reaction
reaction = ReactionMechanism(reactants=[reactant1, reactant2], products=[product1, product2])
analysis_result = reaction.analyze_reaction()

# Print the analysis results
print("Reaction analysis:")
print(f"Number of reactants: {analysis_result['num_reactants']}")
print(f"Number of products: {analysis_result['num_products']}")
print(f"Activation energy: {analysis_result['activation_energy']}")
print(f"Transition state: {analysis_result['transition_state']}")
