from    __future__  import division

__metaclass__ = type

def clamp (v, a, b):
    if v < a:
        return a
    if v > b:
        return b
    return v

# A ControlPoint is a value that can be changed by a control interface.
# It can take positive or negative values up to a certain maximum.
class ControlPoint:
    __slots__ = [
        "value",    # The current value of the control point
        "step",     # The size of a digital change
        "adj",      # The steps to change .step by
        "max",      # The maximim allowed value
    ]

    def __init__ (self, value, step, adjust, max):
        self.value  = value
        self.step   = step
        self.adj    = adjust
        self.max    = max

    # Return a scaled value
    def scale (self, sc):
        return (self.value / self.max) * sc

    def scale_step (self, sc):
        return (self.step / self.max) * sc

# An Action is a command sent from a control interface
class Action:
    pass

class Stop (Action):
    pass

class Quit (Action):
    pass

# A ControlAction is an adjustment to a ControlPoint.
# The value of a ControlAction is always in [-1,1].
class Control (Action):
    __slots__   = ["axis", "value"]

    def __init__ (self, axis, value, **kw):
        super(Control, self).__init__(**kw)
        self.axis       = axis
        self.value      = value

class Analogue (Control):
    def apply (self, point):
        point.value     = self.value * point.max

class Digital (Control):
    def apply (self, point):
        point.value     = self.value * point.step

class AbsAdjust (Control):
    def apply (self, point):
        point.step      = self.value * point.max

class RelAdjust (Control):
    def apply (self, point):
        st              = point.step + self.value * point.adj
        point.step      = clamp(st, 0, point.max)

