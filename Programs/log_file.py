from datetime import datetime
import glob
import os


log_file_path = 'Files/log_file.txt'
log_file_archive_folder_path = 'Files/Log_File_Archive'


def overwrite_log_file():
    with open(log_file_path, 'w') as log_file:
        log_file.write(
            f'[{datetime.now().replace(microsecond=0)}] {"PROGRAM STARTED":25}: {"/.../RUN.py has begun.":70}'
        )


def write_to_log_file(title, message):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f'\n[{datetime.now().replace(microsecond=0)}] {title:25}: {message:70}')


def archive_log_file():
    archived_log_file_path = \
       f'{log_file_archive_folder_path}/{str(datetime.now().replace(microsecond=0)).replace(" ", "_")}.txt'

    archived_log_file = open(archived_log_file_path, 'w')
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            archived_log_file.write(line)
    archived_log_file.close()

    file_paths_list = sorted(glob.glob(f'{log_file_archive_folder_path}/*.txt'), reverse=True)

    for index, file_path in enumerate(file_paths_list):
        if index > 9:
            os.remove(file_path)
