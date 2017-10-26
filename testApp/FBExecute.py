from _ast import alias
from pydoc_data import topics

import facebook
import json
import ast
import mechanize
import re
import csv
import string
import cookielib
import sys
import time
import os

from FBDb import *
from FBExecute import *
import random
from bson import ObjectId
import urllib2
from operator import itemgetter

# colleges = []
# colleges.append("bangladesh%20university%20of%20engineering%20and%20technology")
# colleges.append("buet")

class FBExecute:

    def get_input_people_list(self, filepath):
        people = []
        file = open(os.path.join(os.path.dirname(__file__), filepath), "r")
        while True:
            line = file.readline()
            line = line.strip()
            if not line:
                break
            linearr = line.split()
            linearrlen = len(linearr)
            newline = ""
            if linearrlen > 1:
                for x in range(1, linearrlen):
                    newline = newline + " " + linearr[x]
                newline = newline.strip()
                people.append(newline)
        return people

    def get_top_20_friends(self, browser, profile):
        response = browser.open(profile + "/friends")
        html = response.read()
        lines = html.split("\n")
        for line in lines:
            if "friends.search" in line:
                line1 = line.split("https://www.facebook.com/")
                friends = []
                for itr in line1:
                    if not itr.startswith("<div class="):
                        itr = itr.split("\"")[0]
                        if "&amp;" in itr:
                            itr = itr.split("&amp;")[0]
                        if "?fref=pb" in itr:
                            itr = itr.split("?fref=pb")[0]
                        if "?ref=br" in itr:
                            itr = itr.split("?ref=br")[0]
                        if itr.endswith("/"):
                            itr = itr[:-1]
                        itr = "https://www.facebook.com/" + itr.strip()
                        itr = itr.lower()
                        if not itr.startswith(
                                "https://www.facebook.com/pages") and not "university" in itr and not "-" in itr:
                            friends.append(itr)
                friends = list(set(friends))
                return friends

    def visit_profile(self, browser, profile):
        response = browser.open(profile)
        if response:
            print "response exists!"
        else:
            print "response is not existing!"
        html = response.read()
        #print "### read the response"
        lines = html.split("\n")
        dict = {}
        dict["score"] = 0
        dict["score1"] = 0
        dict["score2"] = 0
        dict["profile"] = profile
        dict["actual"] = "na"
        dict["friends"] = self.get_top_20_friends(browser, profile)
        for line in lines:
            if "<title id=\"pageTitle\">" in line:
                dict["name"] = line.split("<title id=\"pageTitle\">")[1].split("</title>")[0]
            if "Profile Photo" in line:
                line1 = ""
                line1 = line.split("Profile Photo")[1].split("src=\"")[1]
                line1 = line1.split("\" /></a></div>")[0]
                if "amp;" in line1:
                    line1 = line1.split("amp;")[0] + line1.split("amp;")[1]
                dict["pic"] = line1
            if "Former" in line or "Studies at " in line or "Studied or " in line or "Lives in " in line or "From " in line:
                line1 = re.sub("<[^>]*>", " ", line)
                line1 = string.replace(line1, "Intro", "")
                line1 = string.replace(line1, "-->", "")
                line1 = string.replace(line1, "  ", " ")
                line1 = line1.strip()
                lines1 = line1.split("        ")
                former = ""
                worked = ""
                went = ""
                studies = ""
                studied = ""
                stays = ""
                home = ""
                current = ""
                for str in lines1:
                    if str.startswith("Former "):
                        former = str
                    elif str.startswith("Worked at "):
                        worked = str
                    elif str.startswith("Went to "):
                        went = str
                    elif str.startswith("Studies "):
                        studies = str
                    elif str.startswith("Studied "):
                        studied = str
                    elif str.startswith("Lives in "):
                        stays = str
                    elif str.startswith("From ") or "From " in str:
                        home = str
                    else:
                        current = str
                dict["education"] = ""
                if studies:
                    dict["education"] = dict["education"] + studies
                if studied:
                    if dict["education"]:
                        dict["education"] = dict["education"] + "; " + studied
                    else:
                        dict["education"] = dict["education"] + studied
                if went:
                    if dict["education"]:
                        dict["education"] = dict["education"] + "; " + went
                    else:
                        dict["education"] = dict["education"] + went
                dict["location"] = ""
                if stays:
                    dict["location"] = dict["location"] + stays
                if home:
                    if dict["location"]:
                        dict["location"] = dict["location"] + "; " + home
                    else:
                        dict["location"] = dict["location"] + home
                dict["work"] = ""
                if current:
                    dict["work"] = dict["work"] + current
                if worked:
                    if dict["work"]:
                        dict["work"] = dict["work"] + "; " + worked
                    else:
                        dict["work"] = dict["work"] + worked
                if former:
                    if dict["work"]:
                        dict["work"] = dict["work"] + "; " + former
                    else:
                        dict["work"] = dict["work"] + former
        return dict

    def login_into_facebook(self, creds_file):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        cookie_jar = cookielib.LWPCookieJar()
        # browser.set_proxies({"http": "111.11.11.11"})
        browser.set_cookiejar(cookie_jar)
        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
        browser.open("https://www.facebook.com/")
        browser.select_form(nr=0)
        filepath = os.path.join(os.path.dirname(__file__), creds_file)
        f = open(filepath, "r")
        data = f.readlines()
        list = []
        for line in data:
            if line:
                line = line.strip()
                list.append(line.split(" ")[0] + " " + line.split(" ")[1])
        random_line = random.choice(list)
        browser.form["email"] = random_line.split(" ")[0]
        browser.form["pass"] = random_line.split(" ")[1]
        print "login: ", browser.form["email"], " :: ", browser.form["pass"]
        browser.submit()
        return browser

    def process(self, browser, url):
        url = browser.open(url)
        response = url.read()
        splits = response.split("<div class=\"_5d-5\">")
        splits_len = splits.__len__()
        users = []
        for i in range(0, splits_len-1):
            curr = splits[i+1]
            name = curr.split("</div>")[0]
            name = name.strip()
            next = splits[i]
            link = next.split("<div class=\"_gll\"><div><a href=\"")[1].split("\" data-testid=\"serp_result_link")[0]
            link = link.strip()
            if "&amp;" in link:
                link = link.split("&amp;")[0]
            if "?fref=pb" in link:
                link = link.split("?fref=pb")[0]
            if "?ref=br" in link:
                link = link.split("?ref=br")[0]
            if link.endswith("/"):
                link = link[:-1]
            link = link.strip()
            link = link.lower()
            user = {}
            user["name"] = name
            user["profile"] = link
            users.append(user)
        return users

    def get_info_about_people(self, input_file, colleges, creds_file, db_host, db_port, replace):
        dicts = []
        base_facebook_search_url = "https://www.facebook.com/search/people/?q="
        db_client = FBDb.connect(db_host, db_port)
        browser = self.login_into_facebook(creds_file)
        people = self.get_input_people_list(input_file)
        for person in people:
            users = []
            person = person.strip()
            person_bkp = person
            person = re.sub("\.", "", person)
            urls = []
            if colleges is not None and len(colleges) > 0:
                for college in colleges:
                    if person.startswith("Md"):
                        urls.append(base_facebook_search_url + person.strip() + " " + college)
                        urls.append(base_facebook_search_url + person.split("Md")[1].strip() + " " + college)
                        urls.append(base_facebook_search_url + "Mohammed " + person.split("Md")[1].strip() + " " + college)
                        urls.append(base_facebook_search_url + "Mohammad " + person.split("Md")[1].strip() + " " + college)
                        if len(person.split("Md")[1].split()) == 3:
                            urls.append(base_facebook_search_url + person.strip().split()[0] + " " + person.strip().split()[1] + " " + person.strip().split()[3] + " " + college)
                            urls.append(base_facebook_search_url + person.split("Md")[1].strip().split()[0] + " " + person.split("Md")[1].strip().split()[2] + " " + college)
                            urls.append(base_facebook_search_url + "Mohammed " + person.split("Md")[1].strip().split()[0] + " " + person.split("Md")[1].strip().split()[2] + " " + college)
                            urls.append(base_facebook_search_url + "Mohammad " + person.split("Md")[1].strip().split()[0] + " " + person.split("Md")[1].strip().split()[2] + " " + college)
                    else:
                        urls.append(base_facebook_search_url + person.strip() + " " + college)
                        if len(person.strip().split()) == 3:
                            urls.append(base_facebook_search_url + person.strip().split()[0] + " " + person.strip().split()[2] + " " + college)
            else:
                if person.startswith("Md"):
                    urls.append(base_facebook_search_url + person.strip())
                    urls.append(base_facebook_search_url + person.split("Md")[1].strip())
                    urls.append(base_facebook_search_url + "Mohammed " + person.split("Md")[1].strip())
                    urls.append(base_facebook_search_url + "Mohammad " + person.split("Md")[1].strip())
                    if len(person.split("Md")[1].split()) == 3:
                        urls.append(base_facebook_search_url + person.strip().split()[0] + " " + person.strip().split()[1] + " " + person.strip().split()[3])
                        urls.append(base_facebook_search_url + person.split("Md")[1].strip().split()[0] + " " + person.split("Md")[1].strip().split()[2])
                        urls.append(base_facebook_search_url + "Mohammed " + person.split("Md")[1].strip().split()[0] + " " + person.split("Md")[1].strip().split()[2])
                        urls.append(base_facebook_search_url + "Mohammad " + person.split("Md")[1].strip().split()[0] + " " + person.split("Md")[1].strip().split()[2])
                else:
                    urls.append(base_facebook_search_url + person.strip())
                    if len(person.strip().split()) == 3:
                        urls.append(base_facebook_search_url + person.strip().split()[0] + " " + person.strip().split()[2])
            for url in urls:
                url = url.strip()
                url = re.sub("\\s+", " ", url)
                url = re.sub(" ", "%20", url)
                users = users + self.process(browser, url)
            new_users = []
            for user in users:
                if user not in new_users:
                    new_users.append(user)
            users = new_users
            print person_bkp, " ==> ", users
            dict = FBDb.find_dict(db_client, "buet3", person_bkp)
            if replace:
                dict = None
                FBDb.remove_dict(db_client, "buet3", person_bkp)
            if dict is None:
                dict = {}
                profiles = []
                for user in users:
                    time.sleep(0.8)
                    print user["profile"]
                    profile = self.visit_profile(browser, user["profile"])
                    if profile is not None:
                        profiles.append(profile)
                dict["person"] = person_bkp
                dict["profiles"] = profiles
                FBDb.store_profile(db_client, "buet3", dict)
            else:
                print "dict already present:\n", dict
            dicts.append(dict)
