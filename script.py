import moviepy.editor as mpe
import moviepy.video as mpv
from random import randint
from random import randrange
from math import floor
from assets.words import word_list
import youtube_dl
import sys
from mutagen.mp3 import MP3
songs = []
from os import listdir
from os.path import isfile, join
import json
import pathlib
import logging
import subprocess


logging.basicConfig(filename='sad_gen.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        songs.append(d['filename'])
        print('Done downloading '+ d['filename'] +' , now converting ...')
ydl_opts = {
    'writeinfojson': 'True',
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

class Main:
    movies = [f for f in listdir("assets/movies") if isfile(join("assets/movies", f))]
    def __init__(self,url):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except:
            logging.error("Something has gone wrong while downloading " + url)
        for song in songs:
            movie = self.movies[randrange(len(self.movies))]
            audio = MP3(song)
            g = Generator("assets/movies/"+movie, song)
            song_json = song.replace(".mp3",".info.json")
            with open(song_json, 'r') as myfile:
                data=myfile.read()
            obj = json.loads(data)
            name = str(obj['title'])
            print(movie)
            g.create(audio.info.length-5,name)



class Generator:
    def __init__(self, filename, audioname):
        self.overlays = [f for f in listdir("assets/overlays") if isfile(join("assets/overlays", f))]
        self.total_duration = 0
        self.clip_list = []
        self.clip = mpe.VideoFileClip(filename)
        self.audio = mpe.AudioFileClip(audioname)
        self.overlay = mpe.VideoFileClip("assets/overlays/"+self.overlays[randrange(len(self.overlays))]).subclip().resize(self.clip.size).set_opacity(0.40)

    def audi_test(self):
        f = self.clip.set_audio(self.audio)
        f.write_videofile('out.mp4', temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
    def create(self, desired_length,name):
        self.random_word_screen(name)
        while self.total_duration < desired_length:
            self.add_clip()
        self.images = [f for f in listdir("assets/img") if isfile(join("assets/img", f))]
        self.image_name = self.images[randrange(len(self.images))]
        final = mpe.concatenate_videoclips(self.clip_list)
        image = mpe.ImageClip('assets/img/'+self.image_name).resize(self.clip.size).set_opacity(0.35).set_duration(self.total_duration)
        final = mpe.CompositeVideoClip([final, image])
        self.audio = self.audio.set_duration(self.total_duration)
        final = final.set_audio(self.audio)
        try:
            final.write_videofile("videos/"+name+".mkv", temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
        except:
            logging.error("Something has gone wrong while creating final video file " + name)
    def add_clip(self):
        r = randint(300, floor(self.clip.duration-860))
        subclip = self.clip.subclip(r, r+(r%10))
        merged = mpe.CompositeVideoClip([subclip, self.overlay.subclip(2, 2+r%10)])
        if r%2==0: #adds a fade_in transition if r is even.
            merged = mpv.fx.all.fadein(merged, 3)
        self.clip_list.append(merged)
        self.total_duration += r%10

    def random_word_screen(self,name):
        clip = mpe.TextClip(name, font = 'Roboto-Regular', fontsize = 70, color = 'white',size=self.clip.size,bg_color = 'black',method='caption',align='center').set_duration(2)
        self.clip_list.append(clip)
        self.total_duration += 2

if isfile(sys.argv[1]):
    with open(sys.argv[1], 'r') as myfile:
        for url in myfile.read().split(','):
            Main(url)
else:
    Main(sys.argv[1])

