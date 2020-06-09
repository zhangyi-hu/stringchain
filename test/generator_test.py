import os
from typing import Set

from pytest import raises

from stringchain.generator import GraphGenerator, PyCodeGenVisitor
from stringchain.stringgraph import StringGraphVisitor, NodeInfo


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


def test_python_code_gen_visitor():
  inputs = """
  foo. bar. goo. bar. foo
  goo. one. {two}. bar
  one . this . that
  """
  gg = GraphGenerator()
  sg = gg.generate(inputs)
  visitor = PyCodeGenVisitor(gg.var_marks, 'Foo')
  sg.bfs_visit(visitor)
  dir_name = os.path.dirname(os.path.realpath(__file__))
  fname = os.path.join(dir_name, "..", "stringchain", "srcgen", visitor.rootclass_name + ".py")
  with open(fname, "w") as out:
    out.write(visitor.build())


def test_string_chain_builder():
  from stringchain.srcgen.FooBuilder import FooBuilder
  builder = FooBuilder()
  with raises(ValueError) as ex:
    FooBuilder.build(builder.goo.one.two.bar)
  assert "Unassigned variables: {two}" == str(ex.value)

  with raises(ValueError) as ex:
    FooBuilder.build(builder.goo.one.two.bar, goo=123)
  assert "Variable {goo} not present in string chain: goo.one.{two}.bar" == str(ex.value)

  res = FooBuilder.build(builder.goo.one.two.bar, two=123)
  assert "goo.one.123.bar" == res
