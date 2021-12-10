import pygame
import time
import numpy as np

class LightStripSim:

    def __init__(self, N_LEDS, LEDS_PER_COLOUR):
        self.N_LEDS = N_LEDS
        self.LEDS_PER_COLOUR = LEDS_PER_COLOUR
        self.MAX_CHANNEL = 255
        self.MIN_CHANNEL = 0

        pygame.init()

        # set up screen
        self.size = (500, int(500/N_LEDS))
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill((0, 0, 0))

        self.circle_pos = []
        self.circle_height = int(self.size[1]/2)
        for n in range(self.N_LEDS):
            self.circle_pos.append(int(round(self.size[0] * (n + 0.5) / self.N_LEDS)))
        self.circle_radius = int(self.size[0] / (2 * self.N_LEDS))

        # variables to handle playing a sequence
        self.song_start_time = 0.0
        self.sequence_playing = None
        self.sequence_index = 0
        self.max_sequence_index = 0
        self.master_brightness = 1.0

    def draw_leds(self, led_array):
        led_array_repeated = np.repeat(led_array, self.LEDS_PER_COLOUR, axis=0)
        led_array_scaled = np.round(led_array_repeated * self.master_brightness).astype(np.uint8)
        for pos, colour in zip(self.circle_pos, led_array_scaled):
            pygame.draw.circle(self.screen, colour, (pos, self.circle_height), self.circle_radius)

        pygame.display.update()

    def start_playing_sequence(self, light_sequence, track_pos = 0.0):
        self.song_start_time = time.time() - track_pos
        # take the first change time after the start pos
        self.sequence_index = 0
        while light_sequence.change_times[self.sequence_index] < track_pos:
            self.sequence_index += 1

        self.sequence_playing = light_sequence
        self.max_sequence_index = len(light_sequence.change_times)

    def update_playing_sequence(self):
        change_time = self.sequence_playing.change_times[self.sequence_index]
        time_to_next_change = change_time + self.song_start_time - time.time()

        if time_to_next_change < 0:
            led_array = self.sequence_playing.led_array[self.sequence_index]
            self.draw_leds(led_array)

            self.sequence_index += 1
            if self.sequence_index >= self.max_sequence_index:
                # We have reached the end
                return 2
            return 1
        return 0

    def update_simulation(self):
        pygame.event.get()

    def is_playing_sequence(self):
        return self.sequence_playing is not None

    def turn_off_leds(self):
        self.draw_leds(np.array([(0, 0, 0)] * int(self.N_LEDS/self.LEDS_PER_COLOUR)))

    def set_constant_colour(self, led_array):
        self.draw_leds(led_array)

    def set_master_brightness(self, brightness):
        self.master_brightness = max(min(brightness, 1), 0)

    def end_playing_sequence(self):
        self.song_start_time = 0
        self.sequence_index = 0
        self.sequence_playing = None
        self.max_sequence_index = 0

    def shutdown(self):
        pygame.display.quit()
        pygame.quit()
