from __future__ import annotations

import json

from PIL import Image
from typing import Any, Dict, List, Optional, Set, Union
from pathlib import Path

from ..types import PathLike
from ..classes import AssetReader, AABB, GameObject, MeshImage, RectTransform, Vector2


class JSONEncoder(json.JSONEncoder):
  def default(self, o: Any):
    try:
      if isinstance(o, Inspector):
        return o.attribute

      return super().default(o)
    except TypeError:
      try:
        return repr(o)
      except:
        return str(o)


class Inspector:
  """
    simple inspector to see what happened behind the prefab structure to make it easier to debug

    ```Python
    # usage
    ins = Inspector(obj)

    # inspect directly
    value = ins.inspect()
    print(value)

    # write into json
    ins.write('test.json')

    # add new instance to inspect
    from UnityPy.classes import Mesh
    Inspector.extend_class(Mesh, ['name', 'path_id'])

    # remove instance
    Inspector.remove_class(Mesh)

    # ignore instance
    from PIL import Image
    Inspector.ignore_class(Image.Image)

    ```
  """
  _ignore: Set[Any] = {AssetReader}
  _extend: Dict[type, List[str]] = {
    Image.Image: [
      'mode',
      'size',
    ],
    GameObject: [
      'name',
      'path_id',
      'active',
      'children',
      'size',
      'scale',
      'local_offset',
      'global_offset',
      'image',
      'MonoBehaviour',
      'RectTransform',
    ],
    MeshImage: [
      'path_id',
      'size',
      'mRawSpriteSize',
      'Sprite',
      'Mesh',
      'image',
      'AABB',
    ],
    RectTransform: [
      'path_id',
      'anchor_min',
      'anchor_max',
      'anchor_pos',
      'size_delta',
      'local_scale',
      'pivot',
    ],
    AABB: [
      'center',
      'extend',
      'padding',
      'size',
    ],
    Vector2: [
      'x',
      'y',
    ],
  }

  _obj: Any
  _keys: List[str]
  attribute: Dict[str, Any]


  def __init__(self, obj: Any, keys: Optional[List[str]] = None, inspect: bool = False) -> None:
    self._obj = obj

    if not keys:
      if type(obj) in self._extend:
        keys = self._extend[type(obj)]
      else:
        keys = dir(obj)

    self._keys = self.filter_keys(self._obj, keys)

    if inspect:
      self.inspect()


  def __repr__(self) -> str:
    return f"<{self.__class__.__name__} {repr(self._obj)}>"


  @property
  def object(self) -> Any:
    return self._obj


  @property
  def instance(self) -> type:
    return type(self._obj)


  @property
  def classname(self) -> str:
    return self._obj.__class__.__name__


  @property
  def module(self) -> str:
    return self._obj.__class__.__module__


  def inspect(self) -> Dict[str, Any]:
    self.attribute = self.get_attribute(self._obj, self._keys)
    return self.attribute


  def write(self, path: PathLike, indent: int = 2) -> Path:
    path = Path(path)
    data = { type(self._obj).__name__: self.inspect() }

    with open(path, 'w', encoding='utf-8') as file:
      json.dump(data, file, indent=indent, cls=JSONEncoder)

    return path


  @classmethod
  def filter_keys(cls, obj: Any, keys: List[str]) -> List[str]:
    return [
      x
      for x in keys
      if not isinstance(getattr(obj, x), tuple(cls._ignore))
    ]


  @classmethod
  def get_attribute(cls, obj: Any, keys: List[str]) -> Dict[str, Any]:
    build = {}

    for key in keys:
      value = getattr(obj, key)
      types = type(value)

      if (types in cls._extend) and (types not in cls._ignore):
        build[key] = cls(value, cls._extend[types], inspect=True)
        continue

      if (key == 'children') and (type(obj) == GameObject):
        build[key] = []

        for child in value:
          build[key].append(cls(child, cls._extend[GameObject], inspect=True))

        continue

      build[key] = value

    return build


  @classmethod
  def ignore_class(cls, instance: type) -> bool:
    try:
      if instance in cls._ignore:
        print(f"{instance} already in ignored list.")
        return False

      cls._ignore.add(instance)

    except:
      return False

    return True


  @classmethod
  def extend_class(cls, instance: type, keys: List[str]) -> bool:
    try:
      if instance in cls._extend:
        print(f"{instance} already in extend list.")
        return False

      cls._extend[instance] = keys

    except:
      return False

    return True


  @classmethod
  def remove_class(cls, instance: type) -> bool:
    try:
      if instance not in cls._extend:
        print(f"{instance} not found in extend list.")
        return False

      del cls._extend[instance]

    except:
      return False

    return True


  @classmethod
  def extend_keys(cls, instance: type, keys: Union[List[str], str]) -> bool:
    if isinstance(keys, str):
      keys = [keys]

    try:
      if instance not in cls._extend:
        return cls.extend_class(instance, keys)

      for key in keys:
        if key in cls._extend[instance]:
          continue

        cls._extend[instance].append(key)

    except:
      return False

    return True


  @classmethod
  def remove_keys(cls, instance: type, keys: Union[List[str], str]) -> bool:
    if isinstance(keys, str):
      keys = [keys]

    try:
      if instance not in cls._extend:
        print(f"{instance} not available in extend list.")
        return False

      for key in keys:
        if key not in cls._extend[instance]:
          continue

        cls._extend[instance].remove(key)

    except:
      return False

    return True
