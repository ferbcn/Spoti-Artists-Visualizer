import json
import math

import pygame, sys, time
import spotipy
from pygame.locals import *
import random

from pygame.sprite import Sprite
from spotipy import SpotifyClientCredentials

from artist_object import ArtistObject


WINDOWWIDTH = 1200
WINDOWHEIGHT = 1000

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = [255, 0, 0]
GREEN = [10, 250, 10]

def load_settings():
    with open("settings.json", "r") as j:
        settings = json.load(j)
    return settings


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


        self.root_artist = ArtistObject(self.screen, uri="4tZwfgrHOc3mvqYlEYSvVi", color=GREEN, pos=(WINDOWWIDTH/2,WINDOWHEIGHT/2))
        self.selected_artist = self.root_artist
        self.prev_selected_artist = None
        self.artist_collection = pygame.sprite.Group()
        self.artist_collection.add(self.root_artist)

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

                elif event.type == KEYDOWN:
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
                            self.prev_selected_artist.rect.x = self.selected_artist.rect.x
                            self.prev_selected_artist.rect.y = self.selected_artist.rect.y

                            self.selected_artist.rect.x = WINDOWWIDTH / 2
                            self.selected_artist.rect.y = WINDOWHEIGHT / 2

                            self.create_children()
                            self.timer = 0
                    x, y = event.pos
                    for artist in self.artist_collection:
                        if artist.rect.collidepoint(x, y):
                            print(artist.name)
                            self.selected_artist.color = RED
                            self.selected_artist.draw()
                            self.prev_selected_artist = self.selected_artist
                            self.selected_artist = artist
                            self.selected_artist.color = GREEN
                            self.selected_artist.draw()

                if event.type == MOUSEMOTION:
                    if self.mouse_down:
                        x, y = event.pos
                        pos = (x-100/2, y-100/2)
                        #for artist in self.artist_collection:
                        #    artist.move_object(pos)
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


    def create_children(self):
        self.artist_collection.empty()
        self.artist_collection.add(self.selected_artist)
        #artist_uri = self.get_artist_uri_from_name(artist_name)
        # suggested_artists = ["Justice", "Kavinsky", "Breakbot", "Digitalism", "Cassius"]
        suggested_artists = self.search_suggested_artists_from_uri(self.selected_artist.uri)

        l = len(suggested_artists)
        step = 2*math.pi / l
        new_pos = []
        for i in range(l):
            x = math.cos(i*step) * 300 + self.selected_artist.rect.x
            y = math.sin(i*step) * 300 + self.selected_artist.rect.y
            new_pos.append((x, y))

        for i in range(l):
            new_art = ArtistObject(self.screen, parent=self.selected_artist, name=suggested_artists[i][0], popularity=suggested_artists[i][2], uri=suggested_artists[i][1], pos=new_pos[i])
            self.artist_collection.add(new_art)

    def search_suggested_artists_from_uri(self, artist_uri, limit=12):
        suggested_artists = []
        results = self.spoti.artist_related_artists(artist_uri)
        artists = results['artists'][:limit]
        for item in artists:
            image_url = item['images'][-1:]
            suggested_artists.append((item['name'], item['uri'], item['popularity'], image_url))
        return suggested_artists

    def get_artist_uri_from_name(self, artist_name):
        results = self.spoti.search(q='artist:' + artist_name, type='artist')
        artist_uri = results['artists']['items'][0]['uri']
        return artist_uri


if __name__ == "__main__":
    # init fireworks class
    v = Visualizer()
