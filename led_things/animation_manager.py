# an animation will specify:
#	what color components it will act upon
#	how much those components will change over a certain period of time
#	the interpolation or function of the changing components (ramp up, log ramp up, liear change over time...)
#	repititions of the animation
#	initial conditions (beginning values of color components)

# an animation chain consists of:
#	individually created animations chained together
#	repitition counts (or infinitely looping)

# the animation manager:
#	is the main interface the programmer will use to add animations to LEDs
#	provides a means to add and remove specific animations from LEDs
#	will do all LED updating / data transmission on a separate thread
#	will create template animations on request that can be modified by the user


from animation_chain import AnimationChain
from led_manager import LedManager
from animation import Animation
import threading
import time


class LedAnimationManager:
    frame_delta = 0.0
    led_man = None

    # the thread that executes the animations on leds
    animation_thread = None
    animation_thread_cancel_lock = None
    animation_thread_stop = False

    led_animations = None
    led_anim_lock = None

    # initialize the animation manager
    # led_manager is the LedManager class that this class will act upon
    # frame rate specifies the target frame rate for the animations as a whole number
    def __init__(self, led_manager, frame_rate=30.0):
        if isinstance(led_manager, LedManager):
            self.led_man = led_manager

        # set desired frame rate for leds
        self.set_frame_rate(frame_rate)

        # initialize lock for stopping our animation thread
        self.animation_thread_cancel_lock = threading.Lock()
        # create our animation thread
        self.animation_thread = threading.Thread(target=self.animation_function, name="animation-thread-0")

        # create animation dictionary
        self.led_animations = {}
        # lock for manipulating the animation dictionary
        self.led_anim_lock = threading.Lock()


    # add an animation chain to an led
    def add_animation(self, led_num, animation_chain):
        if led_num >= self.led_man.numLeds:
            print("*** ERROR: animation_manager.add_animation: led specified is larger than total leds\n")
            return

        if isinstance(animation_chain, AnimationChain):
            self.led_animations[led_num] = animation_chain

        if isinstance(animation_chain, Animation):
            chain = AnimationChain([animation_chain])
            self.led_animations[led_num] = chain

        return


    # removes all animations associated with an led
    def remove_animation(self, which_led):
        # good coding practices say I should lock this but python is single threaded
        self.led_animations.pop(which_led)


    def remove_all_animations(self):
        self.led_animations = {}


    def start_animation_thread(self):
        self.animation_thread.start()

    def end_animation_thread(self):
        self.animation_thread_cancel_lock.acquire(True)
        self.animation_thread_stop = True
        self.animation_thread_cancel_lock.release()


    # sets target frame rate for updating leds
    def set_frame_rate(self, frame_rate):
        self.frame_delta = 1.0 / frame_rate

    # the function that executes animations on the leds
    # the instance of the animation manager is passed in by default because
    # this function is owned by the led animation manager
    def animation_function(ledAnim):
        # get our start time
        initial_time = time.clock()
        while (True):
            # if our frame delta is greater than our set frame rate
            delta = time.clock() - initial_time
            if delta >= ledAnim.frame_delta:
                # execute our animations on their targets
                # print("animate")

                # acquire the animation lock, wait until we get it
                # ledAnim.led_anim_lock.acquire(True)

                finished_animations = []
                # process all animations in the dictionary
                for led_num, anim in ledAnim.led_animations.items():
                    new_colors = anim.do_frame(delta)
                    # print(led_num)
                    # test if our animation is done
                    if not new_colors == None:
                        # animation is not done, so set the color
                        ledAnim.led_man.set_color(led_num, new_colors[0], new_colors[1], new_colors[2])
                    else:
                        # animation is done, add it to a list so that it is removed after iteration
                        finished_animations.append(led_num)

                # after iteration, remove all finished animations
                for led_num in finished_animations:
                    del ledAnim.led_animations[led_num]

                # release lock on the animation dictionary
                # ledAnim.led_anim_lock.release()

                #for i in range(0, ledAnim.led_man.numLeds):
                #    ledAnim.led_man.printLedValue(i)

                # tell led manager to send out values
                ledAnim.led_man.update_leds()

                # update initial time for next iteration
                initial_time = time.clock()

            # check if we should exit the thread
            # get the lock
            # ledAnim.animation_thread_cancel_lock.acquire(True)
            # test our stop flag, exit if necessary
            if (ledAnim.animation_thread_stop == True):
                # ledAnim.animation_thread_cancel_lock.release()
                return
        # do not exit, release lock
        # ledAnim.animation_thread_cancel_lock.release()


if __name__ == '__main__':
    print("\ntesting animation manager")

    # ledMan = LedManager(64)

    ledMan = LedManager(4)
    ledAnim = LedAnimationManager(ledMan)

    from animation import Animation
    R_up = Animation((0, 0, 0), (255, 0, 0), 7.0)
    R_down = Animation((255, 0, 0), (0, 0, 0), 8.0)

    anim1 = Animation((0, 0, 0), (200, 255, 50), 5.0)
    anim2 = Animation((100, 20, 255), (200, 100, 120), 7.0)
    anim3 = Animation((255, 255, 255), (0, 0, 255), 10.0)

    ac = AnimationChain([R_up, R_down], 3)

    ledAnim.add_animation(0, ac)
    ledAnim.add_animation(1, anim1)
    ledAnim.add_animation(2, anim2)
    ledAnim.add_animation(3, anim3)

    for k, v in ledAnim.led_animations.items():
        print("key:" + str(k))
        for a in v.animation_chain:
            print(a.step)

    ledAnim.start_animation_thread()

    try:
        while (True):
            pass
    except:
        print("exception")
        ledAnim.end_animation_thread()

    pass
