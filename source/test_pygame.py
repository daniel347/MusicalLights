import pygame
from time import sleep
pygame.init()
screen = pygame.display.set_mode((640, 640))

if __name__ == "__main__":
    while True:
        for i in range(0,255):
            screen.fill((i, i, i))
            pygame.event.pump()
            pygame.display.flip()
            sleep(0.05)

