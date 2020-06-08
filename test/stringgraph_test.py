from stringchain.stringgraph import StringGraph


def test_string_graph():
  sg = StringGraph()
  sg.add_root("foo")
  sg.add_child("foo", "bar")
  sg.add_root("bar")

  assert sg.get_children("foo") == {"bar"}
  assert sg.get_children("bar") == set()
