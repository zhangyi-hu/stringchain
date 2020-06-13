import argparse
from dataclasses import dataclass
from os import path
from typing import Iterable

from stringchain.stringgraph import StringGraph, StringGraphVisitor, NodeInfo


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


@dataclass
class PyCodeGenVisitor(StringGraphVisitor):
  """
  A code python code generator that will grammartize the string chain construction with given a string graph
  """

  name: str

  def __post_init__(self):
    self.dataclass_header = "@dataclass(eq=False, repr=False, frozen=True)"
    self.baseclass_name = "AbstractTreeNode"
    self.rootclass_name = f"{self.name}Builder"  # this is the class that the user will be using
    self.blocks = ["\n".join((  # code blocks that will grow when visiting a given string graph
      "# pylint: skip-file",
      "import re",
      "from abc import ABC",
      "from dataclasses import dataclass",
      "from typing import ClassVar",
      "from stringchain import StringTreeNode",
      "",
      "",
      self.dataclass_header,
      f"class {self.baseclass_name}(StringTreeNode, ABC):",
      f"  _variable_mark_left = '{self._var_marks[0]}'",
      f"  _variable_mark_right = '{self._var_marks[1]}'",
      "",
      "  def _get_class(self, item: str):",
      "    return globals()[item]",
      "",
      "",
    ))]

  def build(self) -> str:
    self.blocks.append("\n")
    return "\n".join(self.blocks)

  @staticmethod
  def _quote(item: str) -> str:
    return "'" + item + "',"

  def visit_roots(self, roots: Iterable[str]):
    sorted_roots = sorted(roots)
    self.blocks.append("\n".join((
      self.dataclass_header,
      f"class {self.rootclass_name}({self.baseclass_name}):",
      f"  _children = ({' '.join(map(PyCodeGenVisitor._quote, sorted_roots))})",
      f"  _variable_pattern: ClassVar[str] = '{self._var_marks[0]}.*?{self._var_marks[1]}'",
      "",
      "\n".join((f"  {root}: {root} = None" for root in sorted_roots)),
      "",
      "  @classmethod",
      "  def _mark_variable(cls, variable: str):",
      "    return f'{cls._variable_mark_left}{variable}{cls._variable_mark_right}'",
      "",
      "  @classmethod",
      f"  def build(cls, tree: {self.baseclass_name}, deliminator: str = '.', **kwargs) -> str:",
      "    res = deliminator.join(tree.path())",
      "    for k, v in kwargs.items():",
      "      variable = cls._mark_variable(k)",
      "      if variable not in res:",
      "        raise ValueError(f'Variable {variable} not present in string chain: {res}')",
      "      res = res.replace(variable, str(v))",
      "    not_assigned = re.findall(cls._variable_pattern, res)",
      "    if not_assigned:",
      "      variables = ', '.join(not_assigned)",
      "      raise ValueError(f'Unassigned variables: {variables}')",
      "    return res",
      "",
      ""
    )))

  def visit_node(self, node: str, info: NodeInfo):
    sorted_children = sorted(info.adjacent)
    body = "  pass" if not (sorted_children or info.is_variable) else "\n".join((
      f"  _children = ({' '.join(map(PyCodeGenVisitor._quote, sorted_children))})" if sorted_children else "",
      f"  _is_variable = True" if info.is_variable else "",
      "",
      "\n".join((f"  {child}: {child} = None" for child in sorted_children)),
    ))
    self.blocks.append("\n".join((
      self.dataclass_header,
      f"class {node}({self.baseclass_name}):",
      body,
      "",
      ""
    )))


# a command line tool to generate string chain graph module from a file of string chain samples
def generate():
  parser = argparse.ArgumentParser()
  parser.add_argument("input_file", help="The input file containing the sample string chains", type=str)
  parser.add_argument("module", help="The name of module that will be generated", type=str)
  parser.add_argument("-o", "--outdir", help="The directory to save the generated module file module_name.py",
                      type=str, default=".")
  args = parser.parse_args()

  # 1) process the string chain samples in the input file
  with open(args.input_file, "r") as infile:
    samples: str = infile.read()
  gg = GraphGenerator()
  code_gen = PyCodeGenVisitor(gg.var_marks, args.module)
  string_graph = gg.generate(samples)
  string_graph.bfs_visit(code_gen)

  # 2) generate the module file and save to the specified location
  outfile = path.join(args.outdir, args.module + ".py")
  with open(outfile, "w") as out:
    out.write(code_gen.build())
  print(f"module file {outfile} generated")
