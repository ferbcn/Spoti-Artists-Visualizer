import json
import math

import pygame, sys, time
import spotipy
from pygame.locals import *
import random

from pygame.sprite import Sprite
from spotipy import SpotifyClientCredentials

colorPals = {"yellows": [(225, 220, 13), (240, 235, 0), (255, 249, 0), (242, 238, 85), (249, 246, 92)],
             "greens": [(8, 108, 2), (71, 106, 55), (23, 179, 38), (68, 132, 90), (16, 168, 46)],
             "reds": [(255, 133, 133), (255, 71, 71), (255, 0, 0), (227, 0, 0), (186, 0, 0)],
             "blues": [(1, 31, 75), (3, 57, 108), (0, 91, 150), (100, 151, 177), (179, 205, 224)],
             "white": [(0, 0, 0)]}

WINDOWWIDTH = 800
WINDOWHEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def load_settings():
    with open("settings.json", "r") as j:
        settings = json.load(j)
    return settings

class ArtistObject(Sprite):
    def __init__(self, screen, name="Daft Punk", pos=(100,100)):
        super(ArtistObject, self).__init__()
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 18)

        """
        self.image = pygame.image.load('sphere.png')
        width = self.image.get_rect().width
        height = self.image.get_rect().height
        self.image = pygame.transform.scale(self.image, (width/2, height/2))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        """

        # Object attributes
        self.parent_artist = None
        self.name = name
        self.size = 100
        self.color = None

        self.image = pygame.Surface([self.size, self.size])
        #self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.rect.x = pos[0]
        self.rect.y = pos[1]

        pygame.draw.circle(
            self.image,  # Surface to draw on
            [255, 10, 50],  # Color in RGB Fashion
            [self.size/2, self.size/2],  # Center
            50,  # Radius
            # draw_top_right=True,
            # draw_top_left=True
        )

        self.image.blit(self.font.render(self.name, True, WHITE), (0, 0))


    def update(self):
        pass
        # self.rect.x = self.pos_x
        # self.rect.y = self.pos_y

    def move_object(self, pos):
        self.rect.x, self.rect.y = pos


class Visualizer:
    def __init__(self):
        super().__init__()

        self.timer = 0
        self.dt = 0.05

        # Configuration
        pygame.init()
        self.fps = 30
        self.fpsClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

        self.mouse_down = False

        self.root_artist = ArtistObject(self.screen, pos=(WINDOWWIDTH/2,WINDOWHEIGHT/2))
        self.artist_collection = pygame.sprite.Group()
        self.artist_collection.add(self.root_artist)

        self.selected_artist = self.root_artist

        # setup spotipy credentials
        settings = load_settings()
        self.spoti = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(settings.get('spotipy_client_id'),
                                                                settings.get('spotipy_client_secret')))

        self.run_loop()


    def run_loop(self):
        # Game loop.
        while True:
            self.screen.fill(BLACK)
            self.artist_collection.draw(self.screen)
            self.artist_collection.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == MOUSEBUTTONUP:
                    self.mouse_down = False

                elif event.type == MOUSEBUTTONDOWN:
                    self.mouse_down = True
                    if event.button == 1:
                        if self.timer == 0:  # First mouse click.
                            self.timer = 0.001  # Start the timer.
                        # Click again before 0.5 seconds to double click.
                        elif self.timer < 0.5:
                            print('double click')
                            self.create_children()
                            self.timer = 0

                if event.type == MOUSEMOTION:
                    if self.mouse_down:
                        x, y = event.pos
                        pos = (x-100/2, y-100/2)
                        self.selected_artist.move_object(pos)

            # Increase timer after mouse was pressed the first time.
            if self.timer != 0:
                self.timer += self.dt
                # Reset after 0.5 seconds.
                if self.timer >= 0.5:
                    print('too late')
                    self.timer = 0

            pygame.display.flip()
            self.fpsClock.tick(self.fps)


    def create_children(self, artist_name="Daft Punk"):
        self.artist_collection.empty()
        artist_uri = self.get_artist_uri_from_name(artist_name)
        # suggested_artists = ["Justice", "Kavinsky", "Breakbot", "Digitalism", "Cassius"]
        suggested_artists = self.search_suggested_artists_from_uri(artist_uri)

        l = len(suggested_artists)
        step = 2*math.pi / l
        new_pos = []
        for i in range(l):
            x = math.cos(i*step) * 200 + self.selected_artist.rect.x
            y = math.sin(i*step) * 200 + self.selected_artist.rect.y
            new_pos.append((x, y))
        print(new_pos)

        for i in range(l):
            new_art = ArtistObject(self.screen, name=suggested_artists[i][0], pos=new_pos[i])
            self.artist_collection.add(new_art)

    def search_suggested_artists_from_uri(self, artist_uri):
        suggested_artists = []
        results = self.spoti.artist_related_artists(artist_uri)
        artists = results['artists']
        for item in artists:
            image_url = item['images'][-1:]
            suggested_artists.append((item['name'], item['uri'], image_url))
        return suggested_artists

    def get_artist_uri_from_name(self, artist_name):
        results = self.spoti.search(q='artist:' + artist_name, type='artist')
        artist_uri = results['artists']['items'][0]['uri']
        return artist_uri


if __name__ == "__main__":
    # init fireworks class
    v = Visualizer()
