import  os
from    __future__      import division
import  pygame

# Grr python2 rubbish
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


# Colours
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (80,  80,  80)
RED     = (240, 0,   0)
YELLOW  = (240, 240, 0)


# This implements the pygame interface. This can handle key-up events,
# so the motors stop as soon as you release the key. It create a tiny
# window just to accept events.
class PygameInterface:
    keydown = {
        pygame.K_ESCAPE:        act.Quit(),
        pygame.K_SPACE:         act.Stop(),
    }

    key_axis = (
        axis.DigitalAxis(axis="speed",
            plus=pygame.K_w, minus=pygame.K_s,
            more=pygame.K_UP, less=pygame.K_DOWN,
        ),
        axis.DigitalAxis(axis="turn",
            plus=pygame.K_d, minus=pygame.K_a,
            more=pygame.K_RIGHT, less=pygame.K_LEFT,
        ),
    )

    joy_axis = {
        0:      axis.AnalogueAxis(axis="turn", scale=1.0),
        1:      axis.AnalogueAxis(axis="speed", scale=-1.0),
    }

    mouse_axis = (
        axis.AnalogueAxis(axis="turn", scale=1.0, dead=0.3),
        axis.AnalogueAxis(axis="speed", scale=-1.0, dead=0.3),
    )

    winsize = (400, 300)

    def __init__ (self):
        self.win        = None
        self.joy        = None
        self.mouse      = False

    def setup (self):
        self.setup_display()
        self.setup_joystick()

    def setup_display (self):
        pygame.display.init()
        self.win = pygame.display.set_mode(self.winsize)
        pygame.key.set_repeat(0)

    def setup_joystick (self):
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            return

        self.joy    = pygame.joystick.Joystick(0)
        self.joy.init()

    def quit (self):
        pygame.quit()

    def handle_joy_event (self, event, actions):
        if event.axis not in self.joy_axis:
            return
        axis    = self.joy_axis[event.axis]
        value   = event.value

    def handle_mouse_click (self):
        self.mouse = not self.mouse
        pygame.event.set_grab(self.mouse)
        pygame.mouse.set_visible(not self.mouse)

        if self.mouse:
            ws  = self.winsize
            pygame.mouse.set_pos(ws[0]/2, ws[1]/2)

    def handle_mouse_motion (self, pos):
        ws  = self.winsize
        rv  = []

        for i in 0, 1:
            sc  = ws[i]/2
            v   = (pos[i] - sc)/sc
            a   = self.mouse_axis[i].handle_value(v)
            rv.extend(a)

        return rv

    def get_actions (self):
        actions = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append(Action("quit"))

            if event.type == pygame.KEYDOWN:
                if event.key in self.keydown:
                    actions.append(self.keydown[event.key])
                else:
                    for a in self.key_axis:
                        actions.extend(a.handle_keydown(event.key))

            if event.type == pygame.KEYUP:
                for a in self.key_axis:
                    actions.extend(a.handle_keyup(event.key))

            if event.type == pygame.JOYAXISMOTION:
                if event.axis in self.joy_axis:
                    actions.extend(
                        self.joy_axis[event.axis].
                            handle_value(event.value))

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click()

            if event.type == pygame.MOUSEMOTION:
                if self.mouse:
                    actions.extend(
                        self.handle_mouse_motion(event.pos))

        return actions

    def puts (self, msg):
        print(msg)

    def draw (self, state):
        w   = self.win
        d   = pygame.draw
        sp  = state.speed.scale(100)
        sps = state.speed.scale_step(100)
        tr  = state.turn.scale(100)
        trs = state.turn.scale_step(100)

        w.fill(BLACK)

        d.rect(w, GRAY, [150-trs, 125, 2*trs, 50], 0)
        if tr > 0:
            d.rect(w, RED, [150, 125, tr, 50], 0)
        elif tr < 0:
            d.rect(w, RED, [150+tr, 125, -tr, 50], 0)
        d.rect(w, WHITE, [50, 125, 200, 50], 2)
        d.line(w, WHITE, [150, 125], [150, 175], 2)

        d.rect(w, GRAY, [300, 150-sps, 50, 2*sps], 0)
        if sp > 0:
            d.rect(w, RED, [300, 150-sp, 50, sp], 0)
        elif sp < 0:
            d.rect(w, RED, [300, 150, 50, -sp], 0)
        d.rect(w, WHITE, [300, 50, 50, 200], 2)
        d.line(w, WHITE, [300, 150], [350, 150], 2)


    def update (self):
        pygame.display.update()


def main():
    print("Using PyGame interface")
    win   = PygameInterface()

    run(win)

#Comment
if __name__ == '__main__':
    try:
        main()
    except:
        pass
