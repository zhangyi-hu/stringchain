from dataclasses import dataclass
from typing import Dict, Set


@dataclass
class NodeInfo:
  adjacent: Set[str]
  is_variable: bool


class StringGraph:
  """
  This graph allows circles
  """

  def __init__(self):
    self._roots: Set[str] = set()
    self._info: Dict[str, NodeInfo] = {}

  def add_root(self, root: str):
    # forbid using a variable as root
    if root in self._info:
      if self._info[root].is_variable:
        raise ValueError(f"{root} already defined as a variable, cannot be used as a root.")
    else:
      self._info[root] = NodeInfo(set(), False)

    self._roots.add(root)

  # add a new vertex: child and a directional edge: parent -> child
  def add_child(self, parent: str, child: str, variable: bool = False):
    if parent not in self._info:
      raise ValueError(f"parent node, {parent} not exist in graph.")

    # add vertex, child
    if child in self._info:
      if self._info[child].is_variable != variable:
        raise ValueError(f"child node already exist with contradicting variable status {not variable}")
    else:
      self._info[child] = NodeInfo(set(), variable)

    # add edge, parent -> child
    self._info[parent].adjacent.add(child)

  def is_variable(self, node: str) -> bool:
    if node not in self._info:
      raise KeyError(f"{node} not exist in graph")
    return self._info[node].is_variable

  def get_children(self, node: str) -> Set[str]:
    if node not in self._info:
      raise KeyError(f"{node} not exist in graph")
    return self._info[node].adjacent

  def get_roots(self) -> Set[str]:
    return self._roots
