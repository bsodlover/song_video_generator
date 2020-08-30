# Song\_video\_generator
This python script tries to create a song video with songs and videos you provide to it. It basically selects random clips from your video(s) of 15 seconds until it fills the song length. It uses youtube-dl to download your music. You can even put a playlist and this script will make a video for each song.

# How to use
1. Install imagemagick
1. Install dependencies by running pip -r requirements.txt
1. Put your videos on assets/movies
	1.	If you want, you can replace all the other assets with yours.
1. Run the script by doing: python script.py url (this url can be a youtube song, soundcloud song, playlist, etc... anything compatible with youtube-dl) OR python script.py your-song.mp3 OR python script.py songs.txt (a text file with various urls separated by a "," )
	1. It's very recommended to read the optional flags.
1. Be patient. It can take a while.
1. The final video(s) will be on videos/

# Optional Flags

