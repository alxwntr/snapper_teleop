from    geometry_msgs.msg       import Twist
from    geometry_msgs.msg       import Vector3
import  rospy

from    . import actions as act

# Grr python2 rubbish
__metaclass__ = type

class TwistController:
    __slots__ = ["speed", "turn"]

    def __init__ (self):
        # XXX These need adjusting. The numbers are:
        #   initial value
        #   step applied by e.g. pressing W
        #   adjustment to step e.g. by pressing arrows
        #   max value
        # 2.0 seems rather high for turn?
        self.speed  = act.ControlPoint(0, 0.4, 0.1, 4.0)
        self.turn   = act.ControlPoint(0, 2.0, 0.5, 6.0)

    def stop (self):
        self.speed.value    = 0
        self.turn.value     = 0

    def handle_action (self, action):
        if isinstance(action, act.Stop):
            self.stop()

        elif isinstance(action, act.Control):
            if action.axis == "speed":
                action.apply(self.speed)

            elif action.axis == "turn":
                action.apply(self.turn)

        else:
            throw(RuntimeError("Bad action " + action))

    def to_twist (self):
        return Twist(
            linear=Vector3(self.speed.value, 0, 0),
            angular=Vector3(0, 0, self.turn.value),
        )

def wait_for_subscribers(pub):
    i = 0
    while not rospy.is_shutdown() and pub.get_num_connections() == 0:
        if i == 4:
            print("Waiting for subscriber to connect to {}".format(pub.name))
        rospy.sleep(0.5)
        i += 1
        i = i % 5
    if rospy.is_shutdown():
        raise Exception("Got shutdown request before subscribers connected")

def run (win):
    win.setup()

    pub = rospy.Publisher('demand_out', Twist, queue_size=1)
    rospy.init_node('pub')

    rate    = rospy.Rate(5)
    state   = TwistController()

    try:
        wait_for_subscribers(pub)

        running = True

        while not rospy.is_shutdown() and running:

            for action in win.get_actions():
                if isinstance(action, act.Quit):
                    state.stop()
                    print("Exiting program")
                    running = False
                else:
                    state.handle_action(action)

            win.draw(state)

            win.update()
            pub.publish(state.to_twist())
            rate.sleep()
    finally:
        win.quit()
        pub.publish(Twist(Vector3(0, 0, 0), Vector3(0, 0, 0)))

