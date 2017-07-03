from __future__ import unicode_literals

from django.db import models
from mongoengine import *
from bson.json_util import default
from datetime import datetime

class Employee(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    
class SearchParams(EmbeddedDocument):
    firstName = StringField(max_length=50)
    lastName = StringField(max_length=50)
    school = StringField(max_length=500)
    keywords = ListField(StringField(), default=list)
    title = StringField(max_length=500)
    company = StringField(max_length=100)
    postalCode = StringField(max_length=10)
    distance = StringField()
    locationType = StringField(max_length=50)
    countryCode = StringField(max_length=10)
    titleScope = StringField()
    rsid = IntField()
    openAdvancedForm = BooleanField()
    orig = StringField()
    
class SearchParamsWrapper(EmbeddedDocument):
    searchParams = EmbeddedDocumentField(SearchParams)
    
class LogoResultBase(EmbeddedDocument):
    altText = StringField(default=None)
    key = StringField(default=None)
    useGlyphGhost = StringField(default=None)
    className = StringField(default=None)
    width = StringField(default=None)
    generateUrl = StringField(default=None)
    inlineParams = StringField(default=None)
    genericGhostImage = StringField(default=None)
    ghostImage60 = StringField(default=None)
    height = StringField(default=None)
    media_picture_link = StringField(default=None)
    media_picture_link_100 = StringField(default=None)
    media_picture_link_200 = StringField(default=None)
    media_picture_link_400 = StringField(default=None)
    pictureId = StringField(default=None)
    type = StringField(default=None)
    
class ProfilePhoto(EmbeddedDocument):
    genericGhostImage = StringField(default=None)
    media_picture_link = StringField(default=None)
    media_picture_link_100 = StringField(default=None)
    media_picture_link_200 = StringField(default=None)
    media_picture_link_400 = StringField(default=None)
    
class PhotoWrapper(EmbeddedDocument):
    profilePhoto = EmbeddedDocumentField(ProfilePhoto)
    
class Person(EmbeddedDocument):
    authToken = StringField(max_length=10)
    fmt_location = StringField()
    linkAuto_voltron_people_search_1 = StringField()
    fmt_industry = StringField()
    personId = IntField()
    isNameMatch = BooleanField(default=True)
    authType = StringField()
    isContact = BooleanField(default = False)
    link_nprofile_view_3 = StringField()
    fmt_name = StringField()
    link_nprofile_view_4 = StringField()
    isConnectedEnabled = BooleanField(default = False)
    connectionCount = IntField()
    displayLocale = StringField()
    isProfilePic = BooleanField(default = False)
    firstName = StringField()
    lastName = StringField()
    isHeadless = BooleanField(default = False)
    link_voltron_people_search_5 = StringField()
    isBookmarked = BooleanField(default = False)
    fmt_headline = StringField()
    profilePhoto = EmbeddedDocumentField(PhotoWrapper)
    logo_result_base = EmbeddedDocumentField(LogoResultBase)
    
class PersonWrapper(EmbeddedDocument):
    person = EmbeddedDocumentField(Person)

class Record(EmbeddedDocument):
    email = EmailField(required=True, unique=True)
    searchParams = EmbeddedDocumentField(SearchParams)
    isUserUpdated = BooleanField(default=False)
    resultCount = IntField(default=0)
    #dateCreated = DateTimeField(default = datetime.utcnow(), auto_now_add=True)
    #dateCreated = DateTimeField(default = datetime.utcnow(), auto_now_add=True)
    dateCreated = DateTimeField(default = datetime.utcnow(), null=True)
    dateUpdated = DateTimeField(default = datetime.utcnow(), null=True)
    createdBy = StringField(default='System')
    updatedBy = StringField(default='System')
    isEmailSent = BooleanField(default = False)
    emailCount = IntField(default=0)
    results = EmbeddedDocumentListField(PersonWrapper)

class DBRecord(Document):
    record = EmbeddedDocumentField(Record)

class CSPerson(Document):
    person = EmbeddedDocumentField(Person)