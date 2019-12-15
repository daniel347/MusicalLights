import pygame
import math

class ChristmasTreeSim:

    def __init__(self, num_light_sets):
        pygame.init()

        # set up screen
        self.size = (640, 640)
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill((0,0,0))

        # define tree geometry
        self.stump = pygame.Rect((self.size[0] - 40)/2, self.size[1] - 60, 40, 60)
        self.stump_colour = pygame.Color(50, 20, 20, 100)  # hopefully brown
        self.base_width = 500  # the max width of the leafy part of the tree
        self.update_rect, self.polygons = self.make_tree_geometry(num_light_sets)

        # draw the stump
        pygame.draw.rect(self.screen, self.stump_colour, self.stump)
        pygame.display.update()


    def make_tree_geometry(self, num_light_sets):
        trapiezium_height = math.floor((self.size[1] - self.stump.height) / num_light_sets)
        print(trapiezium_height)
        base_x1 = (self.size[0] - 500)/2
        base_y1 = self.size[1] - self.stump.height
        grad = self.base_width / (2 * (self.size[1] - self.stump.height))
        print(grad)

        x1 = lambda n : base_x1 + n * trapiezium_height * grad

        base_x2 = (self.size[0] + 500)/2
        x2 = lambda n : base_x2 - n * trapiezium_height * grad

        polygons = []
        for n in range(num_light_sets):
            # construct the trapieziums which make up the tree
            polygons.append([(x1(n), base_y1 - trapiezium_height * n),
                             (x1(n+1), base_y1 - trapiezium_height * (n + 1)),
                             (x2(n+1), base_y1 - trapiezium_height * (n + 1)),
                             (x2(n), base_y1 - trapiezium_height * n),])

        update_rect = pygame.Rect(base_x1, 0, self.base_width, self.size[1] - 60)

        return update_rect, polygons

    def draw_tree(self, brightnesses):
        pygame.event.pump()

        for polygon, brightness in zip(self.polygons, brightnesses):
            c = pygame.Color(brightness, brightness, brightness, 100)  # at the moment use white as the colour
            pygame.draw.polygon(self.screen, c, polygon)

        pygame.display.update(self.update_rect)



