# This Python file uses the following encoding: utf-8
"""autogenerated by genpy from digitaleye_msgs/ComponentState.msg. Do not edit."""
import codecs
import sys
python3 = True if sys.hexversion > 0x03000000 else False
import genpy
import struct

import digitaleye_msgs.msg
import geometry_msgs.msg
import sensor_msgs.msg
import std_msgs.msg

class ComponentState(genpy.Message):
  _md5sum = "ed3ae0629002089e5901fb2f69befd77"
  _type = "digitaleye_msgs/ComponentState"
  _has_header = False  # flag to mark the presence of a Header object
  _full_text = """# State of a system component and its attached sensor(s)

# state of the component
digitaleye_msgs/State component

# state(s) of the component’s attached sensor(s)
digitaleye_msgs/Sensor[] sensors

================================================================================
MSG: digitaleye_msgs/State
# Details of a system’s status

# unique identifier of the system
# whose status is being reported
uint32 id

# system’s current state within the 
# DigitalEye state machine
uint32 state

# system’s substatus within the current state,
# unique to each system
uint32 status

# description of the system’s current state/status
string description

# timestamp indicating last change in state or status
# (epoch time in sec)
uint32 lastChange

# list of performance metrics associated with the
# current state
digitaleye_msgs/Metric[] metrics

================================================================================
MSG: digitaleye_msgs/Metric
# Performance indicator for a subsystem,
# component or sensor

# name of the performance indicator
string name

# value of the performance indicator
string value

================================================================================
MSG: digitaleye_msgs/Sensor
# Description of a monitoring DigitalEye sensor
# and its properties

# unique identifier of the sensor
# e.g. hardware serial number
string sensor_id

# brand/model of sensor hardware
string model

# type of sensor being described
# e.g. camera, LIDAR, etc.
uint32 type

# position of the sensor in
# the DigitalEye’s local reference frame (meters)
geometry_msgs/Pose pose

# direction in which the sensor is facing
# with respect to the local frame’s x-axis
float32 azimuth

# resolution height of the image captured by the sensor
uint32 image_width

# resolution width of the image captured by the sensor
uint32 image_height

# frame rate of a vision sensor
uint32 frame_rate

# sensor’s current power level
float32 power

# Whether or not the sensor has been calibrated
bool calibrated

# current state of the sensor
digitaleye_msgs/State state

# Sensor inertial measurements
digitaleye_msgs/IMUValue imu

================================================================================
MSG: geometry_msgs/Pose
# A representation of pose in free space, composed of position and orientation. 
Point position
Quaternion orientation

================================================================================
MSG: geometry_msgs/Point
# This contains the position of a point in free space
float64 x
float64 y
float64 z

================================================================================
MSG: geometry_msgs/Quaternion
# This represents an orientation in free space in quaternion form.

float64 x
float64 y
float64 z
float64 w

================================================================================
MSG: digitaleye_msgs/IMUValue
# Description of an IMU value reading

# Imu heading
float32 heading

# Unique identifier of the sensor
# e.g. hardware serial number
string device_id

# Imu measurements
sensor_msgs/Imu imu

# Magenetometer readings
geometry_msgs/Vector3 magnetic_field

# Imu reading of roll
float32 roll

# Imu reading of pitch
float32 pitch

# Calibration status
bool deviceCalibrated

================================================================================
MSG: sensor_msgs/Imu
# This is a message to hold data from an IMU (Inertial Measurement Unit)
#
# Accelerations should be in m/s^2 (not in g's), and rotational velocity should be in rad/sec
#
# If the covariance of the measurement is known, it should be filled in (if all you know is the 
# variance of each measurement, e.g. from the datasheet, just put those along the diagonal)
# A covariance matrix of all zeros will be interpreted as "covariance unknown", and to use the
# data a covariance will have to be assumed or gotten from some other source
#
# If you have no estimate for one of the data elements (e.g. your IMU doesn't produce an orientation 
# estimate), please set element 0 of the associated covariance matrix to -1
# If you are interpreting this message, please check for a value of -1 in the first element of each 
# covariance matrix, and disregard the associated estimate.

Header header

geometry_msgs/Quaternion orientation
float64[9] orientation_covariance # Row major about x, y, z axes

geometry_msgs/Vector3 angular_velocity
float64[9] angular_velocity_covariance # Row major about x, y, z axes

geometry_msgs/Vector3 linear_acceleration
float64[9] linear_acceleration_covariance # Row major x, y z 

================================================================================
MSG: std_msgs/Header
# Standard metadata for higher-level stamped data types.
# This is generally used to communicate timestamped data 
# in a particular coordinate frame.
# 
# sequence ID: consecutively increasing ID 
uint32 seq
#Two-integer timestamp that is expressed as:
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')
# time-handling sugar is provided by the client library
time stamp
#Frame this data is associated with
string frame_id

================================================================================
MSG: geometry_msgs/Vector3
# This represents a vector in free space. 
# It is only meant to represent a direction. Therefore, it does not
# make sense to apply a translation to it (e.g., when applying a 
# generic rigid transformation to a Vector3, tf2 will only apply the
# rotation). If you want your data to be translatable too, use the
# geometry_msgs/Point message instead.

float64 x
float64 y
float64 z"""
  __slots__ = ['component','sensors']
  _slot_types = ['digitaleye_msgs/State','digitaleye_msgs/Sensor[]']

  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       component,sensors

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(ComponentState, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.component is None:
        self.component = digitaleye_msgs.msg.State()
      if self.sensors is None:
        self.sensors = []
    else:
      self.component = digitaleye_msgs.msg.State()
      self.sensors = []

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
      buff.write(_get_struct_3I().pack(_x.component.id, _x.component.state, _x.component.status))
      _x = self.component.description
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self.component.lastChange
      buff.write(_get_struct_I().pack(_x))
      length = len(self.component.metrics)
      buff.write(_struct_I.pack(length))
      for val1 in self.component.metrics:
        _x = val1.name
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = val1.value
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      length = len(self.sensors)
      buff.write(_struct_I.pack(length))
      for val1 in self.sensors:
        _x = val1.sensor_id
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = val1.model
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = val1.type
        buff.write(_get_struct_I().pack(_x))
        _v1 = val1.pose
        _v2 = _v1.position
        _x = _v2
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        _v3 = _v1.orientation
        _x = _v3
        buff.write(_get_struct_4d().pack(_x.x, _x.y, _x.z, _x.w))
        _x = val1
        buff.write(_get_struct_f3IfB().pack(_x.azimuth, _x.image_width, _x.image_height, _x.frame_rate, _x.power, _x.calibrated))
        _v4 = val1.state
        _x = _v4
        buff.write(_get_struct_3I().pack(_x.id, _x.state, _x.status))
        _x = _v4.description
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = _v4.lastChange
        buff.write(_get_struct_I().pack(_x))
        length = len(_v4.metrics)
        buff.write(_struct_I.pack(length))
        for val3 in _v4.metrics:
          _x = val3.name
          length = len(_x)
          if python3 or type(_x) == unicode:
            _x = _x.encode('utf-8')
            length = len(_x)
          buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
          _x = val3.value
          length = len(_x)
          if python3 or type(_x) == unicode:
            _x = _x.encode('utf-8')
            length = len(_x)
          buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _v5 = val1.imu
        _x = _v5.heading
        buff.write(_get_struct_f().pack(_x))
        _x = _v5.device_id
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _v6 = _v5.imu
        _v7 = _v6.header
        _x = _v7.seq
        buff.write(_get_struct_I().pack(_x))
        _v8 = _v7.stamp
        _x = _v8
        buff.write(_get_struct_2I().pack(_x.secs, _x.nsecs))
        _x = _v7.frame_id
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _v9 = _v6.orientation
        _x = _v9
        buff.write(_get_struct_4d().pack(_x.x, _x.y, _x.z, _x.w))
        buff.write(_get_struct_9d().pack(*_v6.orientation_covariance))
        _v10 = _v6.angular_velocity
        _x = _v10
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        buff.write(_get_struct_9d().pack(*_v6.angular_velocity_covariance))
        _v11 = _v6.linear_acceleration
        _x = _v11
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        buff.write(_get_struct_9d().pack(*_v6.linear_acceleration_covariance))
        _v12 = _v5.magnetic_field
        _x = _v12
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        _x = _v5
        buff.write(_get_struct_2fB().pack(_x.roll, _x.pitch, _x.deviceCalibrated))
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
      if self.component is None:
        self.component = digitaleye_msgs.msg.State()
      if self.sensors is None:
        self.sensors = None
      end = 0
      _x = self
      start = end
      end += 12
      (_x.component.id, _x.component.state, _x.component.status,) = _get_struct_3I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.component.description = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.component.description = str[start:end]
      start = end
      end += 4
      (self.component.lastChange,) = _get_struct_I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      self.component.metrics = []
      for i in range(0, length):
        val1 = digitaleye_msgs.msg.Metric()
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.name = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.name = str[start:end]
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.value = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.value = str[start:end]
        self.component.metrics.append(val1)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      self.sensors = []
      for i in range(0, length):
        val1 = digitaleye_msgs.msg.Sensor()
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.sensor_id = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.sensor_id = str[start:end]
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.model = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.model = str[start:end]
        start = end
        end += 4
        (val1.type,) = _get_struct_I().unpack(str[start:end])
        _v13 = val1.pose
        _v14 = _v13.position
        _x = _v14
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        _v15 = _v13.orientation
        _x = _v15
        start = end
        end += 32
        (_x.x, _x.y, _x.z, _x.w,) = _get_struct_4d().unpack(str[start:end])
        _x = val1
        start = end
        end += 21
        (_x.azimuth, _x.image_width, _x.image_height, _x.frame_rate, _x.power, _x.calibrated,) = _get_struct_f3IfB().unpack(str[start:end])
        val1.calibrated = bool(val1.calibrated)
        _v16 = val1.state
        _x = _v16
        start = end
        end += 12
        (_x.id, _x.state, _x.status,) = _get_struct_3I().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          _v16.description = str[start:end].decode('utf-8', 'rosmsg')
        else:
          _v16.description = str[start:end]
        start = end
        end += 4
        (_v16.lastChange,) = _get_struct_I().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        _v16.metrics = []
        for i in range(0, length):
          val3 = digitaleye_msgs.msg.Metric()
          start = end
          end += 4
          (length,) = _struct_I.unpack(str[start:end])
          start = end
          end += length
          if python3:
            val3.name = str[start:end].decode('utf-8', 'rosmsg')
          else:
            val3.name = str[start:end]
          start = end
          end += 4
          (length,) = _struct_I.unpack(str[start:end])
          start = end
          end += length
          if python3:
            val3.value = str[start:end].decode('utf-8', 'rosmsg')
          else:
            val3.value = str[start:end]
          _v16.metrics.append(val3)
        _v17 = val1.imu
        start = end
        end += 4
        (_v17.heading,) = _get_struct_f().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          _v17.device_id = str[start:end].decode('utf-8', 'rosmsg')
        else:
          _v17.device_id = str[start:end]
        _v18 = _v17.imu
        _v19 = _v18.header
        start = end
        end += 4
        (_v19.seq,) = _get_struct_I().unpack(str[start:end])
        _v20 = _v19.stamp
        _x = _v20
        start = end
        end += 8
        (_x.secs, _x.nsecs,) = _get_struct_2I().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          _v19.frame_id = str[start:end].decode('utf-8', 'rosmsg')
        else:
          _v19.frame_id = str[start:end]
        _v21 = _v18.orientation
        _x = _v21
        start = end
        end += 32
        (_x.x, _x.y, _x.z, _x.w,) = _get_struct_4d().unpack(str[start:end])
        start = end
        end += 72
        _v18.orientation_covariance = _get_struct_9d().unpack(str[start:end])
        _v22 = _v18.angular_velocity
        _x = _v22
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        start = end
        end += 72
        _v18.angular_velocity_covariance = _get_struct_9d().unpack(str[start:end])
        _v23 = _v18.linear_acceleration
        _x = _v23
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        start = end
        end += 72
        _v18.linear_acceleration_covariance = _get_struct_9d().unpack(str[start:end])
        _v24 = _v17.magnetic_field
        _x = _v24
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        _x = _v17
        start = end
        end += 9
        (_x.roll, _x.pitch, _x.deviceCalibrated,) = _get_struct_2fB().unpack(str[start:end])
        _v17.deviceCalibrated = bool(_v17.deviceCalibrated)
        self.sensors.append(val1)
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
      buff.write(_get_struct_3I().pack(_x.component.id, _x.component.state, _x.component.status))
      _x = self.component.description
      length = len(_x)
      if python3 or type(_x) == unicode:
        _x = _x.encode('utf-8')
        length = len(_x)
      buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      _x = self.component.lastChange
      buff.write(_get_struct_I().pack(_x))
      length = len(self.component.metrics)
      buff.write(_struct_I.pack(length))
      for val1 in self.component.metrics:
        _x = val1.name
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = val1.value
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
      length = len(self.sensors)
      buff.write(_struct_I.pack(length))
      for val1 in self.sensors:
        _x = val1.sensor_id
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = val1.model
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = val1.type
        buff.write(_get_struct_I().pack(_x))
        _v25 = val1.pose
        _v26 = _v25.position
        _x = _v26
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        _v27 = _v25.orientation
        _x = _v27
        buff.write(_get_struct_4d().pack(_x.x, _x.y, _x.z, _x.w))
        _x = val1
        buff.write(_get_struct_f3IfB().pack(_x.azimuth, _x.image_width, _x.image_height, _x.frame_rate, _x.power, _x.calibrated))
        _v28 = val1.state
        _x = _v28
        buff.write(_get_struct_3I().pack(_x.id, _x.state, _x.status))
        _x = _v28.description
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _x = _v28.lastChange
        buff.write(_get_struct_I().pack(_x))
        length = len(_v28.metrics)
        buff.write(_struct_I.pack(length))
        for val3 in _v28.metrics:
          _x = val3.name
          length = len(_x)
          if python3 or type(_x) == unicode:
            _x = _x.encode('utf-8')
            length = len(_x)
          buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
          _x = val3.value
          length = len(_x)
          if python3 or type(_x) == unicode:
            _x = _x.encode('utf-8')
            length = len(_x)
          buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _v29 = val1.imu
        _x = _v29.heading
        buff.write(_get_struct_f().pack(_x))
        _x = _v29.device_id
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _v30 = _v29.imu
        _v31 = _v30.header
        _x = _v31.seq
        buff.write(_get_struct_I().pack(_x))
        _v32 = _v31.stamp
        _x = _v32
        buff.write(_get_struct_2I().pack(_x.secs, _x.nsecs))
        _x = _v31.frame_id
        length = len(_x)
        if python3 or type(_x) == unicode:
          _x = _x.encode('utf-8')
          length = len(_x)
        buff.write(struct.Struct('<I%ss'%length).pack(length, _x))
        _v33 = _v30.orientation
        _x = _v33
        buff.write(_get_struct_4d().pack(_x.x, _x.y, _x.z, _x.w))
        buff.write(_v30.orientation_covariance.tostring())
        _v34 = _v30.angular_velocity
        _x = _v34
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        buff.write(_v30.angular_velocity_covariance.tostring())
        _v35 = _v30.linear_acceleration
        _x = _v35
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        buff.write(_v30.linear_acceleration_covariance.tostring())
        _v36 = _v29.magnetic_field
        _x = _v36
        buff.write(_get_struct_3d().pack(_x.x, _x.y, _x.z))
        _x = _v29
        buff.write(_get_struct_2fB().pack(_x.roll, _x.pitch, _x.deviceCalibrated))
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
      if self.component is None:
        self.component = digitaleye_msgs.msg.State()
      if self.sensors is None:
        self.sensors = None
      end = 0
      _x = self
      start = end
      end += 12
      (_x.component.id, _x.component.state, _x.component.status,) = _get_struct_3I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      start = end
      end += length
      if python3:
        self.component.description = str[start:end].decode('utf-8', 'rosmsg')
      else:
        self.component.description = str[start:end]
      start = end
      end += 4
      (self.component.lastChange,) = _get_struct_I().unpack(str[start:end])
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      self.component.metrics = []
      for i in range(0, length):
        val1 = digitaleye_msgs.msg.Metric()
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.name = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.name = str[start:end]
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.value = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.value = str[start:end]
        self.component.metrics.append(val1)
      start = end
      end += 4
      (length,) = _struct_I.unpack(str[start:end])
      self.sensors = []
      for i in range(0, length):
        val1 = digitaleye_msgs.msg.Sensor()
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.sensor_id = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.sensor_id = str[start:end]
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          val1.model = str[start:end].decode('utf-8', 'rosmsg')
        else:
          val1.model = str[start:end]
        start = end
        end += 4
        (val1.type,) = _get_struct_I().unpack(str[start:end])
        _v37 = val1.pose
        _v38 = _v37.position
        _x = _v38
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        _v39 = _v37.orientation
        _x = _v39
        start = end
        end += 32
        (_x.x, _x.y, _x.z, _x.w,) = _get_struct_4d().unpack(str[start:end])
        _x = val1
        start = end
        end += 21
        (_x.azimuth, _x.image_width, _x.image_height, _x.frame_rate, _x.power, _x.calibrated,) = _get_struct_f3IfB().unpack(str[start:end])
        val1.calibrated = bool(val1.calibrated)
        _v40 = val1.state
        _x = _v40
        start = end
        end += 12
        (_x.id, _x.state, _x.status,) = _get_struct_3I().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          _v40.description = str[start:end].decode('utf-8', 'rosmsg')
        else:
          _v40.description = str[start:end]
        start = end
        end += 4
        (_v40.lastChange,) = _get_struct_I().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        _v40.metrics = []
        for i in range(0, length):
          val3 = digitaleye_msgs.msg.Metric()
          start = end
          end += 4
          (length,) = _struct_I.unpack(str[start:end])
          start = end
          end += length
          if python3:
            val3.name = str[start:end].decode('utf-8', 'rosmsg')
          else:
            val3.name = str[start:end]
          start = end
          end += 4
          (length,) = _struct_I.unpack(str[start:end])
          start = end
          end += length
          if python3:
            val3.value = str[start:end].decode('utf-8', 'rosmsg')
          else:
            val3.value = str[start:end]
          _v40.metrics.append(val3)
        _v41 = val1.imu
        start = end
        end += 4
        (_v41.heading,) = _get_struct_f().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          _v41.device_id = str[start:end].decode('utf-8', 'rosmsg')
        else:
          _v41.device_id = str[start:end]
        _v42 = _v41.imu
        _v43 = _v42.header
        start = end
        end += 4
        (_v43.seq,) = _get_struct_I().unpack(str[start:end])
        _v44 = _v43.stamp
        _x = _v44
        start = end
        end += 8
        (_x.secs, _x.nsecs,) = _get_struct_2I().unpack(str[start:end])
        start = end
        end += 4
        (length,) = _struct_I.unpack(str[start:end])
        start = end
        end += length
        if python3:
          _v43.frame_id = str[start:end].decode('utf-8', 'rosmsg')
        else:
          _v43.frame_id = str[start:end]
        _v45 = _v42.orientation
        _x = _v45
        start = end
        end += 32
        (_x.x, _x.y, _x.z, _x.w,) = _get_struct_4d().unpack(str[start:end])
        start = end
        end += 72
        _v42.orientation_covariance = numpy.frombuffer(str[start:end], dtype=numpy.float64, count=9)
        _v46 = _v42.angular_velocity
        _x = _v46
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        start = end
        end += 72
        _v42.angular_velocity_covariance = numpy.frombuffer(str[start:end], dtype=numpy.float64, count=9)
        _v47 = _v42.linear_acceleration
        _x = _v47
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        start = end
        end += 72
        _v42.linear_acceleration_covariance = numpy.frombuffer(str[start:end], dtype=numpy.float64, count=9)
        _v48 = _v41.magnetic_field
        _x = _v48
        start = end
        end += 24
        (_x.x, _x.y, _x.z,) = _get_struct_3d().unpack(str[start:end])
        _x = _v41
        start = end
        end += 9
        (_x.roll, _x.pitch, _x.deviceCalibrated,) = _get_struct_2fB().unpack(str[start:end])
        _v41.deviceCalibrated = bool(_v41.deviceCalibrated)
        self.sensors.append(val1)
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
_struct_2fB = None
def _get_struct_2fB():
    global _struct_2fB
    if _struct_2fB is None:
        _struct_2fB = struct.Struct("<2fB")
    return _struct_2fB
_struct_3I = None
def _get_struct_3I():
    global _struct_3I
    if _struct_3I is None:
        _struct_3I = struct.Struct("<3I")
    return _struct_3I
_struct_3d = None
def _get_struct_3d():
    global _struct_3d
    if _struct_3d is None:
        _struct_3d = struct.Struct("<3d")
    return _struct_3d
_struct_4d = None
def _get_struct_4d():
    global _struct_4d
    if _struct_4d is None:
        _struct_4d = struct.Struct("<4d")
    return _struct_4d
_struct_9d = None
def _get_struct_9d():
    global _struct_9d
    if _struct_9d is None:
        _struct_9d = struct.Struct("<9d")
    return _struct_9d
_struct_f = None
def _get_struct_f():
    global _struct_f
    if _struct_f is None:
        _struct_f = struct.Struct("<f")
    return _struct_f
_struct_f3IfB = None
def _get_struct_f3IfB():
    global _struct_f3IfB
    if _struct_f3IfB is None:
        _struct_f3IfB = struct.Struct("<f3IfB")
    return _struct_f3IfB
