from typing import Tuple
from bayes_network import BayesNetwork
ROUND_DIGITS = 5

def CPTVertex(p) -> dict[str, float]:
    """
    Calculates the Conditional Probability Table (CPT) for a vertex.

    Parameters:
    p (float): The probability value for the 'low' state.

    Returns:
    dict[str, float]: A dictionary representing the CPT with 
    'low', 'medium', and 'high' states and their corresponding probabilities.
    """
    return {'low' : round(p, ROUND_DIGITS),
            'medium' : round(min(1, p * 2), ROUND_DIGITS),
            'high' : round(min(1, p * 3), ROUND_DIGITS)}

def CPTEdge(qi, leakage) -> dict[Tuple[bool, bool], float]:
    """
    Computes the Conditional Probability Table (CPT) for an edge in a Bayesian network.

    Parameters:
    - qi (float): The probability of the edge being blocked given excatly one of its parents is true.
    - leakage (float): The probability of the edge being blocked when both its parents are false.

    Returns:
    - cpt (dict[Tuple[bool, bool], float]): The CPT for the edge,
      represented as a dictionary of tuples (parent values) to probabilities.
    """
    return {(False, False): leakage,
            (True, False): round(1 - qi,ROUND_DIGITS),
            (False, True): round(1 - qi, ROUND_DIGITS),
            (True, True): round(1 - qi ** 2, ROUND_DIGITS)}

def InitBN(initFilePath: str) -> BayesNetwork:
    """
    Initializes a Bayes Network based on the information provided in the given file.

    Args:
        initFilePath (str): The path to the file containing the initialization information.

    Returns:
        BayesNetwork: The initialized Bayes Network.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    """
    with open(initFilePath, 'r') as f:
        # find all lines starting with '#' and cut them off on ';'
        lines = list(line.split(';')[0].split('#')[1].strip().split(' ')
                     for line in f.readlines() if line.startswith("#"))  # seperate the line to a list of words/tokens.
        lines = list(list(filter(lambda e: e!='', line)) for line in lines) # filter empty words/tokens

    x = [int(line[1]) for line in lines if line[0].lower() == 'x'][0]
    y = [int(line[1]) for line in lines if line[0].lower() == 'y'][0]

    leakage = list(float(line[1]) for line in lines if line[0].lower() == 'l')[0]
    season = [{"low" : [float(line[1])],
              "medium": [float(line[2])],
              "high": [float(line[3])]} for line in lines if line[0].lower() == 's'][0]

    nodes = [(i, j) for i in range(x + 1) for j in range(y + 1)]

    nodesCPT, fragEdgesCPT = {node: {'low': 0, 'medium': 0, 'high': 0} for node in nodes}, {}
    for line in lines:
        action = line[0]
        if action == 'V':
            nodesCPT[(int(line[1]), int(line[2]))] = CPTVertex(float(line[3]))
        if action == 'F':
            fragEdgesCPT[tuple(sorted(((int(line[1]), int(line[2])),
                          (int(line[3]), int(line[4])))))] = CPTEdge(1 - float(line[5]), leakage)
        if action == 'B':
            fragEdgesCPT[tuple(sorted(((int(line[1]), int(line[2])),
                          (int(line[3]), int(line[4])))))] = {k: 1.0 for k in [(False, False), (True, False), (False, True), (True, True)]}
    print("season: ", season)
    print("nodesCPT: ", nodesCPT)
    print("fragEdgesCPT: ", fragEdgesCPT)
    print('\n\n')

    return BayesNetwork(season, fragEdgesCPT, nodesCPT, x, y)

def PlotBN(bayesNetwork: BayesNetwork):
    """
    Plots the given Bayes Network.

    Args:
        bayesNetwork (BayesNetwork): The Bayes Network to be plotted.
    """
    import networkx as nx
    import matplotlib.pyplot as plt

    if not bayesNetwork.bn: return # If the network is empty, do not plot
    pos = nx.spring_layout(bayesNetwork.bn)  # Generates a layout for nodes
    plt.figure(figsize=(16, 9))
    # Determine layout bounds to adjust annotation positions dynamically
    x_values, y_values = zip(*pos.values())
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_range = x_max - x_min
    y_range = y_max - y_min
    # Pad the range to ensure annotations fit
    plt.xlim(x_min - 0.1 * x_range, x_max + 0.1 * x_range)
    plt.ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)

    # Draw the network structure
    nx.draw(bayesNetwork.bn, pos, with_labels=True, node_size=2000, node_color='lightblue', arrowsize=20, font_weight='bold')

    # Annotate with CPT information
    for node in nx.topological_sort(bayesNetwork.bn):
        CPT = '\n'.join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in bayesNetwork.VarCPT(node).items()])
        plt.text(pos[node][0], max(pos[node][1] - 0.25, y_min - 0.012), s=CPT, bbox=dict(facecolor='white', alpha=0.5), horizontalalignment='center',)

    plt.title("Bayesian Network with Conditional Probability Tables")
    plt.axis('off')
    plt.ion()
    plt.show()
    plt.pause(3)
