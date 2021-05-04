from __future__ import division
__metaclass__ = type

from    .   import actions as act

class Axis:
    __slots__   = ["axis", "value"]

    def __init__ (self, axis):
        self.axis   = axis
        self.value  = 0

class DigitalAxis (Axis):
    __slots__   = ["plus", "minus", "more", "less"]

    def __init__ (self, plus, minus, more, less, **kws):
        super(DigitalAxis, self).__init__(**kws)
        self.plus   = plus
        self.minus  = minus
        self.more   = more
        self.less   = less

    def mk_digital (self):
        return act.Digital(axis=self.axis, value=self.value)

    def mk_adjust (self, by):
        return act.RelAdjust(axis=self.axis, value=by)

    def handle_keydown (self, key):
        if key == self.plus:
            self.value  = 1
            return [self.mk_digital()]

        if key == self.minus:
            self.value  = -1
            return [self.mk_digital()]

        if key == self.more:
            return [self.mk_adjust(1), self.mk_digital()]

        if key == self.less:
            return [self.mk_adjust(-1), self.mk_digital()]

        return []

    def handle_keyup (self, key):
        if key == self.plus and self.value == 1:
            self.value  = 0
            return [self.mk_digital()]

        elif key == self.minus and self.value == -1:
            self.value  = 0
            return [self.mk_digital()]

        return []

class AnalogueAxis (Axis):
    __slots__   = ["scale", "dead"]

    def __init__ (self, scale=1.0, dead=0.1, **kws):
        super(AnalogueAxis, self).__init__(**kws)
        self.scale  = scale / (1.0 - dead)
        self.dead   = dead

    def handle_value (self, value):
        if value < self.dead and value > -self.dead:
            value   = 0.0
        else:
            if value > 0:
                value   = value - self.dead
            else:
                value   = value + self.dead
            value   = round(value * self.scale, 3)

        if value == self.value:
            return []
        self.value  = value

        return [act.Analogue(axis=self.axis, value=value)]

