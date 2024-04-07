from typing import Tuple
import networkx as nx
from grid import Grid, UpdateGridType
from agents.agent import Agent, AgentType
from agents.human_agent import HumanAgent
from type_aliases import Node

agent_classes = {
    AgentType.HUMAN.value: HumanAgent,
}

def InitGrid(initFilePath: str) -> Tuple[Grid, list[Agent]]:
    """initializes grid from init file

    Args:
        initFilePath (str): init file path

    Returns:
        Grid: Simulator's grid
        list[Agent]: the agents activated in the simulator
    """
    with open(initFilePath, 'r') as f:
        # find all lines starting with '#' and cut them off on ';'
        lines = list(line.split(';')[0].split('#')[1].strip().split(' ')
                     for line in f.readlines() if line.startswith("#"))  # seperate the line to a list of words/tokens.
        lines = list(list(filter(lambda e: e!='', line)) for line in lines) # filter empty words/tokens

    x = list(int(line[1]) for line in lines if line[0].lower() == 'x')[0] # extract x max value from file
    y = list(int(line[1]) for line in lines if line[0].lower() == 'y')[0] # extract y max value from file

    grid: Grid = Grid(x, y)

    for line in lines:
        action = line[0]
        # if action is of updating the grid type then call UpdateGrid
        if any(action == updateGridType.value for updateGridType in UpdateGridType):
            grid.UpdateGrid(action, line[1:])

    Grid.numOfPackages = len(sum(grid.packages.values(), []))

    agents: list[Agent] = []
    for line in lines: # build the agents specified in the file
        action = line[0]
        if action not in agent_classes: continue
        agents.append(agent_classes[action](line[1:], grid))

    for agent in agents:
        agent.ProcessStep(grid)

    lastDropOffTime = max(p.dropOffMaxTime for p in sum(grid.packages.values(), []))
    Agent.lastDropOffTime = lastDropOffTime

    return grid, agents

def GetNeighbors(grid: Grid, node: Node) -> set[Node]:
    """Gets the neighbors of a node

    Args:
        grid (Grid): the simulator's grid
        node (Node): a node

    Returns:
        set[Node]: the neighbors of the node
    """
    actions = set(edge[1] for edge in grid.graph.edges() if edge[0] == node).union(
        set(edge[0] for edge in grid.graph.edges() if edge[1] == node))
    return actions
