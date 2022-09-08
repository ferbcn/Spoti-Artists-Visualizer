import pygame
from pygame.sprite import Sprite

colorPals = {"yellows": [[225, 220, 13], (240, 235, 0), (255, 249, 0), (242, 238, 85), (249, 246, 92)],
             "greens": [(8, 108, 2), (71, 106, 55), (23, 179, 38), (68, 132, 90), (16, 168, 46)],
             "reds": [(255, 133, 133), (255, 71, 71), (255, 0, 0), (227, 0, 0), (186, 0, 0)],
             "blues": [(1, 31, 75), (3, 57, 108), (0, 91, 150), (100, 151, 177), (179, 205, 224)],
             "white": [(0, 0, 0)]}

WINDOWWIDTH = 1200
WINDOWHEIGHT = 800

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = [255, 0, 0]

FONTSIZE = 14

class ArtistObject(Sprite):
    def __init__(self, screen, parent=None, name="", uri="", color=(100, 151, 177), pos=(0, 0), popularity=50):
        super(ArtistObject, self).__init__()
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', FONTSIZE)


        self.speed_y = 0

        # Object attributes
        self.parent_artist = parent
        self.popularity = popularity
        self.name = name
        self.uri = uri
        self.size = popularity * 2
        self.color = color

        self.image = pygame.Surface([self.size, self.size])
        self.rect = self.image.get_rect()

        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.text_image = pygame.Surface([len(self.name)*10, 20])
        self.text_rect = self.text_image.get_rect()
        self.text_rect.x = self.rect.x
        self.text_rect.y = self.rect.y

        self.draw()

    def draw(self):
        # draw circle
        pygame.draw.circle(
            self.image,  # Surface to draw on
            self.color,  # Color in RGB Fashion
            [self.size / 2, self.size / 2],  # Center
            self.size / 2,  # Radius
            # draw_top_right=True,
            # draw_top_left=True
        )

        self.image = pygame.image.load('sphere.png')
        self.image = pygame.transform.scale(self.image, (self.popularity*2, self.popularity*2))
        self.image.fill((190, 0, 0, 100), special_flags=pygame.BLEND_ADD)

        # add name as text
        cut = int(self.size/FONTSIZE)*2
        line1 = self.name[:cut]
        line2 = self.name[cut:]
        self.image.blit(self.font.render(line1, True, WHITE), (0, 0))
        self.image.blit(self.font.render(line2, True, WHITE), (0, 20))
        # add line to parent
        # if self.parent_artist is not None:
        #     pygame.draw.line(self.screen, self.color, self.rect.center, self.parent_artist.rect.center, 2)


    def update(self):
        self.rect.y += self.speed_y
        # self.rect.x = self.pos_x

    def move_object(self, pos):
        self.rect.x, self.rect.y = pos
