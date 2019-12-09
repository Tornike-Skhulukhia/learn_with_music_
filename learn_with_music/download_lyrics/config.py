# DRY - solve later

'''
    Config file for lyrics download
'''
import os

data_folder = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "data")

# print(data_folder)

# database to save general data, such as search terms & retrieval times
general_db = os.path.join(data_folder, "general.db")

# name for general searches data saving table
general_table = "searches_data"

# for each search term, create folder and save training versions there
lyrics_folder = \
    os.path.join(data_folder, "lyrics")

individual_lyrics_folder = \
    os.path.join(lyrics_folder, "individual")

with_meta_data_lyrics_folder = \
    os.path.join(lyrics_folder, "with_meta_data")

# end time to assign to all lyrics lines when downloaded
end_time_convention = 9999
