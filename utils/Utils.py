import sys
import string
import logging
import os
import re
from io import open
import yaml
from core import dumper


def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def inspec(directory, regex_dir_name):
    # Use os.listdir() to get a list of all the files in the directory
    files = os.listdir(directory)
    # Iterate over the list of files and read each one
    for file in files:
        if os.path.isdir(file):
            pass
        with open(os.path.join(directory, file), 'r', encoding='iso8859-1') as f:
            # print(f"[*] reading file: {file}") uncoment if you want to debug :}
            content = f.read()
            #print(content)
            # open regex file
            regex_file = read_yaml('regex.yaml')
            for key, value in regex_file.items():
                regex_obj = re.compile(value)
                check = regex_obj.findall(content)
                if check:
                    for findings in set(check):
                        print(f"[*] FOUND pattern: [{key}]:     [{findings}]")
                        dumper.regex_dump_file(regex_dir_name, findings)


# Progress bar function
def printProgress(times, total, prefix='', suffix='', decimals=2, bar=100):
    filled = int(round(bar * times / float(total)))
    percents = round(100.00 * (times / float(total)), decimals)
    bar = '#' * filled + '-' * (bar - filled)
    sys.stdout.write('%s [%s] %s%s %s\r' %
                     (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if times == total:
        print("\n")


# A very basic implementations of Strings
def strings(filename, directory, min=4):
    strings_file = os.path.join(directory, "strings.txt")
    path = os.path.join(directory, filename)
    with open(path, encoding='Latin-1') as infile:
        str_list = re.findall("[\x20-\x7E]+\x00", infile.read())
        with open(strings_file, "a") as st:
            for string in str_list:
                if len(string) > min:
                    logging.debug(string)
                    st.write(string + "\n")

# Method to receive messages from Javascript API calls


def on_message(message, data):
   print("[on_message] message:", message, "data:", data)
