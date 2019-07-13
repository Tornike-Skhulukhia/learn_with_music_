'''
    class to download audio data
'''



'''
    Database part of all aspects should be done with outer
    class, that will organize lyrics and audio downloads, 
    that solves few problems with code duplication and 
    removes unnecessary checks...

    Just assign appropriate properties using audio&lyrics
    download class methods, when they run and 
    then save this data in database using outer class...
'''

if __name__ == "__main__":
    from config import (
        general_db, general_table, audio_files_folder)
else:
    from .config import (
        general_db, general_table, audio_files_folder)

import os
import time


class AudioDownloader:

    def __init__(self, search_term, v=False):
        self.search_term = search_term.lower().strip()
        
        self.general_db = general_db
        self.general_table = general_table

        self.start_time = time.time()

        self.audio_url = ""
        self.audio_name_in_source = ""

        self.audio_files_folder = audio_files_folder
        self.v = v


    def connect_to_db(self, db):
        '''connect to db and return connection & cursor objects'''
        import sqlite3

        conn = sqlite3.connect(db)
        c = conn.cursor()
        return (conn, c)


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


    def term_is_new(self):
        # because we make this check at first,
        # make sure table exists
        conn, c = self.connect_to_db(self.general_db)
        self.create_general_table_if_necessary(conn, c)

        ''' check if search term is already used'''
        check_sql = \
            ('select * from searches_data where search_term = '
            f'"{self.search_term}" AND audio_retrieval_time IS NOT NULL')

        res = c.execute(check_sql).fetchall()

        return False if res else True


    def save_data_in_db(self):
        '''save objects specific data in appropriate fields'''
        conn, c = self.connect_to_db(self.general_db)
        
        # save record
        insert_sql = (
            f'insert into {self.general_table}('
            'search_term,'
            'audio_url, '
            'audio_name_in_source,' 
            'audio_retrieval_time)'
            'values(?, ?, ?, ?)')

        data_to_add = (
            self.search_term,
            self.audio_url,
            self.audio_name_in_source,
            time.time() - self.start_time,
            # self.audio_retrieval_time
            )

        c.execute(insert_sql, data_to_add)
        conn.commit()



    def download_audio(self):
        '''
            possible returned values:
                if term was not tried before:
                    1. if * was successfull - link of audio file location - 
                        search_term named wav audio files location link
                    2. if something went wrong - False
                        Reason may be that audio source(video on youtube) 
                        was not found, or error occured in program execution
                
                If term tried before:
                    1. link of audio file location - 
                        same as previously mentioned
                    2. False - if audio was not found(when tried), or
                        for some reason we deleted it from folder
        '''
        # import
        from requests_html import HTMLSession
        import youtube_dl

        try:

            # check if file is already downloaded
            filename_mp3 = self.search_term + ".mp3"
            filename_wav = self.search_term + ".wav"
            # file_loc_mp3 = os.path.join(self.audio_files_folder, filename_mp3)
            file_loc_wav = os.path.join(self.audio_files_folder, filename_wav)
            
            if self.term_is_new():
                from urllib.parse import urlencode
                
                params = {"search_query": self.search_term}
                url = f"https://www.youtube.com/results?{urlencode(params)}"

                session = HTMLSession(); r = session.get(url)
                a_s = r.html.xpath('//a[starts-with(@href, "/watch?v=")]')
                # print(len(a_s))

                if self.v: print("render started".center(50))

                r.html.render()
                if self.v: print("render completed".center(50))
                
                a_s = r.html.xpath('//a[starts-with(@href, "/watch?v=")]//@href')

                # assume first one is correct result
                res_url = "https://www.youtube.com" + a_s[0]

                # data to save in general db
                self.audio_url = res_url
                video_title = r.html.find(
                    "a#video-title.yt-simple-endpoint."
                    "style-scope.ytd-video-renderer")[0].text
                self.audio_name_in_source = video_title.strip()

                # os.chdir(save_location)
                file_location = os.path.join(
                    self.audio_files_folder, filename_mp3)

                ydl_opts = {
                    'outtmpl' : file_location,
                    # "quiet"   : True, # if removed, no progress will be shown
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        # sometimes problem with 'opus' vs MP3
                        'preferredcodec': 'mp3', 
                        'preferredquality': '192',
                    }],
                }

                if self.v: print("file download started".center(50))

                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([res_url])


                # # download without python library | --prefer-ffmpeg (argument)
                # comm = f"cd '{self.audio_files_folder}' &&"
                # # --no-warnings causes codec errors -- similar as python library use case
                # comm += f"youtube-dl  -o '{self.search_term}' '{res_url}' --prefer-ffmpeg" 
                # # name probably will be seach_term.webm (?) 
                # # --> we do not care about extension, as we will convert to wav & delete old one
                # # with ffmpeg
                # print(comm)
                # os.system(comm)
                # # exit()


                if self.v: print("file download completed".center(50))

                # because we deal with not only mp3:
                downloaded_filename = [
                    i for i in os.listdir(self.audio_files_folder)
                    if i.startswith(self.search_term)][0]

                audio_file_loc = os.path.join(self.audio_files_folder, downloaded_filename)
                # convert mp3 to wav
                self.convert_mp3_to_wav_and_delete_mp3_file(audio_file_loc)
                self.save_data_in_db()
                result = file_loc_wav

            else:  # term is old
                if os.path.isfile(file_loc_wav):
                    if self.v:
                        print(f'Audio for "{self.search_term.title()}" was already downloaded')# save file
                    result = file_loc_wav
                else:
                    if self.v:
                        print("Search term was already tried & Audio was not found")# save file
                    result = False

        except:
            import traceback; print(traceback.format_exc())
            self.save_data_in_db()
            result = False
            if self.v: print("Sorry, result not found or something went wrong")

        return result


    def convert_mp3_to_wav_and_delete_mp3_file(self, initial_file):

        # actually, it could be different, like .opus file
        folder = os.path.dirname(initial_file) 
        old_file_name = os.path.basename(initial_file)

        # new_file_name = old_file_name.replace(".mp3", ".wav")
        file_extension = old_file_name.split(".")[-1]
        new_file_name = old_file_name.replace(
            "." + file_extension, ".wav")

        new_file_path = os.path.join(folder, new_file_name)

        if self.v: print(f"Converting {file_extension} to wav".center(50))
        comm = f'''ffmpeg -loglevel panic  -y -i "{initial_file}" "{new_file_path}"'''

        os.system(comm)
        os.remove(initial_file)

        # print(comm)
        if self.v: print("Conversion completed".center(50))

