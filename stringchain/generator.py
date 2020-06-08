from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Dict, Set, Iterable, Tuple


@dataclass
class NodeInfo:
  adjacent: Set[str]
  is_variable: bool


@dataclass
class StringGraphVisitor(ABC):
  _var_marks: Tuple[str, str]

  @abstractmethod
  def visit_roots(self, roots: Iterable[str]):
    pass

  @abstractmethod
  def visit_node(self, node: str, info: NodeInfo):
    pass


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
        raise ValueError(f"child node {child} already exist with contradicting variable status {not variable}")
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

  # breadth first traversal
  def bfs_visit(self, visitor: StringGraphVisitor):
    to_visit = set(self._info.keys())
    visitor.visit_roots(self._roots)
    q = deque(sorted(self._roots))
    while q:
      front = q.popleft()
      if front in to_visit:
        info = self._info[front]
        visitor.visit_node(front, info)
        to_visit.remove(front)

        for child in sorted(info.adjacent):
          if child in to_visit:
            q.append(child)


@dataclass
class GraphGenerator:
  var_marks = ("{", "}")
  delimiter: str = "."

  def __post_init__(self):
    self._mark_size_left, self._mark_size_right = map(len, self.var_marks)
    if self._mark_size_left < 1 or self._mark_size_right < 1:
      raise ValueError("Variable marks cannot be empty")

  def _node_name_and_variable_status(self, item: str):
    match_left, match_right = item.startswith(self.var_marks[0]), item.endswith(self.var_marks[1])
    if match_left != match_right:
      raise ValueError(f"{item} matches variable mark on the left but not right or vice versa")

    status = match_left and match_right
    name = item[self._mark_size_left:-self._mark_size_right] if status else item
    return status, name

  def _split(self, s: str):
    return filter(len, map(str.strip, s.split(self.delimiter)))

  def _generate(self, lines: Iterable[Iterable[str]]) -> StringGraph:
    sg = StringGraph()
    for line in lines:
      if line:  # if line is not empty
        # add root
        head, *tail = line
        variable, name = self._node_name_and_variable_status(head)
        if variable:
          raise ValueError("Starting node is root, cannot be a variable")
        sg.add_root(name)

        # add the rest
        parent = name
        while tail:
          head, *tail = tail
          variable, child = self._node_name_and_variable_status(head)
          sg.add_child(parent, child, variable)
          parent = child

    return sg

  def generate(self, inputs: str) -> StringGraph:
    lines = filter(len, map(str.strip, inputs.splitlines()))
    strings = map(self._split, lines)
    return self._generate(strings)
