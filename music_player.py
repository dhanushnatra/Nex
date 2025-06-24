from pathlib import Path
import vlc
import os
from time import sleep

PLAYLIST_FOLDER = "/home/ilikesunday/Music"
player :vlc.MediaPlayer  = vlc.MediaPlayer()
isplaying=False
current=0

def get_songs(folder):
    supported_exts = ('.mp3', '.wav', '.flac', '.ogg', '.aac', ".m4a", ".opus")
    
    if not os.path.isdir(folder):
        print(f"Folder does not exist: {folder}")
        return []
    
    return [os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(supported_exts)]

def play_songs(song_list):
    global current
    try:
        instance :vlc.Instance = vlc.Instance()
        for song in song_list:
            print(f'Playing: {os.path.basename(song)}')
            media = instance.media_new(song)
            current+=1
            player.set_media(media)
            player.play()
            # Wait for the song to finish
            while True:
                state = player.get_state()
                if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
                    break
                sleep(1)
    except KeyboardInterrupt:
        player.stop()

songs = get_songs(PLAYLIST_FOLDER)


def playPause():
    global isplaying
    if player.is_playing():
        player.pause()
        isplaying = False
        return "paused"
    else:
        if current == 0:
            play_songs(song_list=songs)
            isplaying = True
            return "playing from playlist"
        player.play()
        isplaying = True
        return "continued playing"

def stop():
    global isplaying
    player.stop()
    isplaying = False
    return "stopped"
    
if __name__=="__main__":
    playPause()
