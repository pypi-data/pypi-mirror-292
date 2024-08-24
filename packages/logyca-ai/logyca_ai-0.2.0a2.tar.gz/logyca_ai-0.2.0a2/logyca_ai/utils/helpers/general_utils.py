from datetime import datetime
import random
import os
from datetime import timedelta

def get_random_name_datetime():
    date_now = datetime.now()
    return "{}{}".format(date_now.strftime("%Y%m%d%H%M%S_"),random.randint(10000, 99999))

def delete_files_by_modification_hours(folder,hours_limit:int=8):
    now = datetime.now()
    time_limit = now - timedelta(hours=int(hours_limit))

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            modification_time = os.path.getmtime(file_path)
            modification_datetime = datetime.fromtimestamp(modification_time)
            if modification_datetime < time_limit:
                os.remove(file_path)
