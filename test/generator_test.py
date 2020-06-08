from pytest import raises

from stringchain.generator import StringGraph, GraphGenerator


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
