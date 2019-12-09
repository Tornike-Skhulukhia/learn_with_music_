'''
    File to test functionality
'''
import sys

from download_audio.download_audio import AudioDownloader
from download_lyrics.download_lyrics import LyricsDownloader
from exercise import Exercise


# test
search_term = "dua lipa be the one" if len(sys.argv) != 2 else sys.argv[1]

print(search_term)
# downoad lyrics
lyrics = LyricsDownloader(
    search_term, True).get_and_save_lyrics()


# download audio
audio = AudioDownloader(
    search_term, True).download_audio()

student = Exercise(lyrics, audio, search_term)


# # I want to ...
student.play(just_show_num=30)
# # student.train()
# # student.exercise()
