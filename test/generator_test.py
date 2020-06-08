from typing import Set

from pytest import raises

from stringchain.generator import StringGraph, GraphGenerator, StringGraphVisitor, NodeInfo


def test_graph_generator():
  inputs = """
  foo  . bar

     bar .bar.goo
  foo.one.{two}.this
  bar.one.this.that
  """
  gg = GraphGenerator()
  sg = gg.generate(inputs)

  assert sg.is_variable('two')
  assert sg.get_roots() == {'foo', 'bar'}
  assert sg.get_children('foo') == {'bar', 'one'}
  assert sg.get_children('bar') == {'bar', 'goo', 'one'}
  assert sg.get_children('one') == {'two', 'this'}
  assert sg.get_children('this') == {'that'}


def test_graph_generator_failure():
  gg = GraphGenerator()
  inputs = """
  {foo}.bar
  """
  with raises(ValueError) as ex:
    gg.generate(inputs)
  assert "Starting node is root, cannot be a variable" == str(ex.value)

  inputs = """
  foo.bar
  goo.{bar}
  """
  with raises(ValueError) as ex:
    gg.generate(inputs)
  assert "child node bar already exist with contradicting variable status False" == str(ex.value)

  inputs = """
  foo.{bar}
  bar.foo
  """
  with raises(ValueError) as ex:
    gg.generate(inputs)
  assert "bar already defined as a variable, cannot be used as a root." == str(ex.value)


def test_string_graph():
  sg = StringGraph()
  sg.add_root("foo")
  sg.add_child("foo", "bar")
  sg.add_root("bar")

  assert sg.get_children("foo") == {"bar"}
  assert sg.get_children("bar") == set()


class ToStringVisitor(StringGraphVisitor):
  def __init__(self):
    self.result = ""

  def visit_roots(self, roots: Set[str]):
    self.result += "{" + ", ".join(sorted(roots)) + "}\n"

  def visit_node(self, node: str, info: NodeInfo):
    prefix = "$" if info.is_variable else ""
    self.result += prefix + node + " -> {" + ", ".join(sorted(info.adjacent)) + "}\n"


def test_string_graph_visitor():
  inputs = """
  foo. bar. goo. bar. foo
  goo. one. {two}. bar
  one . this . that
  """
  bm_dump = """{foo, goo, one}
foo -> {bar}
goo -> {bar, one}
one -> {this, two}
bar -> {foo, goo}
this -> {that}
$two -> {bar}
that -> {}
"""
  gg = GraphGenerator()
  sg = gg.generate(inputs)
  visitor = ToStringVisitor()
  sg.bfs_visit(visitor)
  assert bm_dump == visitor.result
