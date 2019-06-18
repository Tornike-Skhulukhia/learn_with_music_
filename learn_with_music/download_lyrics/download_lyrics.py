'''
    Class to download lyrics using given search term
'''


if __name__ == "__main__":
    from config import (
        general_db, general_table, lyrics_folder, end_time_convention,
        individual_lyrics_folder, with_meta_data_lyrics_folder)
else:
    from .config import (
        general_db, general_table, lyrics_folder, end_time_convention,
        individual_lyrics_folder, with_meta_data_lyrics_folder)

import time


class LyricsDownloader:
    ''' class to download & save lyrics data '''
    def __init__(self, search_term, v=False):
        self.search_term = search_term.lower().strip()
        self.general_db = general_db
        self.general_table = general_table
        self.lyrics_folder = lyrics_folder
        self.individual_lyrics_folder = individual_lyrics_folder
        self.with_meta_data_lyrics_folder = with_meta_data_lyrics_folder

        self.start_time = time.time()

        self.end_time_convention = end_time_convention
        # we will use these data in database
        self.used_lyrics_site = ""
        self.lyrics_url = ""

        self.v = v 


    def connect_to_db(self, db):
        '''connect to db and return connection & cursor objects'''
        import sqlite3

        conn = sqlite3.connect(db)
        c = conn.cursor()
        return (conn, c)


    def term_is_new(self):
        # because we make this check at first,
        # make sure table exists
        conn, c = self.connect_to_db(self.general_db)
        self.create_general_table_if_necessary(conn, c)

        ''' check if search term is already used'''
        check_sql = \
            ('select * from searches_data where search_term = '
            f'"{self.search_term}" AND lyrics_retrieval_time IS NOT NULL')

        res = c.execute(check_sql).fetchall()

        return False if res else True

    def create_general_table_if_necessary(self, conn, c):
        # create table if not exists
        create_sql = (
            f'CREATE TABLE IF NOT EXISTS {self.general_table} ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'search_term TEXT,'
            'start_time TEXT,'
            "audio_url TEXT,"
            "audio_name_in_source TEXT,"
            "used_lyrics_site TEXT,"
            "lyrics_url TEXT,"
            "lyrics_retrieval_time INTEGER,"
            "audio_retrieval_time INTEGER"
            ')'  )

        c.execute(create_sql)
        conn.commit()


    def save_data_in_db(self):
        '''save objects specific data in appropriate fields'''
        conn, c = self.connect_to_db(self.general_db)
        
        # save record
        insert_sql = (
            f'insert into {self.general_table}'
            '(search_term,'
            'used_lyrics_site, lyrics_url,'
            'lyrics_retrieval_time)'
            'values(?, ?, ?, ?)')

        data_to_add = (
            self.search_term,
            # self.audio_url,
            # self.audio_name_in_source,
            self.used_lyrics_site,
            self.lyrics_url,
            time.time() - self.start_time,
            # self.audio_retrieval_time
            )

        c.execute(insert_sql, data_to_add)
        conn.commit()


    def download_lyrics(self, center_num = 100):
        '''
            Possible returned values:
                1. full lyric text - list of lines
                2. None - if search_term is not new - 
                                data was already tried to download
                                so trying again probably makes no sense
                3. False - if lyrics data 
                            was not found in current sites
        '''

        from requests_html import HTMLSession
        from urllib.parse import quote 
        import re

        # check if term is new
        if not self.term_is_new():
            if self.v: print(
                f' Lyrics for "{self.search_term.title()}" was already downloaded')
            return # we may differentiate answer from False this way

        def download_from_azlyrics(self):
            start_url = "https://search.azlyrics.com/search.php?q={}"
            url = start_url.format(quote(self.search_term.strip()))

            r = HTMLSession().get(url)

            # assume first match as correct one
            lyric_url = ""
            try:
                lyric_url = r.html.xpath("//div[@class='panel'][last()]//td[@class='text-left visitedlyr']//@href")[0]
                # replace [chorus] ... kind of things -- make sure, not other parts are damaged !
                r_2 = HTMLSession().get(lyric_url)
                selector = '///div[@class="col-xs-12 col-lg-8 text-center"]'\
                                                            '//div[not(@*)]//text()'

                lyrics_text = [i.strip() for i in r_2.html.xpath(selector) if i.strip()]
                lyrics_text = [re.sub(r"\[.*\]", "", i) for i in lyrics_text]

                # in case of first, or last line, if it is not empty, add empties
                if lyrics_text[0]:  lyrics_text.insert(0, "" )
                if lyrics_text[-1]: lyrics_text.append("")

                # assign lyric site data to save in database
                self.used_lyrics_site = "azlyrics.com"
                self.lyrics_url = lyric_url
            except:
                # import traceback; print(traceback.format_exc())
                # breakpoint()
                lyrics_text = False

            if self.v:
                if not lyrics_text:   
                    print("Sorry, lyrics not found in source 1...")

            return lyrics_text


        def download_from_lyrics_fandom(self):
            start_url = \
                "https://lyrics.fandom.com/wiki/Special:Search?search={}"
            url = start_url.format(quote(self.search_term.strip()))

            r = HTMLSession().get(url)

            # assume first match as correct one
            lyric_url = ""
            try:
                results =  r.html.find("a.result-link")
                for index, i in enumerate(results):
                    if ":" in i.text and "https://" not in i.text:
                        lyric_url = i.attrs["href"]
                        break
                r = HTMLSession().get(lyric_url)
                selector = 'div.lyricbox'

                lyrics_text = r.html.find(selector)[0].text.split("\n")

                # in case of first, or last line, if it is not empty, add empties
                if lyrics_text[0]:  lyrics_text.insert(0, "" )
                if lyrics_text[-1]: lyrics_text.append("")

                # assign lyric site data to save in database
                self.used_lyrics_site = "lyrics.fandom.com"
                self.lyrics_url = lyric_url
            except:
                # import traceback; print(traceback.format_exc())
                # breakpoint()
                lyrics_text = False

            if self.v:
                if not lyrics_text:   
                    print("Sorry, lyrics not found in source 2...")

            return lyrics_text


        # Go download_from_azlyrics
        answer = download_from_azlyrics(self)

        if not answer:
            answer = download_from_lyrics_fandom(self)

        self.save_data_in_db()
        return answer


    def get_and_save_lyrics(self, center_num = 50):
        '''
            Possible returned values:
                If search term was not new:
                    1. if lyrics found on websites (when tried):
                        data from previously downloaded lyrics files -
                        dictionary in format:
                            {
                                line_num_1: [line_1_text, line_1_end_second],
                                line_num_2: [line_2_text, line_2_end_second],
                                line_num_3: [line_3_text, line_3_end_second]
                                ...
                            }

                    2. if lyrics not found on websites(when tried):
                        None 

                If search term was new:
                    1. if data was found - lyrics datas dictionary
                        (format mentioned above)
                    2. if data not found - False
        '''
        # import 
        import json, os, time

        # save file
        file_loc = os.path.join(
            self.with_meta_data_lyrics_folder, self.search_term + ".json")

        # get lyrics
        lyrics_text = self.download_lyrics(center_num = center_num)

        if lyrics_text:
            save_in_json = {
                "download_date": time.ctime(),
                "last_edit": time.ctime(),
                "lyrics_text":
                    [{"line number": index + 1,
                     "text": line_text } \
                            for index, line_text in enumerate(lyrics_text)]
            }

            with open(file_loc, "w") as f:
                f.write(json.dumps(save_in_json, indent=4))
            # save separate file which we will use in intervals data edit/save
            intervals_save_loc = os.path.join(
                self.individual_lyrics_folder, self.search_term + ".json")

            intervals_data = self.get_lyrics_from_json_file(
                file_loc, "lines_and_seconds")

            with open(intervals_save_loc, "w") as f: 
                f.write(json.dumps(intervals_data, indent=4))

            if self.v:
                print("Lyrics downloaded successfully")
                print("-" * center_num)

            # as we wrote data in file, we do not need to retrieve it again 
            result = intervals_data


        elif lyrics_text is None: # download already was tried
            # was it successfull? yes - if file exists
            intervals_save_loc = os.path.join(
                self.individual_lyrics_folder, self.search_term + ".json")

            if os.path.isfile(file_loc):
                result = self.get_lyrics_from_json_file(
                        intervals_save_loc, "just_data")
            else:
                result = None # data not found
                # here we can also use False, not None, but make them
                # different, so that we may need this information later
                # good news - both evaluate to not True

        else:  # download was not tried before
            result = False  # data not found 

        return result



    def get_lyrics_from_json_file(self, json_file, case):
        import json

        with open(json_file) as f:

            full_json = json.load(f)

            if case == "lines_and_seconds":
                result = {}
                for record in full_json["lyrics_text"]:
                    line_num = record["line number"]
                    text     = record["text"]
                    end_time = self.end_time_convention # convention 

                    result.update(  # save like { line_number : [text, end_time], ...}
                        {
                            line_num: [text, end_time]
                        }
                    )

            elif case == "just_data":
                # breakpoint()
                result = full_json
        return result

