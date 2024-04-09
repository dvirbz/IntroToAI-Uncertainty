from enum import Enum
from typing import Tuple
import copy
import networkx as nx
from package import Package
from type_aliases import Node, Edge
from utils import GetNeighbors

class Grid:
    """Simulator's Grid"""
    numOfPackages = 0

    def __init__(self, x: int , y: int):
        """Initiallizes connected grid with size x*y

        Args:
            x (int): 1st dimension size
            y (int): 2nd dimension size
        """
        self._size: Tuple[int, int] = (x + 1, y + 1)
        self._graph: nx.Graph = nx.grid_2d_graph(x + 1, y + 1)
        self._fragEdges: dict[Edge, float] = {}
        self._packages: dict[Node, list[Package]] = {}
        self._uncertaintyEdges: tuple[tuple[Edge, int]] = () # -1 for unknown, 0 for blocked, 1 for open
        self._policy: dict[Node, dict[tuple[tuple[Edge, int]], tuple[Node, float]]] = {}
    
    @property
    def size(self) -> Tuple[int, int]:
        """Returns the size of the grid"""
        return self._size

    @property
    def graph(self) -> nx.Graph:
        """Returns the networkx graph object"""
        return self._graph

    @property
    def fragEdges(self) -> set[Edge]:
        """returns self.fragEdges

        Args:
            set(Edge): the fragEdges in the grid
        """
        return self._fragEdges

    @property
    def packages(self) -> dict[Node, list[Package]]:
        """returns self._packages

        Returns:
            dict: {Node: Package}
        """
        return self._packages
    
    @property
    def uncertaintyEdges(self) -> dict[Node, list[Package]]:
        """returns self._packages

        Returns:
            dict: {Node: Package}
        """
        return self._uncertaintyEdges
    
    @property
    def policy(self) -> dict[Node, list[Package]]:
        """returns self._packages

        Returns:
            dict: {Node: Package}
        """
        return self._policy

    def UpdateGrid(self, cmd: str, params: list[str] | Edge) -> None:
        """Updates grid

        Args:
            cmd (str): command used to update the grid
            params (list[str]): parameters to the command
        """
        if cmd == UpdateGridType.ACTION.value:
            pass
        if cmd == UpdateGridType.BLOCK.value:
            edge = ((int(params[0]), int(params[1])), (int(params[2]), int(params[3])))
            if edge in self.graph.edges():
                self.graph.remove_edge(*edge)
        if cmd == UpdateGridType.FRAGILE.value:
            edge = ((int(params[0]), int(params[1])), (int(params[2]), int(params[3])))
            self._fragEdges[edge] = float(params[4])
        if cmd == UpdateGridType.PACKAGE.value:
            self.AddPackage(params)

    def AddPackage(self, params: list[str]):
        """Adds a package to the grid

        Args:
            params (str): parameters of the package
        """
        package = Package(params)
        coords = package.pickupLoc
        self._packages[coords] = self._packages.get(coords, []) + [package]

    def PickPackagesFromNode(self, coords: Node, i: int) -> set[Package]:
        """Return a Package at the location if exists and appeard and delete from grid

        Args:
            coords (Node): check if in these coords there is a package

        Returns:
            Package: Package at the location if exists otherwise None
        """
        packages = []
        for package in self._packages.get(coords, [])[:]:
            if package.pickupTime > i: continue
            packages.append(package)
            self._packages[coords].remove(package)
            if not self._packages[coords]:
                del self._packages[coords]
        return packages

    def FilterAppearedPackages(self, i: int) -> dict[Node, list[Package]]:
        """return all packages that are currently available

        Args:
            i (int): current iteration

        Returns:
            dict[Package]: Currently available packages
        """
        appearedPackeges: dict[Node, list[Package]] = {coords:\
            [package for package in packages if package.pickupTime <= i]\
                for coords, packages in self._packages.items()}
        appearedPackeges = {coords: packages for coords, packages in appearedPackeges.items() if packages}
        return appearedPackeges

    def EarliestPacksage(self) -> set[Node]:
        """Returns the node of the package that arrives the earliest

        Returns:
            Node: The node of the earliest package
        """
        earliest = (None, None)
        for node, packages in self._packages.items():
            for package in packages:
                if earliest == (None, None) or package.pickupTime < earliest[1]:
                    earliest = ({node}, package.pickupTime)
                if package.pickupTime == earliest[1]:
                    earliest[0].add(node)
        return earliest[0]

    def GetPickups(self) -> Tuple[Tuple[Node, int]]:
        """Returns the nodes of the packages that need to be picked up

        Returns:
            set[Node]: The nodes of the packages that need to be picked up
        """
        pickups = ()
        for node, packages in self._packages.items():
            for package in packages:
                pickups = pickups + ((node, package.pickupTime),)
        return pickups

    def GetDropdowns(self) -> Tuple[Tuple[Node, int]]:
        dropdowns = ()
        for packages in self._packages.values():
            for package in packages:
                dropdowns = dropdowns + ((package.dropoffLoc, package.dropOffMaxTime),)

        return dropdowns

    def GetUncertaintyPolicy(self, startNode: Node, endNode: Node) -> dict[Node, dict[tuple[tuple[Edge, int]], tuple[Node, float]]]:
        """Returns the uncertainty policy of the grid

        Returns:
            dict[Node, dict[Node, float]]: The uncertainty policy of the grid
        """
        if startNode == endNode: #might need to be different
            return self.policy
        self.policy = {endNode: {(): 0}} | ({node: {self._uncertaintyEdges: float('-inf')} for node in self.graph.nodes() if node != endNode})
        actions = [(endNode,node) for node in GetNeighbors(self, endNode)]
        for action in actions:
            gridCopy = copy.deepcopy(self)
            self.UpdatePolicy(endNode, action) #Might need to be global
            if action in self._fragEdges:
                gridCopy.fragEdges.remove(action) # need to account for reversability            
            gridCopy.GetUncertaintyPolicy(startNode, action[1])
            self.policy = gridCopy.policy # change to update based on max and combine T and F options to U based on their probabilities
            
        return self.policy
                   
    def UpdatePolicy(self, current: Node, action: Edge) -> None:
        """Updates the policy of the grid

        Args:
            current (Node): The current node
            action (Edge): The action to be taken
        """
        if action in self._fragEdges:
            pass
            # update action[1] with F in policy and -1 in value If exitsts F get max and update the best action
            # update action[0]/current with T in policy and -2 in value
        else:
            pass
            # update action[1] with U in policy and -1 in value
            
    def UpdatePolicyValue(self, node: Node, destNode: Node, stepValue: float, uncertaintyEdges: tuple[tuple[Edge, int]]) -> None:
        """Updates the policy value of the grid

        Args:
            node (Node): The current node
            destNode (Node): The destination node
            stepValue (float): The step value
            uncertaintyEdges (tuple[tuple[Edge, int]]): The uncertainty edges
        """
        currentValue = self.policy.get(node, {}).get(uncertaintyEdges, (float('-inf'), None))
        if currentValue[0] == float('-inf'):
            self.policy[node][uncertaintyEdges] = (self.policy[destNode][uncertaintyEdges] + stepValue, destNode)
        else:
            self.policy[node][uncertaintyEdges] = max(currentValue, (self.policy[destNode][uncertaintyEdges] + stepValue, destNode))
            
class UpdateGridType(Enum):
    """Enum for options to update grid."""
    ACTION = 'ACT'
    BLOCK = 'B'
    FRAGILE = 'F'
    PACKAGE = 'P'
