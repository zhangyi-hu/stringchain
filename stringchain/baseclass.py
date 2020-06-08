from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Optional, ClassVar


@dataclass(eq=False, repr=False, frozen=True)
class StringTreeNode(ABC):
  """
  A Abstract class that can be inherited to build delimited strings.
  By subclassing DotStringTree, one can design a DSL describing a tree,
  where each node is a string, from predetermined set of possible values.
  For instance, root.[foo.[here|there]|bar.[one|two]] is such a DSL
  If a tree node, foo for instance, is marked as a variable, then we surround it with "{}",
  and the resulted string might look like: root.{foo}.here
  Later we can substitute variable foo with run time value, for instance "314565",
  and the string will be converted to root.314565.here
  """
  _path_to_parent: Tuple[str, ...] = ()
  _value: Optional[str] = None

  # Concrete subclass of StringTreeNode, if not a leaf, must override the class field _children
  # with all possible string values of its children nodes.
  _children: ClassVar[Tuple[str, ...]] = ()
  _is_variable: ClassVar[bool] = False

  _variable_mark_left: ClassVar[str] = "{"
  _variable_mark_right: ClassVar[str] = "}"

  def path(self) -> Tuple[str, ...]:
    if self._value is None:  # only possible when this node is the root
      return ()

    # surround this node with variable marks to mark it as an variable
    if self.__class__._is_variable:
      value = self.__class__._variable_mark_left + self._value + self.__class__._variable_mark_right
    else:
      value = self._value

    if self._path_to_parent:
      return self._path_to_parent + (value,)
    else:
      return value,

  @abstractmethod
  def _get_class(self, item: str):
    """
    The subclass must have the following implementation of this method

    def _get_class(self, item: str):
      return globals()[item]

    globals() only contains the objects in the same module where self.__class__ is defined
    """
    pass

  def __getattribute__(self, item):
    children = object.__getattribute__(self, '_children')
    if item in children:
      # load the class with class name 'item'
      class_whose_name_is_item = object.__getattribute__(self, '_get_class')(item)
      # load the path of the current node
      path = object.__getattribute__(self, 'path')()
      # create and return the new tree node an instance of class 'item'
      return class_whose_name_is_item(_path_to_parent=path, _value=item)
    else:  # if attribute 'item' not registered as a child, just treat as a normal attribute
      return object.__getattribute__(self, item)
