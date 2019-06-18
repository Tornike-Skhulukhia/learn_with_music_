'''
    Better documentation is goooiiiiing... :-)
'''


from just_play import just_player
import time, json, os


class Trainer(just_player):
    
    def __init__(self, lyrics, audio_file, search_term):
        super().__init__(lyrics, audio_file)
        self.search_term = search_term.lower().strip()

        # temporary
        self.lyrics_file = os.path.join(
            os.getcwd(), 
            "data/lyrics/individual", 
            self.search_term + ".json")

        ############

    def get_input(self, duration=True):
        # breakpoint()

        start = time.time()
        answer = input("<<<>>>").strip().lower()

        duration_ = time.time() - start
        if duration:
            return (answer, duration_)
            # print(f"returned {answer} & {duration_}")
        else:
            # print(f"returned {answer}")
            return answer


    def reset_line_play_number(self):
        self.lyrics[self.line][1] = 9999


    def set_current_line_duration(self, duration):
        # first line case
        if self.line == 1:
            # we may change it a bit because of dict use, not list...
            self.lyrics[1][1] = duration
        else:
            prev_end_sec = self.lyrics[self.line - 1][1]
            self.lyrics[self.line][1] = prev_end_sec + duration


    def save_changes(self):
        with open(self.lyrics_file, "w") as f:
            print(" Changed Saved ".center(40, "="))
            f.write(json.dumps(self.lyrics, indent=4))


    def reset_lyrics_data_for_training(self):
        ''' reset all changed seconds to 9999-s for now this way'''
        for i, _ in self.lyrics.items():
            self.lyrics[i][1] = 9999  # make dynamic later 


    def train(self):
        self.reset_lyrics_data_for_training()

        print()
        print(" Training started ".center(120, "="))
        text = '''
            Listen to music and look at lyrics shown. 
            Left column shows current line's text, right - next line's text.

            Use these keys for navigation(+ Enter):
                1. Just Enter         - to confirm that line was already told
                2. . (dot)            - to stop process
                3. -number/+number    - to move backward/forward in song lines
            
            Good Luck!
        '''
        # breakpoint()

        print(text)
        print("="*120)

        while True:
            self.play_line(stop_previouses=True)
            self.show_line(sleep_=False, two_column=True)

            answer, duration = self.get_input()
            # self.answer = answer
            # self.duration = duration

            # to not overcompicate with lots of methods for now...
            # make decision
            if answer == "": # confirm sign
                self.set_current_line_duration(duration)
                # differentiate if song ends with False
                if not self.change_line(+1, True):
                    # end
                    print("Training Completed") # :-)
                    self.stop_previous_music()
                    y_n = input(" Save changes?  Y(yes) / N(no) \n").strip()
                    if y_n.lower() == "y": self.save_changes()
                    break


            # stop case  # handle completion later without explicit . (dot) case...
            elif answer == ".": 
                print(" Training Stopped ".center(50, "#")) # :-)
                self.stop_previous_music()
                y_n = input(" Save changes?  Y(yes) / N(no. ) \n").strip()
                if y_n.lower() == "y": self.save_changes()
                break

            # go to specific line case
            elif answer[0] in "-+": 
                # not go in details for now
                try:
                    # breakpoint()
                    num = eval(answer)
                    self.change_line(num, True)
                    # if we returned back, change that back lines 
                    # number to infinity to play again before
                    # stopped
                    if answer[0] == "-":
                        self.reset_line_play_number()
                except:
                    continue

