'''
    Better documentation is goooiiiiing... :-)
'''


from pprint import pprint as pp
# from cadmium_info import lyrics
import os
import threading
from time import sleep

class just_player:
    '''
        Class to just play the audio
    '''
    def __init__(self, lyrics, audio_file):

        if not isinstance(lyrics, dict):
            self.lyrics = {i + 1: list(j) for i, j in enumerate(lyrics)}
            # self.lyrics = lyrics
        else:
            self.lyrics = {int(i): j for i, j in lyrics.items()}
        self.line = 1
        self.max_line_num = len(self.lyrics)
        self.audio_file = audio_file


    # helpers
    def stop_previous_music(self):
        comm = '''killall ffplay_local >/dev/null 2>&1'''
        os.system(comm)
    

    def reset_line(self):
        self.line = 1 

    def play_music_(self, start_second, duration, stop_previouses):
        if stop_previouses: self.stop_previous_music()

        bin_ = os.path.join(os.getcwd(), "bin", "ffplay_local")

        comm = (f'{bin_} -ss {start_second} -t'
                  f' {duration} "{self.audio_file}"' 
                  f' -loglevel quiet -nodisp -autoexit')
        os.system(comm)


    def play_music(self, start_second, duration, stop_previouses=False):
        threading.Thread(target=self.play_music_, 
                         args=(start_second, duration, stop_previouses)).start()



    def get_line_start_second(self):
        if self.line != 1:
            start = self.lyrics[self.line - 1][1]
            # 9999 case -- when going say +124 line forward...
            if str(start) == "9999":
                for i in range(self.line - 1)[::-1]:
                    if str(self.lyrics[self.line - i][1]) != "9999":
                        start = self.lyrics[self.line - i][1]
                else:
                    start = 0
        else:
            start = 0 # start from 0 second, if it is first line

        return start


    def get_current_line_duration(self):
        # how many seconds should current line be played for
        start = self.get_line_start_second()
        # breakpoint()

        end =   self.lyrics[self.line][1]
        duration = end - start

        return duration


    def play_line(self, stop_previouses=False):
        # play current line, use self.lyrics property info
        start_second = self.get_line_start_second()
        duration = self.get_current_line_duration()

        self.play_music(start_second, duration, stop_previouses)
        # sleep(duration) 


    def get_line_text(self, current=True):
        '''
            Get current or next lines, if current is False
        '''
        if not current: 
            if self.line + 1 <= self.max_line_num:
                answer = self.lyrics[self.line + 1][0]
            else:
                answer = ""  # no lines left
        else:
            answer = self.lyrics[self.line][0]

        return answer


    def show_line(self, sleep_=True, two_column=False, custom_one=False):
        duration = self.get_current_line_duration()
        current_line = self.get_line_text()
        next_line = self.get_line_text(current=False)

        if custom_one:
            print(custom_one.center(50))
        else:
            if two_column:
                # print(repr(text))
                print(current_line.center(50), " | ", next_line.center(50))
            else:
                print(current_line.center(50))

        if sleep_: sleep(duration)


    def change_line(self, num, show_current_line=False):
        '''
            returns False if line is last, so
            it can not bi increased any more 
            ==> if training, --> finished training
        '''
        # num ex: +1, -3 ...
        new_line = self.line + num 

        # refine new_line value
        # write in more readable way
        if new_line > self.max_line_num:
            new_line = self.max_line_num
            return False

        elif new_line < 1:
            new_line = 1

        self.line = new_line
        if show_current_line:
            print(" Line N:".rjust(140, "="), self.line)

        return True

    def play(self, just_show_num=False):
        # play music
        self.stop_previous_music()
        self.reset_line()
        print()
        print(" Player started ".center(50, "="))
        print()
        # breakpoint()

        if just_show_num:
            for index, (i, j) in enumerate(self.lyrics.items()):
                if index +1 <= just_show_num:
                    print(i, j[0])

        for line_num in self.lyrics:
            self.play_line()
            self.show_line()
            # self.line += 1 
            self.change_line(+1)

