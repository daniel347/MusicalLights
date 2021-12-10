from light_strip_sim import LightStripSim
from light_sequence import LightSequence

import numpy as np

sim = LightStripSim(150,10)
led_out = LightSequence()
led_out.led_array = np.array([[[0,0,0]]*15,
                              [[255,0,0]]*15,
                              [[0,255,0]]*15,
                              [[0,0,255]]*15,
                              [[0,0,0]]*15])

led_out.change_times = np.array([0, 0.5, 1, 1.5, 2])

sim.play_led_output(led_out, track_pos=0)
sim.shutdown()
