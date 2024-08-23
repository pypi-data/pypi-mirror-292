# This Python file uses the following encoding: utf-8
"""autogenerated by genpy from digitaleye_msgs/VehicleCommand.msg. Do not edit."""
import codecs
import sys
python3 = True if sys.hexversion > 0x03000000 else False
import genpy
import struct


class VehicleCommand(genpy.Message):
  _md5sum = "e4eb8780a2cbe5090cabe2da1ec18573"
  _type = "digitaleye_msgs/VehicleCommand"
  _has_header = False  # flag to mark the presence of a Header object
  _full_text = """# definition of vehicle commands

# The command, CMD_, see below
uint32 command

# Command
uint32 CMD_GOTO=0
uint32 CMD_TAKEOFF=1
uint32 CMD_LAND=2
uint32 CMD_STOP=3
uint32 CMD_CHANGE_YAW=4
uint32 CMD_CHANGE_SPEED=5
uint32 CMD_JUMP_CMD=6

# Parameters of the command
uint32 delay # delay of the command in second, mostly useful for missions
uint32[] int_param
float64[] float_param

## GOTO: Frame, use FRAME_; yaw angle in degrees, see specified frame;
## x, y, z see specified frame; ground speed m/s
# GOTO int parameters
uint32 GOTO_INT_FRAME=0
uint32 GOTO_INT_YAW=1
uint32 GOTO_INT_PARAM_SIZE=2
# GOTO float parameters
uint32 GOTO_FLOAT_X=0
uint32 GOTO_FLOAT_Y=1
uint32 GOTO_FLOAT_Z=2
uint32 GOTO_FLOAT_SPEED=3
uint32 GOTO_FLOAT_PARAM_SIZE=4

## TAKEOFF: Frame, use FRAME_; yaw angle in degrees, see specified frame;
## z see specified frame; vertical speed m/s
# TAKEOFF int parameters
uint32 TAKEOFF_INT_FRAME=0
uint32 TAKEOFF_INT_YAW=1
uint32 TAKEOFF_INT_PARAM_SIZE=2
# TAKEOFF float parameters
uint32 TAKEOFF_FLOAT_Z=0
uint32 TAKEOFF_FLOAT_SPEED=1
uint32 TAKEOFF_FLOAT_PARAM_SIZE=2

## LAND: no parameters

## STOP: no parameters

## CHANGE_YAW: Frame, use YAW_FRAME_; yaw angle in degrees, see specified frame; speed deg/s
# CHANGE_YAW int parameters
uint32 CHANGE_YAW_INT_FRAME=0
uint32 CHANGE_YAW_INT_YAW=1
uint32 CHANGE_YAW_INT_SPEED=2
uint32 CHANGE_YAW_INT_PARAM_SIZE=3

## CHANGE_SPEED: ground speed in m/s
# TAKEOFF float parameters
uint32 CHANGE_SPEED_FLOAT_Z=0
uint32 CHANGE_SPEED_FLOAT_PARAM_SIZE=1

## JUMP_CMD: Command number to jump to; repeat giving the number of repeats
# JUMP_CMD int parameters
uint32 JUMP_CMD_INT_CMD_NB=0
uint32 JUMP_CMD_INT_REPEAT=1
uint32 JUMP_CMD_INT_PARAM_SIZE=2

## FRAME:
uint32 FRAME_PORTAL = 0 # Portal coordinate frame, coordinates in m, absolute yaw (-1 to not specify)
uint32 FRAME_GLOBAL = 1 # WGS84 coordinate frame (deg) + MSL altitude (m), absolute yaw (-1 to not specify)
uint32 FRAME_FRD = 2 # FRD local frame, x: Forward, y: Right, z: Down (m), relative yaw

"""
  # Pseudo-constants
  CMD_GOTO = 0
  CMD_TAKEOFF = 1
  CMD_LAND = 2
  CMD_STOP = 3
  CMD_CHANGE_YAW = 4
  CMD_CHANGE_SPEED = 5
  CMD_JUMP_CMD = 6
  GOTO_INT_FRAME = 0
  GOTO_INT_YAW = 1
  GOTO_INT_PARAM_SIZE = 2
  GOTO_FLOAT_X = 0
  GOTO_FLOAT_Y = 1
  GOTO_FLOAT_Z = 2
  GOTO_FLOAT_SPEED = 3
  GOTO_FLOAT_PARAM_SIZE = 4
  TAKEOFF_INT_FRAME = 0
  TAKEOFF_INT_YAW = 1
  TAKEOFF_INT_PARAM_SIZE = 2
  TAKEOFF_FLOAT_Z = 0
  TAKEOFF_FLOAT_SPEED = 1
  TAKEOFF_FLOAT_PARAM_SIZE = 2
  CHANGE_YAW_INT_FRAME = 0
  CHANGE_YAW_INT_YAW = 1
  CHANGE_YAW_INT_SPEED = 2
  CHANGE_YAW_INT_PARAM_SIZE = 3
  CHANGE_SPEED_FLOAT_Z = 0
  CHANGE_SPEED_FLOAT_PARAM_SIZE = 1
  JUMP_CMD_INT_CMD_NB = 0
  JUMP_CMD_INT_REPEAT = 1
  JUMP_CMD_INT_PARAM_SIZE = 2
  FRAME_PORTAL = 0
  FRAME_GLOBAL = 1
  FRAME_FRD = 2

  __slots__ = ['command','delay','int_param','float_param']
  _slot_types = ['uint32','uint32','uint32[]','float64[]']

  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       command,delay,int_param,float_param

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(VehicleCommand, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.command is None:
        self.command = 0
      if self.delay is None:
        self.delay = 0
      if self.int_param is None:
        self.int_param = []
      if self.float_param is None:
        self.float_param = []
    else:
      self.command = 0
      self.delay = 0
      self.int_param = []
      self.float_param = []

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
      buff.write(_get_struct_2I().pack(_x.command, _x.delay))
      length = len(self.int_param)
      buff.write(_struct_I.pack(length))
      pattern = '<%sI'%length
      buff.write(struct.Struct(pattern).pack(*self.int_param))
      length = len(self.float_param)
      buff.write(_struct_I.pack(length))
      pattern = '<%sd'%length
      buff.write(struct.Struct(pattern).pack(*self.float_param))
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
      (_x.command, _x.delay,) = _get_struct_2I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sI'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.int_param = s.unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sd'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.float_param = s.unpack(str[start:end])
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
      buff.write(_get_struct_2I().pack(_x.command, _x.delay))
      length = len(self.int_param)
      buff.write(_struct_I.pack(length))
      pattern = '<%sI'%length
      buff.write(self.int_param.tostring())
      length = len(self.float_param)
      buff.write(_struct_I.pack(length))
      pattern = '<%sd'%length
      buff.write(self.float_param.tostring())
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
      (_x.command, _x.delay,) = _get_struct_2I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sI'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.int_param = numpy.frombuffer(str[start:end], dtype=numpy.uint32, count=length)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      pattern = '<%sd'%length
      start = end
      s = struct.Struct(pattern)
      end += s.size
      self.float_param = numpy.frombuffer(str[start:end], dtype=numpy.float64, count=length)
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
