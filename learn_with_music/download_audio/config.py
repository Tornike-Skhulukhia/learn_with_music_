# DRY - solve later 

'''
    config file for audio download
''' 
import os

data_folder = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))),"data")

# print(data_folder)

# database to save general data, such as search terms & retrieval times
general_db = os.path.join(data_folder, "general.db")

# name for general searches data saving table
general_table = "searches_data"

# folder to save all audio files
audio_files_folder = \
    os.path.join(data_folder, "audio")
