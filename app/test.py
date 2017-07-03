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

# print graph.request(id + "/picture")
browser = mechanize.Browser()
browser.set_handle_robots(False)
cookie_jar = cookielib.LWPCookieJar()
browser.set_cookiejar(cookie_jar)
browser.set_handle_equiv(True)
browser.set_handle_redirect(True)
browser.set_handle_referer(True)
browser.set_handle_robots(False)
browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
browser.addheaders = [('User-agent',
                       'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
# browser.open("http://www.facebook.com/" + id)
# browser.set_proxies({'http':'notional-sign-110911.appspot.com'})
browser.open("http://www.facebook.com/")
browser.select_form(nr=0)
browser.form["email"] = "indervir.banipal@utdallas.edu"
browser.form["pass"] = "utdallas@123"
browser.submit()
# return response.read()

url = "http://www.facebook.com/100010856658863"
url = browser.open(url)
response = url.read()
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
            dict["current"] = current
            dict["past"] = past
            dict["past_worked"] = past_worked
            dict["went_to"] = went_to
            dict["studying"] = studying
            dict["studied"] = studied
            dict["stays"] = stays
            dict["home"] = home
            print dict