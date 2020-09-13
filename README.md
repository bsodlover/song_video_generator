# Song\_video\_generator
This python script tries to create a song video with songs and videos you provide to it. It basically selects random clips from your video(s) of 15 seconds until it fills the song length. It uses youtube-dl to download your music. You can even put a playlist and this script will make a video for each song.

# How to use
1. Install imagemagick
1. Install dependencies by running pip -r requirements.txt
1. Put your videos on assets/movies
	1.	If you want, you can replace all the other assets with yours.
1. Run the script by doing: python script.py --link "https://yourrl.com" (this url can be a youtube song, soundcloud song, playlist, etc... anything compatible with youtube-dl), or python script.py --dir directory to create a video from all of the songs in the directory (must be on MP3) OR python script.py --file file.txt (a text file with various urls or songs separated by a "," )
	1. It's very recommended to read the optional flags.
3. Be patient. It can take a while.
4. The final video(s) will be on videos/

# Optional Flags
- \-\-start : The starting second to grab clips from your movies. For example, if the movie intro ends on second 350 and you don't want to include the movie intro, you should add the flag --start 350
- \-\-end : The ending second to grab clips from your movies. For example, if the movie final credits start on second 98000 and you don't want to include the final credits, you should add the flag --end 98000
