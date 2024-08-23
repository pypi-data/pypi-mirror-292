# This Python file uses the following encoding: utf-8
"""autogenerated by genpy from digitaleye_msgs/Action.msg. Do not edit."""
import codecs
import sys
python3 = True if sys.hexversion > 0x03000000 else False
import genpy
import struct


class Action(genpy.Message):
  _md5sum = "b1601f61caa8fd9c8fc9989dd78476a0"
  _type = "digitaleye_msgs/Action"
  _has_header = False  # flag to mark the presence of a Header object
  _full_text = """# Action definition

# action id
uint32 id

# external action id
uint32 ext_id

# action for the following entity id(s) (can be empty)
uint64[] entity_id

# action for the following entity class(es) (can be empty), use ENT_CLASS
uint32[] entity_class

# start time of allocation (included) (Epoch timestamp in seconds)
uint64 start

# end time of allocation (included) (Epoch timestamp in seconds)
uint64 end

# duration of allocation (seconds)
uint64 duration

# category of action, use ALLOC_CAT_ in Constants Allocations
uint32 category

# action dependencies
uint32[] action_dep
"""
  __slots__ = ['id','ext_id','entity_id','entity_class','start','end','duration','category','action_dep']
  _slot_types = ['uint32','uint32','uint64[]','uint32[]','uint64','uint64','uint64','uint32','uint32[]']

  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       id,ext_id,entity_id,entity_class,start,end,duration,category,action_dep

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(Action, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.id is None:
        self.id = 0
      if self.ext_id is None:
        self.ext_id = 0
      if self.entity_id is None:
        self.entity_id = []
      if self.entity_class is None:
        self.entity_class = []
      if self.start is None:
        self.start = 0
      if self.end is None:
        self.end = 0
      if self.duration is None:
        self.duration = 0
      if self.category is None:
        self.category = 0
      if self.action_dep is None:
        self.action_dep = []
    else:
      self.id = 0
      self.ext_id = 0
      self.entity_id = []
      self.entity_class = []
      self.start = 0
      self.end = 0
      self.duration = 0
      self.category = 0
      self.action_dep = []

  def _get_types(self):
    """
    internal API method
    """
    return self._slot_types

  def serialize(self, buff):
    """
    serialize message into buffer
    :param buff: buffer, ``StringIO``
    """
    try:
      _x = self
      buff.write(_get_struct_2I().pack(_x.id, _x.ext_id))
      length = len(self.entity_id)
      buff.write(_struct_I.pack(length))
      pattern = '<%sQ'%length
      buff.write(struct.Struct(pattern).pack(*self.entity_id))
      length = len(self.entity_class)
      buff.write(_struct_I.pack(length))
      pattern = '<%sI'%length
      buff.write(struct.Struct(pattern).pack(*self.entity_class))
      _x = self
      buff.write(_get_struct_3QI().pack(_x.start, _x.end, _x.duration, _x.category))
      length = len(self.action_dep)
      buff.write(_struct_I.pack(length))
      pattern = '<%sI'%length
      buff.write(struct.Struct(pattern).pack(*self.action_dep))
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize(self, str):
    """
    unpack serialized message in str into this message instance
    :param str: byte array of serialized message, ``str``
    """
    if python3:
      codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      end = 0
      _x = self
      start = end
      end += 8
      (_x.id, _x.ext_id,) = _get_struct_2I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sQ'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.entity_id = s.unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sI'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.entity_class = s.unpack(str[start:end])
      _x = self
      start = end
      end += 28
      (_x.start, _x.end, _x.duration, _x.category,) = _get_struct_3QI().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sI'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.action_dep = s.unpack(str[start:end])
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill


  def serialize_numpy(self, buff, numpy):
    """
    serialize message with numpy array types into buffer
    :param buff: buffer, ``StringIO``
    :param numpy: numpy python module
    """
    try:
      _x = self
      buff.write(_get_struct_2I().pack(_x.id, _x.ext_id))
      length = len(self.entity_id)
      buff.write(_struct_I.pack(length))
      pattern = '<%sQ'%length
      buff.write(self.entity_id.tostring())
      length = len(self.entity_class)
      buff.write(_struct_I.pack(length))
      pattern = '<%sI'%length
      buff.write(self.entity_class.tostring())
      _x = self
      buff.write(_get_struct_3QI().pack(_x.start, _x.end, _x.duration, _x.category))
      length = len(self.action_dep)
      buff.write(_struct_I.pack(length))
      pattern = '<%sI'%length
      buff.write(self.action_dep.tostring())
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize_numpy(self, str, numpy):
    """
    unpack serialized message in str into this message instance using numpy for array types
    :param str: byte array of serialized message, ``str``
    :param numpy: numpy python module
    """
    if python3:
      codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      end = 0
      _x = self
      start = end
      end += 8
      (_x.id, _x.ext_id,) = _get_struct_2I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sQ'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.entity_id = numpy.frombuffer(str[start:end], dtype=numpy.uint64, count=length)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sI'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.entity_class = numpy.frombuffer(str[start:end], dtype=numpy.uint32, count=length)
      _x = self
      start = end
      end += 28
      (_x.start, _x.end, _x.duration, _x.category,) = _get_struct_3QI().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sI'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.action_dep = numpy.frombuffer(str[start:end], dtype=numpy.uint32, count=length)
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill

_struct_I = genpy.struct_I
def _get_struct_I():
    global _struct_I
    return _struct_I
_struct_2I = None
def _get_struct_2I():
    global _struct_2I
    if _struct_2I is None:
        _struct_2I = struct.Struct("<2I")
    return _struct_2I
_struct_3QI = None
def _get_struct_3QI():
    global _struct_3QI
    if _struct_3QI is None:
        _struct_3QI = struct.Struct("<3QI")
    return _struct_3QI
