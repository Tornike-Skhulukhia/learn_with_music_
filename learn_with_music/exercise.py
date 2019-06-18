'''
    Better documentation is goooiiiiing... :-)
'''

from trainer import Trainer
import random

class Exercise(Trainer):
    '''
        Class to show exercises
    '''
    def save_answer_and_correct_answer(self, answer, correct_answer, sentence):
        ''' add info to process later as third argument dictionary'''
        save_me = {
            "sentence"        : sentence,
            "answer"          : answer,
            "correct_answer"  : correct_answer,
        }
        '''save given answer for line'''
        if len(self.lyrics[self.line]) == 3:
            # already added
            self.lyrics[self.line][2] = save_me
        else:
            self.lyrics[self.line].append(save_me)  # add as 3-rd element in list

    def pp(self):
        '''pretty print lyrics'''
        from pprint import pprint 

        pprint(self.lyrics)

    def current_lyrics_line(self):
        return self.lyrics[self.line][0]


    def print_guess_stats(self):
        # breakpoint()

        # get stats info
        info, correct_num, correct_percentage = self.get_guesses_stats()
        # show stats
        print('='*129)
        # headers
        print(f'|  {"N"} | {"ტექსტი & კითხვა":^70} | {"პასუხი":^17} | {"სწორი პასუხი":^17} | {"სტატუსი"} |')
        print("-"*129)
        # detailed info
        for index, (sentence, guess, correct, sign) in info.items():
            print(f'| {index:<3}| {repr(sentence):<70} | {guess:^17} | {correct:^17} |    {sign}    |')
        print("-"*129)
        # correct percentage
        print(f"სწორი პასუხები - {correct_num}/{len(info)} | ქულა: {correct_percentage}%".center(130))
        print('='*129)



    def get_guesses_stats(self):
        '''
            get guesses list of tuples/lists, in each list/tuple
            with this sequence --> 
                1. shown sentence(with {} symbols)
                2. guess
                3. correct answer
            and return simple summary - how well did we done, + save data later in db
            (analyze individually later, + give recommendations, advices for songs, that will help to help solve mistakes made here)...
        '''
        import string

        guesses = []
        for i in self.lyrics.values():
            if len(i) == 3:
                guesses.append([
                    i[2]['sentence'],
                    i[2]['answer'],
                    i[2]['correct_answer'],
                ])

        questions_num = len(guesses)
        correct_num = 0

        # save info in dictionary with integers as keys
        info = {}

        for index, (sentence, guess, correct) in enumerate(guesses):
            # remove punctuation signs from text, if any(assume, that in proper text it may be only at the end)
            if correct[-1] in string.punctuation : correct = correct[:-1]
            if guess[-1] in string.punctuation : guess = guess[:-1]

            if guess.strip().lower() == correct.lower().strip():
                sign = "+" # correct
                correct_num += 1
            else:
                sign = "-" # incorrect

            info[index + 1] = (sentence, guess, correct, sign)# start from 1
        correct_percentage = round(correct_num / questions_num, 2) * 100

        return (info, correct_num, correct_percentage)


    def select_and_remove_word(self, text):
        ''' 
            get line text and remove one word from it,
            then return this word and sentence with this word replaced
            by {}
        '''
        words = [i for i in text.split(" ")]

        index = random.randint(1, len(words) - 1)
        random_word = words[index]

        words[index] = "{}" # replace selected words place
        sentence = " ".join(words)

        return [random_word, sentence]



    # maybe add this method in separate class later...
    def exercise(self):
        '''similar to Train classes train method'''
        print()
        print(" Exercise started ".center(120, "="))
        text = '''
            Listen to music and look at lyrics shown. 
            Type word that was told in place of {} symbol when necessary.

            Use these keys for navigation(+ Enter):
                1. answer text        - to confirm your answer
                2. . (dot)            - to stop process
                3. -number/+number    - to move backward/forward in song lines
                4. r (or space/s)     - to repeat line 
            
            Good Luck!
        '''
        # breakpoint()

        print(text)
        print("="*120)

        while True:
            if str(self.lyrics[self.line][1]) != "9999":  # check to not play forever if still 9999 is value
                
                line_text = self.current_lyrics_line()

                removed_word = ""

                self.play_line(stop_previouses=True)

                if random.randint(1, 3) in [1, 2, 3] and len(line_text) > 20:  # to make not similar each case
                    # breakpoint()
                    
                    removed_word, line_text = self.select_and_remove_word(line_text)

                    self.show_line(sleep_=True, custom_one=line_text)

                    answer = self.get_input(duration=False)

                    if answer == "r" or answer == "":
                        continue  # --> repeat same line

                    # stop case  # handle completion later without explicit . (dot) case...
                    elif answer.strip() == ".": 
                        print(" Exercise Stopped ".center(50, "#")) # :-)
                        # self.stop_previous_music()
                        # y_n = input(" Save changes?  Y(yes) / N(no. ) \n").strip()
                        # if y_n.lower() == "y": self.save_changes()
                        break
                        self.print_exercise_results()

                    # go to specific line case
                    elif answer and answer[0] in "-+": 
                        # not go in details for now
                        try:
                            # breakpoint()
                            num = eval(answer)
                            self.change_line(num, True)
                            # # if we returned back, change that back lines 
                            # # number to infinity to play again before
                            # # stopped
                            # if answer[0] == "-":
                            #     self.reset_line_play_number()
                        except:
                            continue
                        # we get answer
                    elif answer:  # 
                        self.save_answer_and_correct_answer(
                                    answer, removed_word, line_text)
                        # differentiate if song ends with False
                        if not self.change_line(+1, True):
                            # end
                            print("Exercise Completed") # :-)
                            self.stop_previous_music()
                            break
                    else:
                        print("something went wrong...")
                else:
                    self.show_line(sleep_=True)
                    self.change_line(1, True)
            else:
                print("Exercise Completed") # :-)
                break
                self.stop_previous_music()
        self.print_guess_stats()

