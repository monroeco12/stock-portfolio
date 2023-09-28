from datetime import datetime


timestamps_file_path = 'Files/timestamps.csv'


def create_timestamps_dict():
    timestamps_dict = {}
    with open(timestamps_file_path, 'r') as timestamps_file:
        for index, line in enumerate(timestamps_file):
            if index > 0:
                data_list = line.rstrip().split(',')

                file_name, last_seen = data_list[0], data_list[1]

                timestamps_dict[file_name] = last_seen

    return timestamps_dict


def update_timestamps_file(timestamps_dict):
    with open(timestamps_file_path, 'w') as timestamps_file:
        timestamps_file.write(f'File_Name,Last_Seen\n')
        for file_name in timestamps_dict:
            timestamps_file.write(f'{file_name},{timestamps_dict[file_name]}\n')


def ignore_weekend(file_name, current_time):
    program_list = ['update_indicators_file.py']

    current_day_name = datetime.strftime(current_time, '%A')

    continue_on = True
    if current_day_name in ['Saturday', 'Sunday'] and file_name not in program_list:
        continue_on = False

    return continue_on


def check_timestamps_file(file_name, program_start_time):
    timestamps_dict = create_timestamps_dict()

    current_time = datetime.now().replace(microsecond=0)
    try:
        last_seen = datetime.strptime(timestamps_dict[file_name], '%Y-%m-%d %H:%M:%S')
    except KeyError:
        last_seen = 'N/A'

    continue_on = False
    seven_pm = program_start_time.replace(hour=19, minute=0, second=0)
    if seven_pm <= current_time or last_seen == 'N/A':
        continue_on = True

    if continue_on is True:
        timestamps_dict[file_name] = current_time
        update_timestamps_file(timestamps_dict=timestamps_dict)
        continue_on = ignore_weekend(file_name=file_name,
                                     current_time=program_start_time)

    return continue_on
