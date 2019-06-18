'''
    File to test functionality
'''

from download_audio.download_audio import AudioDownloader
from download_lyrics.download_lyrics import LyricsDownloader
from exercise import Exercise

# test
search_term = "alan walker ignite"

# downoad lyrics
lyrics = LyricsDownloader(
    search_term, True).get_and_save_lyrics()

# download audio
audio = AudioDownloader(
    search_term, True).download_audio()

student = Exercise(lyrics, audio, search_term)

# I want to ...
student.play(just_show_num=0)
# student.train()
# student.exercise()
