import pygame
import time

class LightStripSim:

    def __init__(self, N_LEDS):
        self.N_LEDS = N_LEDS
        self.MAX_CHANNEL = 255
        self.MIN_CHANNEL = 0

        pygame.init()

        # set up screen
        self.size = (1000, 100)
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill((0, 0, 0))

        self.circle_pos = []
        self.circle_height = int(self.size[1]/2)
        for n in range(self.N_LEDS):
            self.circle_pos.append(int(round(self.size[0] * (n + 0.5) / self.N_LEDS)))
        self.circle_radius = int(self.size[0] / (2 * self.N_LEDS))

    def draw_leds(self, led_array):
        for pos, colour in zip(self.circle_pos, led_array):
            pygame.draw.circle(self.screen, colour, (pos, self.circle_height), self.circle_radius)

        pygame.display.update()

    def play_led_output(self, light_sequence, track_pos = 0.0):
        start_time = time.time()
        for change_time, led_array in light_sequence:
            self.draw_leds(led_array)

            pygame.event.get()
            time_to_next_change = change_time + start_time - track_pos - time.time()
            if time_to_next_change > 0:
                time.sleep(time_to_next_change)

    def close_sim(self):
        pygame.display.quit()
        pygame.quit()