#!/usr/bin/env python

import rospy
from conveyor.msg import Conveyor
import sys, select, os
if os.name == 'nt':
  import msvcrt, time
else:
  import tty, termios

CONVEYOR_MAX_VEL = 100
VEL_STEP_SIZE = 1

msg = """
Control Your TurtleBot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease velocity 
a/d : change direction

space key, s : force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""

def getKey():
    if os.name == 'nt':
        timeout = 0.1
        startTime = time.time()
        while(1):
            if msvcrt.kbhit():
                if sys.version_info[0] >= 3:
                    return msvcrt.getch().decode()
                else:
                    return msvcrt.getch()
            elif time.time() - startTime > timeout:
                return ''

    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(target_vel):
    return "currently:\tvel %s " % target_vel


def constrain(input, low, high):
    if input < low:
      input = low
    elif input > high:
      input = high
    else:
      input = input

    return input

def checkLinearLimitVelocity(vel):
    vel = constrain(vel, -CONVEYOR_MAX_VEL, CONVEYOR_MAX_VEL)

    return vel


if __name__=="__main__":
    if os.name != 'nt':
        settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('conveyor_teleop')
    pub = rospy.Publisher('/conveyor/speed', Conveyor, queue_size=10)

    vel   = 0
    status = 0

    try:
        print(msg)
        while not rospy.is_shutdown():
            key = getKey()
            if key == 'w' :
                vel = checkLinearLimitVelocity(vel + VEL_STEP_SIZE)
                status = status + 1
                print(vels(vel))
            elif key == 'x' :
                vel = checkLinearLimitVelocity(vel - VEL_STEP_SIZE)
                status = status + 1
                print(vels(vel))
            elif key == 'a' :
                vel = checkLinearLimitVelocity( -abs(vel) )
                status = status + 1
                print(vels(vel))
            elif key == 'd' :
                vel = checkLinearLimitVelocity( abs(vel) )
                status = status + 1
                print(vels(vel))
            elif key == ' ' or key == 's' :
                vel   = 0
                print(vels(vel))
            else:
                if (key == '\x03'):
                    break

            if status == 20 :
                print(msg)
                status = 0



            cnvyr = Conveyor()
            cnvyr.speed = vel

            pub.publish(cnvyr)

    except:
        print(e)

    finally:
        cnvyr = Conveyor()
        cnvyr.speed = 0
        pub.publish(cnvyr)

    if os.name != 'nt':
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)