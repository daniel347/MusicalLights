import numpy
import christmas_tree_sim as sim
import random
from time import sleep

if __name__ == "__main__":
    tree = sim.ChristmasTreeSim(15)

    while True:
        brightness = [random.randint(0,255) for i in range (15)]
        tree.draw_tree(brightness)
        sleep(1)