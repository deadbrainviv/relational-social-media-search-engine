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

from FBDb import *

class FBExecute:

    def __init__(self, db_host, db_port, colleges):
        self.db_host = db_host
        self.db_port = db_port
        self.colleges = colleges
        self.db_client = FBDb.connect_db(self.db_host, self.db_port)
        self.db = self.db_client.facebook_db

    def get_facebook_token(self,filepath):
        file = open(filepath, "r")
        while True:
            line = file.readline()
            line = line.strip()
            return line

    def get_input_people_list(self,filepath):
        people = []
        file = open(filepath, "r")
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
                people.append(newline)
        return people

    def visit_profile(self, browser, name, id):
        # print graph.request(id + "/picture") # for getting the picture
        url = "http://www.facebook.com/" + id
        url = browser.open(url)
        response = url.read()
        #print response
        lines = response.split("\n")
        dict = {}
        for line in lines:
            if "Followed by" in line:
                line = line.split("Followed by")[0]
            if "Former" in line or "Studies at " in line or "Studied or " in line or "Lives in " in line or "From " in line:
                line = re.sub("<[^>]*>", " ", line)
                line = string.replace(line, "Intro", "")
                line = string.replace(line, "-->", "")
                line = string.replace(line, "  ", " ")
                line = line.strip()
                lines = line.split("        ")
                current = []
                past = []
                past_worked = []
                went_to = []
                studying = []
                studied = []
                stays = []
                home = []
                for str in lines:
                    if str.startswith("Former "):
                        str = str.split("Former ")[1]
                        past.append(str)
                    elif str.startswith("Worked at "):
                        str = str.split("Worked at ")[1]
                        past_worked.append(str)
                    elif str.startswith("Went to "):
                        str = str.split("Went to ")[1]
                        went_to.append(str)
                    elif str.startswith("Studies "):
                        str = str.split("Studies ")[1]
                        studying.append(str)
                    elif str.startswith("Studied "):
                        str = str.split("Studied ")[1]
                        studied.append(str)
                    elif str.startswith("Lives in "):
                        str = str.split("Lives in ")[1]
                        stays.append(str)
                    elif str.startswith("From ") or "From " in str:
                        str = str.split("From ")[1]
                        home.append(str)
                    else:
                        current.append(str)

                dict["image"] = graph.request(id + "/picture")
                dict["name"] = name
                dict["profile"] = "https://www.facebook.com/" + id

                dict["university"] = ""
                partition = ""
                if not dict["studying"]:
                    dict["education"] = studying + " (current) "
                    partition = "| "
                if not dict["studied"]:
                    dict["education"] = dict["education"] + partition + studied + " (past)"
                partition = ""

                dict["work"] = ""
                partition = ""
                if not dict["current"]:
                    dict["work"] = current + " (current) "
                    partition = "| "
                if not dict["studied"]:
                    dict["education"] = dict["education"] + partition + studied + " (past)"
                partition = ""

                dict["current"] = current
                dict["past"] = past
                dict["past_worked"] = past_worked
                dict["went_to"] = went_to
                dict["stays"] = stays
                dict["home"] = home
                return dict

    def login_into_facebook(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        cookie_jar = cookielib.LWPCookieJar()
        browser.set_cookiejar(cookie_jar)
        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
        browser.open("http://www.facebook.com/")
        browser.select_form(nr=0)
        browser = self.get_creds(browser)
        browser.submit()
        #return response.read()
        return browser

    def get_creds(self, browser):
        f = open("C:\\Users\\IndervirSingh\\Documents\\GitHub\\fbsearch\\properties\\logins.txt", "r")
        data = f.readlines()
        for line in data:
            if line.startswith("*"):
                line = line.strip()
                line = line.split(" ")
                browser.form["email"] = line[0].split("*")[1]
                browser.form["pass"] = line[1]
                break
        return browser

    def extract_users(self,input):
        users = []
        for user in input["data"]:
            users.append(user)
        return users

    def get_info_about_people(self,token, people):
        dicts = []
        graph = facebook.GraphAPI(token)
        for person in people:
            person = person.strip()
            users = []
            if person.startswith("Md."):
                for college in self.colleges:
                    query = "search/?q=Mohammed " + person.split("Md.")[1] + " " + college + "&type=user"
                    users = users + self.extract_users(graph.request(query))
                    query = "search/?q=Mohammad " + person.split("Md.")[1] + " " + college + "&type=user"
                    users = users + self.extract_users(graph.request(query))
                    query = "search/?q=" + person + " " + college + "&type=user"
                    users = users + self.extract_users(graph.request(query))
            else:
                for college in self.colleges:
                    query = "search/?q=" + person + " " + college + "&type=user"
                    users = users + self.extract_users(graph.request(query))
            browser = self.login_into_facebook()
            #print person, " ==> ", users
            for user in users:
                dict = FBDb.find_entry_in_db(self.db, user["id"])
                if dict is None:
                    dict = self.visit_profile(browser, user["name"], user["id"])
                    if dict is not None:
                        FBDb.store_in_db(dict, self.db)
                dicts.append(dict)
                time.sleep(1.0)
            #print person, " ==> ", str(len(dicts))
        return dicts