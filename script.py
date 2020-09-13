import moviepy.editor as mpe
import moviepy.video as mpv
from random import randrange, randint, shuffle
from math import floor
import youtube_dl
import sys
from os import listdir, makedirs
from os.path import isfile, join, exists, splitext, isdir
import json
import pathlib
import logging
import subprocess
import argparse
from mutagen.mp3 import MP3

songs = []
scanned_dirs = []
clips_used = []

parser = argparse.ArgumentParser(""" Song video generator
--start The starting second to grab clips from your movies. For example, if the movie intro ends on second 350 and you don't want to include the movie intro, you should add the flag --start 350
--end  The ending second to grab clips from your movies. For example, if the movie final credits start on second 98000 and you don't want to include the final credits, you should add the flag --end 98000
--link  a link to a song or playlist, in ""
--dir  a directory which contains MP3 songs
--file  a file that contains link songs or playlist separated by a ","
Please take a look at video_maker.log because it contains info about the errors that have happened while making the videos.
""")
parser.add_argument('-s', '--start')
parser.add_argument('-f', '--file')
parser.add_argument('-e', '--end')
parser.add_argument('-l', '--link')
parser.add_argument('-d', '--dir')
args = parser.parse_args()
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
    # 'postprocessors': [{
        # 'key': 'FFmpegExtractAudio',
        # 'preferredcodec': 'mp3',
        # 'preferredquality': '192',
    # }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

class Main:
    def __init__(self,url,is_file):
        if not is_file:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except:
                logging.error("Something has gone wrong while downloading " + url)
            for song in songs:
                ext = splitext(song)[1] #get song file extension
                song_json = song.replace(ext,".info.json") #load song's json
                with open(song_json, 'r') as myfile:
                    data=myfile.read()
                obj = json.loads(data)
                name = str(obj['title'])
                filename = str(obj['title']+" " + obj['uploader'])
                duration = float(str(obj['duration']))
                if not self.check_if_video_done(filename):
                    g = Generator("assets/movies/"+Generator.GetFileFromDir(self,"assets/movies"), song)
                    #if duration <= 250:
                    g.create(duration-5,name,filename)#5 seconds is substracted from the song's duration to avoid errors.
        else:
                try:
                    audio = MP3(url)
                    duration = audio.info.length
                except:
                    duration = 0
                    logging.error("could not extract duration from "+url+", skipping")
                if duration != 0:
                    try:
                        title = audio.get("title")
                        author = audio.get("author")
                        filename = title + " - " + author
                        name = title
                    except:
                        filename = url.replace(".mp3","")
                        filename = filename.split("/")[-1] #we only grab the song's filename and avoid the directories
                        name = filename
                    if not self.check_if_video_done(filename):
                        g = Generator("assets/movies/"+Generator.GetFileFromDir(self,"assets/movies"), url)
                        g.create(duration-5,name,filename)

    def check_if_video_done(self,filename):
        if exists("videos/"+filename+".mkv"):
            logging.warning("skipping " +filename+", already done.")
            print("skipping " +filename+", already done.")
            return True
        else:
            return False





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

    def create_timestamps(self):
        if not args.end or not args.start:
            print("PLEASE INTRODUCE YOUR OWN START AND END TIMESTAMP FOR THE CLIPS WITH FLAGS --start and --end. \n Default 180 will be used.")
            logging.error("PLEASE INTRODUCE YOUR OWN START AND END TIMESTAMP FOR THE CLIPS WITH FLAGS --start and --end. \n Default 180 will be used.")
            args.start = 180
            args.end = 180
        self.end_range = self.clip.duration-int(args.end)
        self.clip_timestamp = [int(args.start)] #we start the clips timestamp array from the start seconds user provided
        while self.clip_timestamp[-1] < self.clip.duration-int(args.end): #while clip_timestamp hasn't reached the desired duration keep on adding 10sec clips
            self.clip_timestamp.append(self.clip_timestamp[-1]+10)
        self.clip_timestamp.pop(-1) #We remove the last one because it contains extra 10 seconds probably not present on the clip
        diff = self.clip_timestamp[-1]-self.end_range+10
        self.clip_timestamp[-1] = self.clip_timestamp[-1]-diff #We narrow the last timestamp to avoid having extra seconds
        shuffle(self.clip_timestamp) #we make the clip_timestamp random so it contains random 10sec clips from the movie

    def audi_test(self):
        f = self.clip.set_audio(self.audio)
        f.write_videofile('out.mp4', temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
    def create(self, desired_length,name,filename):
        self.random_word_screen(name) #we generate the 'intro'
        i = 0
        self.create_timestamps()
        while self.total_duration < desired_length:
           try:
                self.add_clip(self.clip_timestamp[i])
                i = i + 1
           except IndexError: #if we run out of clips, it means that the video is shorter than the song, and all of the clip_timestamp has been used.
                i = 0
                self.create_timestamps() #we randomize again the clips

        final = mpe.concatenate_videoclips(self.clip_list)
        final = mpe.concatenate_videoclips(self.clip_list)
        image = mpe.ImageClip('assets/img/'+Generator.GetFileFromDir(self,"assets/img")).resize(self.clip.size).set_opacity(0.35).set_duration(self.total_duration) #add color overlay
        final = mpe.CompositeVideoClip([final, image])
        self.audio = self.audio.set_duration(desired_length)
        final = final.set_audio(self.audio)
        try:
            final.write_videofile("videos/"+filename+".mkv", temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
        except:
            logging.error("Something has gone wrong while creating final video file " + name)
    def add_clip(self,timestamp):
        subclip = self.clip.subclip(timestamp, timestamp+10)
        merged = mpe.CompositeVideoClip([subclip, self.overlay.subclip(2, 2+timestamp%10)])
        if timestamp%2==0: #adds a fade_in transition if r is even.
            merged = mpv.fx.all.fadein(merged, 3)
        self.clip_list.append(merged)
        self.total_duration += 10

    def random_word_screen(self,name):
        clip = mpe.TextClip(name, font = 'Roboto-Regular', fontsize = 70, color = 'white',size=self.clip.size,bg_color = 'black',method='caption',align='center').set_duration(2)
        self.clip_list.append(clip)
        self.total_duration += 2


try:
    makedirs('videos') #makes the required video folder in case it isn't present.
except:
    pass

if args.file != None:
    with open(args.file, 'r') as myfile:
        for url in myfile.read().split(','):
            Main(url,False)
elif args.dir != None:
    if args.dir[-1] == "/":
        dir = args.dir[:-1]
    else:
        dir = args.dir
    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    for song in files:
        Main(dir+"/"+song,True)
else:
    if args.link != None:
        Main(args.link,False)
    else:
        print("You have not provided any link, dir or text file. Please check the --help flag.")
