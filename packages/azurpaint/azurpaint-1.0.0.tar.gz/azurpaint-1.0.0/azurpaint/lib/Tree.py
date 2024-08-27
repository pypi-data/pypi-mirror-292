from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Union

from ..types import PathLike
from ..classes import GameObject, Vector2

from .Inspector import Inspector


class Node(Inspector):
  """
    `Node` is inherited from `Inspector` but with it's own static property
  """
  _ignore = copy.deepcopy(Inspector._ignore)
  _extend = copy.deepcopy(Inspector._extend)


class Tree:
  """
    Simple tool to debug/investiage prefab structure, work like tree command.
  """
  root: Node
  _indent: int
  _spacing: int
  _ignore: Dict[type, Dict[str, Optional[List[str]]]]
  _branch: Dict[str, str] = {
    'line': '│',
    'enter': '─',
    'split': '├',
    'close': '└',
    'space': ' ',
  }

  def __init__(self, root: Any, indent: int = 4, spacing: int = 1) -> None:
    self.root = Node(root)
    self._indent = indent
    self._spacing = spacing
    self._ignore = {}


  def __str__(self) -> str:
    return self.execute()


  def __repr__(self) -> str:
    return f"<Tree root={repr(self.root.object)}>"


  @property
  def indent(self) -> int:
    return self._indent


  @property
  def spacing(self) -> int:
    return self._spacing


  def write(self, path: PathLike, strip: bool = False) -> None:
    with open(path, 'w', encoding='utf-8') as file:
      file.write(self.execute() if not strip else self.strip())


  def ignore(
    self,
    instance: type,
    attribute: Optional[str] = None,
    value: Optional[List[str]] = None
  ) -> None:
    if instance not in self._ignore:
      self._ignore[instance] = {}

    if attribute:
      self._ignore[instance][attribute] = value

  def branch(
    self,
    *,
    line: str = '│',
    enter: str = '─',
    split: str = '├',
    close: str = '└',
    space: str = ' '
  ) -> None:
    self._branch = {
      'line': line,
      'enter': enter,
      'split': split,
      'close': close,
      'space': space
    }

  def strip(self) -> str:
    prev_branch = { **self._branch }
    prev_spacing = self._spacing

    self.branch(line=' ', enter=' ', split=' ', close=' ', space=' ')
    self._spacing = 0

    output = self.execute()

    # restore config
    self._branch = prev_branch
    self._spacing = prev_spacing
    return output


  def execute(self) -> str:
    return f"{repr(self.root.object)}\n{self._get_node(self.root)}"


  def _get_prefix(self, end: bool = False) -> str:
    return (
      self._branch['space' if end else 'line'] +
      (self._branch['space'] * max(self.indent - 1, 0))
    )


  def _get_suffix(self, end: bool = False) -> str:
    return (
      self._branch['close' if end else 'split'] +
      (self._branch['enter'] * max(self.indent - 1, 0))
    )


  def _get_node(self, node: Node, *, prefix: str = '') -> str:
    result = node.inspect() # inspect to ensure that data is latest
    output = ''

    _prefix = self._get_prefix()
    _suffix = self._get_suffix()
    _ignore = None

    # filter entire object
    if node.instance in self._ignore:
      _ignore = self._ignore[node.instance]

      if not len(_ignore):
        return output

    # filtering key
    keys = []

    for key, value in result.items():
      if isinstance(value, Node):
        value = value.object

      if _ignore and len(_ignore) and (key in _ignore):
        if not _ignore[key]:
          continue

        _ignore_value = _ignore.get(key) or []

        if (value in _ignore_value) or ('__ignore__' in _ignore_value):
          continue

      keys.append(key)


    # get gameobject children
    children = []

    if node.instance == GameObject:
      if not _ignore:
        children = result['children']

      elif len(_ignore) and ('name' in _ignore) and _ignore['name']:
        children = [
          child
          for child in result['children']
          if child.object.name not in _ignore['name']
        ]


    # attribute processor
    prev_node = False

    for index, key in enumerate(keys, start=1):
      if (node.instance == GameObject) and (key in ['parent', 'children']):
        continue

      if (index == len(keys)) and not len(children):
        _prefix = self._get_prefix(end=True)
        _suffix = self._get_suffix(end=True)

      value = result[key]
      template = f"{prefix}{_suffix}<{{type}} {key}={{value}}>\n"

      if prev_node:
        output += f"{(prefix + self._branch['line']).rstrip()}\n" * self.spacing

      if isinstance(value, Node):
        if value.instance == Vector2:
          output += template.format(type=value.classname, value=value.object.values())
          prev_node = False
          continue

        if (value.instance in self._ignore) and not len(self._ignore[value.instance]):
          output += template.format(type=value.classname, value=repr(value.object))
          prev_node = False
          continue

        elif not prev_node:
          output += f"{(prefix + self._branch['line']).rstrip()}\n" * self.spacing

        output += template.format(type=value.classname, value=f"{value.module}")
        output += self._get_node(value, prefix=prefix + _prefix)
        prev_node = True
        continue

      output += template.format(type=type(value).__name__, value=value)
      prev_node = False

    if node.instance != GameObject:
      return output

    for index, child in enumerate(children, start=1):
      if index == len(children):
        _prefix = self._get_prefix(end=True)
        _suffix = self._get_suffix(end=True)

      output += f"{(prefix + self._branch['line']).rstrip()}\n" * self.spacing
      output += f"{prefix}{_suffix}{repr(child.object)}\n"
      output += self._get_node(child, prefix=prefix + _prefix)

    return output


  @staticmethod
  def ignore_class(instance: type) -> bool:
    return Node.ignore_class(instance=instance)


  @staticmethod
  def extend_class(instance: type, keys: List[str]) -> bool:
    return Node.extend_class(instance=instance, keys=keys)


  @staticmethod
  def remove_class(instance: type) -> bool:
    return Node.remove_class(instance=instance)


  @staticmethod
  def extend_keys(instance: type, keys: Union[List[str], str]) -> bool:
    return Node.extend_keys(instance=instance, keys=keys)


  @staticmethod
  def remove_keys(instance: type, keys: Union[List[str], str]) -> bool:
    return Node.remove_keys(instance=instance, keys=keys)
