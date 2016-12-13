from FBExecute import *
from FBDb import *
from bson import ObjectId
import urllib2
from operator import itemgetter
import os
import operator

dir_path = os.path.dirname(os.path.realpath(__file__))
base_file_path = dir_path + "\\seeds_preprocess\\"
files = os.listdir(base_file_path)
entries = []
for file in files:
    if str(file) != "dump":
        print "---------------------" + file + "---------------------"
        f = open(base_file_path + str(file), 'r')
        for line in f.readlines():
            line = line.strip()
            line_arr = line.split(",")
            fb_profile = line_arr[0].split("/about")[0]
            fb_name = line_arr[1]
            fb_name = fb_name.lower()
            fb_name_list = fb_name.split()
            print fb_profile, fb_name
            entries.append(fb_profile + "===>" + str(fb_name_list))
entries = list(set(entries))
line = "\n"
for entry in entries:
    line = line + entry + "\n"
print line
# with open("all_seeds.txt", "a") as curr_file:
#     curr_file.write(line)




































