import json
import math

import pygame, sys, time
import spotipy
from pygame.locals import *
import random

from pygame.sprite import Sprite
from spotipy import SpotifyClientCredentials

from artist_object import ArtistObject

WINDOWWIDTH = 2000
WINDOWHEIGHT = 1000

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = [205, 0, 200]
GREEN = [10, 50, 200]


def load_settings():
    with open("settings.json", "r") as j:
        settings = json.load(j)
    return settings


class Visualizer:
    def __init__(self):
        super().__init__()

        self.timer = 0
        self.dt = 0.05

        self.req_timer = 0
        self.r_dt = 0.01

        # Configuration
        pygame.init()
        self.fps = 30
        self.fpsClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

        self.mouse_down = False
        self.run = False

        self.text = ""
        self.root_artist = ArtistObject(self.screen, uri="4tZwfgrHOc3mvqYlEYSvVi", color=GREEN,
                                        pos=(WINDOWWIDTH / 2, 0), popularity=40)
        self.selected_artist = self.root_artist
        self.prev_selected_artist = None
        self.artist_collection = pygame.sprite.Group()
        self.artist_collection.add(self.root_artist)

        self.current_results = []
        self.selection_history = []
        self.current_results.append(self.root_artist)
        # self.selection_history.append(self.root_artist)

        # setup spotipy credentials
        settings = load_settings()
        self.sp = spotipy.Spotify(
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
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    # PAUSE / RESUME animation
                    elif event.key == pygame.K_SPACE:
                        if self.run:
                            self.run = False
                        else:
                            self.run = True
                    # Finish Reading Input and start animation
                    elif event.key == pygame.K_RETURN:
                        # search artists uri
                        uri = self.get_artist_uri_from_name(self.text)
                        self.selected_artist.uri = uri
                        print(self.text, uri)
                        self.selection_history.append(self.selected_artist)
                        # launch search
                        self.run = True
                    # get keystrokes from keyboard
                    else:
                        self.text += event.unicode
                        self.root_artist.name = self.text
                        self.root_artist.image.fill(BLACK)
                        self.root_artist.draw()


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
                    x, y = event.pos
                    for artist in self.artist_collection:
                        if artist.rect.collidepoint(x, y):
                            self.select_artist_from_options(artist)

                if event.type == MOUSEMOTION:
                    if self.mouse_down:
                        x, y = event.pos
                        pos = (x - 100 / 2, y - 100 / 2)
                        # for artist in self.artist_collection:
                        #    artist.move_object(pos)
                        self.selected_artist.move_object(pos)

            # Increase timer after mouse was pressed the first time.
            if self.timer != 0:
                self.timer += self.dt
                # Reset after 0.5 seconds.
                if self.timer >= 0.5:
                    print('too late')
                    self.timer = 0

            if self.req_timer > 0.05 and self.run:
                self.auto_make_step()
                self.req_timer = 0

            self.req_timer += self.r_dt

            pygame.display.flip()
            self.fpsClock.tick(self.fps)

    def auto_make_step(self):
        # # pic a random result
        # r = random.randint(0, len(self.current_results) - 1)
        # selection = self.current_results[r]
        if len(self.selection_history) > 1:
            for history in self.selection_history:
                for artist in self.current_results:
                    if artist.name == history.name:
                        self.current_results.remove(artist)
                        break
        # Pick most popular result
        selection = self.current_results[0]
        for artist in self.current_results:
            if artist.popularity > selection.popularity:
                selection = artist

        self.select_artist_from_options(selection)
        self.selection_history.append(selection)
        self.create_children()

    def select_artist_from_options(self, artist):
        print(artist.name)
        # self.selected_artist.color = PURPLE
        # self.selected_artist.draw()
        self.prev_selected_artist = self.selected_artist
        self.selected_artist = artist
        self.selected_artist.color = GREEN
        self.selected_artist.draw()


    def create_children(self):
        self.current_results.clear()
        # artist_uri = self.get_artist_uri_from_name(artist_name)
        # suggested_artists = ["Justice", "Kavinsky", "Breakbot", "Digitalism", "Cassius"]
        suggested_artists = self.search_suggested_artists_from_uri(self.selected_artist.uri)

        l = len(suggested_artists)
        step = (WINDOWWIDTH - 200) / l
        new_pos = []
        # set new row height
        y = self.selected_artist.rect.centery + 100
        # if new row is out of window move all objects to top
        if y > WINDOWHEIGHT:
            for artist in self.artist_collection:
                artist.rect.y -= WINDOWHEIGHT
                artist.draw()
            y = self.selected_artist.rect.y + 100
        for i in range(l):
            x = 100 + i * step
            new_pos.append((x, y))

        for i in range(l):
            new_art = ArtistObject(self.screen, parent=self.selected_artist, name=suggested_artists[i][0],
                                   popularity=suggested_artists[i][2], uri=suggested_artists[i][1], pos=new_pos[i], color=PURPLE)
            self.artist_collection.add(new_art)
            self.current_results.append(new_art)

    def search_suggested_artists_from_uri(self, artist_uri, limit=12):
        suggested_artists = []
        results = self.sp.artist_related_artists(artist_uri)
        artists = results['artists'][:limit]
        for item in artists:
            image_url = item['images'][-1:]
            suggested_artists.append((item['name'], item['uri'], item['popularity'], image_url))
        return suggested_artists

    def get_artist_uri_from_name(self, artist_name):
        results = self.sp.search(q='artist:' + artist_name, type='artist')
        artist_uri = results['artists']['items'][0]['uri']
        return artist_uri


if __name__ == "__main__":
    # init fireworks class
    v = Visualizer()
