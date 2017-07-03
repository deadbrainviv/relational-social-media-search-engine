import cookielib
import os
import urllib
import urllib2
import re
import sys
import json
import pymongo
import datetime
from models import Employee, Record, DBRecord, Person, PersonWrapper
from bs4 import BeautifulSoup
# import html5lib 
from bs4 import Comment
import logging
import requests


class People(object):
	def __init__(self, firstName, lastName, email):
		self.firstName = firstName
		self.lastName = lastName
		self.email = email