from datetime import datetime
from time import strftime, localtime
import os


def str_to_datetime(datestr):
    # print(f"str_to_datetime for: {datestr}")
    
    dt = datetime(int(datestr[0:4]), 
        int(datestr[5:7]), 
        int(datestr[8:10]), 
        hour=int(datestr[11:13]), 
        minute=int(datestr[14:16]), 
        second=int(datestr[17:19]))
            #   microsecond=int(datestr[20:])*1000)
    return dt


def make_directory(root, create_date):
    month = create_date.strftime("%m")
    year = create_date.strftime("%Y")
    year_dir = os.path.join(root, year, month)
    # if os.path.exists(year_dir) and os.path.isdir(year_dir):
    #     print(f"Dir {year_dir} exists")
    # else:
    #     os.path.



def test():
    a = str_to_datetime("2016-01-21 10:20:05.123")
    b = str_to_datetime("2024-03-21 09:27:05.123")
    c = str_to_datetime("2015-07-19 10:18:05.123")
    data = [a, b, c]
    max_dt = max(data)
    # print(max(a,c))
    print (max_dt.strftime("%Y"))
    root = "/home/mdaniel/Projects/pyfun/photo_lib"
    file = "test.txt"
    year = "2024"
    month = "05"
    directory = os.path.join(root, year, month, file)
    print(f"Directory: {directory}")
    
    # filename = "/home/mdaniel/Projects/pyfun/photo_lib/testfile.txt"
    os.makedirs(os.path.dirname(directory), exist_ok = True)
    # os.mkdir(os.path.dirname(filename))

# test()