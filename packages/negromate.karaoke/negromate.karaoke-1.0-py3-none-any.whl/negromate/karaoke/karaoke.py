#!/usr/bin/env python
import os
import subprocess

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout

from negromate.songs.loader import load_songs


class SongWidget(BoxLayout):
    active = BooleanProperty(False)
    song = ObjectProperty('')

    @property
    def name(self):
        return self.song.name

    @property
    def subtitle(self):
        return self.song.karaoke_ass or self.song.ass or self.song.srt or self.song.vtt

    @property
    def video(self):
        return self.song.video

    @property
    def cover(self):
        return str(self.song.cover)

    @property
    def thumbnail(self):
        return str(self.song.thumbnail)


class KaraokeGUI(BoxLayout):
    active_song = ObjectProperty(None)
    songs = ListProperty([])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = Window.request_keyboard(
            self.keyboard_closed,
            self,
            'text',
        )
        self.keyboard.bind(on_key_down=self.on_key_down)

    def on_key_down(self, keyboard, keycode, text, modifiers):
        if text == 'a':
            self.previous()
            return True
        elif text == 'd':
            self.next()
            return True
        elif text == 's':
            self.play()
            return True
        return False

    def keyboard_closed(self):
        pass

    def on_songs(self, instance, value):
        container = self.ids['song_container']
        container.clear_widgets()
        for song in self.songs:
            container.add_widget(song)
        self.active_song = self.songs[0]

    def on_active_song(self, instance, value):
        for song in self.songs:
            song.active = False
        value.active = True
        current_song_image = self.ids['current_song_image']
        current_song_title = self.ids['current_song_title']
        current_song_image.source = value.cover
        current_song_title.text = value.name

        scrollview = self.ids['songs_scroll']
        scrollview.scroll_to(value)

    def previous(self):
        idx = self.songs.index(self.active_song)

        if idx > 0:
            idx -= 1
        else:
            idx = len(self.songs) - 1

        self.active_song = self.songs[idx]

    def next(self):
        idx = self.songs.index(self.active_song)

        if idx < len(self.songs) - 1:
            idx += 1
        else:
            idx = 0

        self.active_song = self.songs[idx]

    def play(self):
        subprocess.call([
            'cvlc',
            '--fullscreen',
            '--no-sub-autodetect-file',
            '--sub-file',
            self.active_song.subtitle,
            self.active_song.video,
            'vlc://quit'
        ])


class KaraokeApp(App):
    kv_directory = os.path.join(os.path.dirname(__file__, ), 'kv_templates')

    def __init__(self, root_folder, **kwargs):
        super().__init__(**kwargs)
        self.root_folder = root_folder

    def build(self):
        super().build()
        songs, _ = load_songs(self.root_folder)
        songs.sort(key=lambda a: a.name.lower())
        self.root.songs = [SongWidget(song=s) for s in songs]
        return self.root


def main(path):
    # Window.fullscreen = True
    resource_add_path(os.path.dirname(__file__))
    LabelBase.register(
        name='CyrBit',
        fn_regular='resources/fonts/CyrBit.ttf')
    KaraokeApp(path).run()
