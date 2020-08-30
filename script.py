import moviepy.editor as mpe
import moviepy.video as mpv
from random import randint
from random import randrange
from math import floor
from assets.words import word_list
import youtube_dl
import sys
from os import listdir
from os.path import isfile, join, exists
import json
import pathlib
import logging
import subprocess

songs = []
scanned_dirs = []
clips_used = []

logging.basicConfig(filename='video_maker.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        logging.error(msg)


def my_hook(d):
    if d['status'] == 'finished':
        songs.append(d['filename'])
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
    def __init__(self,url):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except:
            logging.error("Something has gone wrong while downloading " + url)
        for song in songs:
            song_json = song.replace(".mp3",".info.json")
            with open(song_json, 'r') as myfile:
                data=myfile.read()
            obj = json.loads(data)
            name = str(obj['title'])
            filename = str(obj['title']+" " + obj['uploader'])
            if exists("videos/"+filename+".mkv"):
                logging.warning("skipping " +filename+", already done.")
            else:
                duration = float(str(obj['duration']))
                g = Generator("assets/movies/"+Generator.GetFileFromDir(self,"assets/movies"), song)
                #if duration <= 250:
                g.create(duration-5,name,filename)



class Generator:
    def __init__(self, filename, audioname):
        self.total_duration = 0
        self.clip_list = []
        self.clip = mpe.VideoFileClip(filename)
        self.audio = mpe.AudioFileClip(audioname)
        self.overlay = mpe.VideoFileClip("assets/overlays/"+Generator.GetFileFromDir(self,"assets/overlays")).subclip().resize(self.clip.size).set_opacity(0.40)

    def GetFileFromDir(self, directory):
        if directory not in scanned_dirs:
            scanned_dirs.append(directory)
            files = [f for f in listdir(directory) if isfile(join(directory, f))]
            scanned_dirs.append(files)
        index = scanned_dirs.index(directory)+1
        file = scanned_dirs[index][randrange(len(scanned_dirs[index]))]
        return file

    def audi_test(self):
        f = self.clip.set_audio(self.audio)
        f.write_videofile('out.mp4', temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
    def create(self, desired_length,name,filename):
        self.random_word_screen(name)
        while self.total_duration < desired_length:
            self.add_clip()
        final = mpe.concatenate_videoclips(self.clip_list)
        image = mpe.ImageClip('assets/img/'+Generator.GetFileFromDir(self,"assets/img")).resize(self.clip.size).set_opacity(0.35).set_duration(self.total_duration)
        final = mpe.CompositeVideoClip([final, image])
        self.audio = self.audio.set_duration(self.total_duration)
        final = final.set_audio(self.audio)
        try:
            final.write_videofile("videos/"+filename+".mkv", temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
        except:
            logging.error("Something has gone wrong while creating final video file " + name)
    def add_clip(self):
        print("added clip")
        self.duration = self.rand_clip_gen(180,180)
        if self.check_if_used(self.duration) == True:
            i = 0
            while self.check_if_used(self.duration) == True:
                self.duration = self.rand_clip_gen(180,180)
                i = i + 1
                logging.error(i)
                if i >= 200:
                    print("passed")
                    i = 0
                    break

            while self.check_if_used_last_20(self.duration) == True:
                print("got to last 10 :D")
                self.duration = self.rand_clip_gen(180,180)
                i = i + 1
                if i >= 200:
                    i = 0
                    print("TOP 10 PASSED")
                    break


        for i in self.duration:
            clips_used.append(i)
        subclip = self.clip.subclip(self.duration[0], self.duration[0]+(self.duration[0]%10))
        merged = mpe.CompositeVideoClip([subclip, self.overlay.subclip(2, 2+self.duration[0]%10)])
        if self.duration[0]%2==0: #adds a fade_in transition if r is even.
            merged = mpv.fx.all.fadein(merged, 3)
        self.clip_list.append(merged)
        self.total_duration += self.duration[0]%10

    def random_word_screen(self,name):
        clip = mpe.TextClip(name, font = 'Roboto-Regular', fontsize = 70, color = 'white',size=self.clip.size,bg_color = 'black',method='caption',align='center').set_duration(2)
        self.clip_list.append(clip)
        self.total_duration += 2

    def rand_clip_gen(self,min,max):
        r = randint(min, floor(self.clip.duration-max))
        duration = [r,r+1,r+2,r+3,r+4,r+5,r+6,r+7,r+8,r+9]
        return duration

    def check_if_used(self,duration):
        #print("duartiopm \n "+str(self.duration)+"\n clips used"+str(clips_used))
        for i in self.duration:
            if i in clips_used:
                return True

    def check_if_used_last_20(self,duration):
        last_20_clips = []
        i = 0
        for sec in clips_used:
            if i <= 200:
                last_20_clips.append(sec)
                i = i + 1
        print(len(last_20_clips))
        for e in duration:
            if e in last_20_clips:
                last_20_clips = []
                return True


if isfile(sys.argv[1]):
    with open(sys.argv[1], 'r') as myfile:
        for url in myfile.read().split(','):
            Main(url)
else:
    Main(sys.argv[1])



