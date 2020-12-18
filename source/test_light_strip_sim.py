from light_strip_sim import LightStripSim

sim = LightStripSim(150)
led_out = [{"time": 0, "led_array": [(255, 255, 255)] * 150},
           {"time": 1, "led_array": [(255, 0, 255)] * 150},
           {"time": 2, "led_array": [(255, 255, 0)] * 150},
           {"time": 3, "led_array": [(0, 255, 0)] * 150},
           {"time": 4, "led_array": [(0, 0, 255)] * 150}]

sim.play_led_output(led_out, track_pos=2.5)