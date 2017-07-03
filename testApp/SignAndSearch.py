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

logging.basicConfig(filename='log_file.txt',level=logging.INFO)
username = "anandrox1991@gmail.com"
password = "chandraisgr8"
username = "bxm142230@utdallas.edu"
password = ""
dbHost = 'localhost' #found from the hostname() command in mongo.
dbPort = 27017
# dbName = 'test2'
dbName='test2'
dbCollection = 'd_b_record'
url1 = 'https://www.linkedin.com/'
linkedInHome = 'https://www.linkedin.com/'
linkHome = 'http://www.linkedin.com/nhome'
# url1 = 'www.linkedin.com/'
# linkedInHome = 'www.linkedin.com/'
# linkHome = 'www.linkedin.com/nhome'
lSrchTitle = 'Search | LinkedIn'
contentKey = 'content'
curEducationHTMLKey = 'educationHtml'
curEducationKey = 'education'
gReqParamsKey = 'global_requestParams'
pageKey = 'page' #NEED
unifiedSearchKey = 'voltron_unified_search_json'
searchKey = 'search' #NEED
advSearchFormKey = 'advancedSearchForm'
searchFieldsKey = 'searchFields'
baseDataKey = 'baseData' #for result count
resultCountKey = 'resultCount' #NEED
resultPaginationKey = 'resultPagination'
pagesPaginationKey = 'pages'
resultsKey = 'results'
recordKey = 'record'
emailKey ='email'
searchParamsKey = 'searchParams'
userUpdateKey = 'isUserUpdated'
rsltCountKey = 'resultCount'
dateCreateKey = 'dateCreated'
dateUpdateKey = 'dateUpdated'
createByKey = 'createdBy'
updateByKey = 'updatedBy'
emailSentKey = 'isEmailSent'
emailSentCountKey = 'emailCount'
personKey = 'person'
systemVal = 'System'
searchURL = "https://www.linkedin.com/vsearch/p?firstName=Bala&lastName=Yadav&openAdvancedForm=true&locationType=Y&rsid=4764583901457977599432&orig=MDYS"
# searchURL = "www.linkedin.com/vsearch/p?firstName=Bala&lastName=Yadav&openAdvancedForm=true&locationType=Y&rsid=4764583901457977599432&orig=MDYS"

#person related keys
authTokenKey = 'authToken'
authTypeKey = 'authType'
connecCountKey = 'connectionCount'
localeKey = 'displayLocale'
encryptedIdKey = 'encryptedId'
encryptResltKey = 'encryptedResultId'
firstNameKey = 'firstName'
headlineKey = 'fmt_headline'
snippetKey = 'snippets'
fieldNameKey = 'fieldName'  #   Mandal   
bodyListKey = 'bodyList'    #   Mandal
curIndustryKey = 'fmt_industry'
curLocKey = 'fmt_location'
prflNameKey = 'fmt_name'
personIdKey = 'personId'
bookmarkKey = 'isBookmarked'
connectEnableKey = 'isConnectedEnabled'
contactKey = 'isContact'
headlessKey = 'isHeadless'
nameMatchKey = 'isNameMatch'
lastNameKey = 'lastName'
searchLink1Key = 'linkAuto_voltron_people_search_1'
searchLink2Key = 'link_voltron_people_search_5'
profileLink1Key = 'link_nprofile_view_3'
profileLink2Key = 'link_nprofile_view_4'
resultIndexKey = 'resultIndex'
logoBaseKey = 'logo_result_base'
isProfilePic = 'isProfilePic'
profilePhoto = 'profilePhoto'
genericGhostImageKey = 'genericGhostImage'
mediaPicDefKey = 'media_picture_link'
mediaPic100Key = 'media_picture_link_100'
mediaPic200Key = 'media_picture_link_200'
mediaPic400Key = 'media_picture_link_400'
personListKey = 'personList'
emptyString = 'EMPTY'
#general strings
equalTo = '='
amper = '&'
spaceV = '%20'
amperV = '%26'
#URL forming constants
searchBaseURL = 'https://www.linkedin.com/vsearch/p?{0}openAdvancedForm=true&locationType=Y&rsid=4764583901459185729672&orig=ADVS'
paramBaseURL = 'https://www.linkedin.com/vsearch/p?{0}openAdvancedForm=true&{1}{2}{3}rsid=4764583901459312896588&orig=MDYS'
# searchBaseURL = 'www.linkedin.com/vsearch/p?{0}openAdvancedForm=true&locationType=Y&rsid=4764583901459185729672&orig=ADVS'
# paramBaseURL = 'www.linkedin.com/vsearch/p?{0}openAdvancedForm=true&{1}{2}{3}rsid=4764583901459312896588&orig=MDYS'

titleScopeParam = 'titleScope=CP&'
schoolScopeParam = 'school='
companyScopeParam = 'companyScope=CP&'
locationNoSelectParam = 'locationType=Y&'
locationSelectParam = 'locationType=I&'
proxy_url = 'http://notional-sign-110911.appspot.com/'
anyurl = 'www.google.com'

university_choice=''

cookie_filename = "parser.cookies.txt"

class Authenticate(object):
    trialCount = 0;
    def __init__(self, login, password):
        """ Start up... """
        self.login = login
        self.password = password
        # Simulate browser with cookies enabled
        self.cj = cookielib.MozillaCookieJar(cookie_filename)
        '''
        Creating settings for the proxy
        '''
        # proxy_handler = urllib2.ProxyHandler({'http':'209.222.25.83:3128'})
        # 216.58.194.113
        # proxy_handler = urllib2.ProxyHandler({'http':'8.8.8.8'})

        proxy_handler = urllib2.ProxyHandler({'http':'notional-sign-110911.appspot.com'})
        # proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
        if os.access(cookie_filename, os.F_OK):
            self.cj.load()
        self.opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(debuglevel=0),
            urllib2.HTTPSHandler(debuglevel=0),
            proxy_handler,
            urllib2.HTTPCookieProcessor(self.cj)
        )

        self.opener.addheaders = [
            ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                           'Windows NT 5.2; .NET CLR 1.1.4322)'))
        ]
        
    
    def performCSSearch(self, searchParams, dbHost, dbPort, dbName):
        """ Performs search and Saves the information gathered into DB. This method almost performs everything this class is created for """
        print "INSIDE PERFORM CS SEARCH"
        try:
            #self.login = login
            #self.password = password
            # Simulate browser with cookies enabled
            # self.cj = cookielib.MozillaCookieJar(cookie_filename)
            # if os.access(cookie_filename, os.F_OK):
            #     self.cj.load()
            # self.opener = urllib2.build_opener(
            #     urllib2.HTTPRedirectHandler(),
            #     urllib2.HTTPHandler(debuglevel=0),
            #     urllib2.HTTPSHandler(debuglevel=0),
            #     urllib2.HTTPCookieProcessor(self.cj)
            # )
            # self.opener.addheaders = [
            #     ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
            #                    'Windows NT 5.2; .NET CLR 1.1.4322)'))
            # ]
            self.checkLogin(url1)
            # print "LOCATIONS LIST"
            # print searchParams['locations']
            # print "LOCATIONS"
            # print request.session.get('locations')
            print "OTHER DETAILS"
            fName = searchParams['firstName']
            mailId = searchParams['email']
            print fName
            print mailId
            # if fName == 'EMPTY' or mailId == 'EMPTY':
                # raise Exception('Info: Search has to be performed from Search page only, Please try again', 'Info')
            print "Search Params : "
            print searchParams
            fSrchURL = self.formSearchURL(searchParams)
            # print fSrchURL
            print "Printing URLs formed"
            # for f in fSrchURL:
            print fSrchURL[0]
            print fSrchURL[1]
            linkedJSON = self.loadSearch(fSrchURL[1], fName)
            print "Extracted COMMENTS"  
            # print linkedJSON
            self.formCSRecord(linkedJSON, dbHost, dbPort, dbName, mailId, searchParams['locations'])
            return 'Success'
        except Exception as e:
            x,y = e.args
            print x
            print e
            return x

    # IN USE
    def performSearch(self, searchParams, dbHost, dbPort, dbName):
        """ Performs search and Saves the information gathered into DB. This method almost performs everything this class is created for """
        print "inside Perform Search ... "
        try:
            #self.login = login
            #self.password = password
            # Simulate browser with cookies enabled
            self.cj = cookielib.MozillaCookieJar(cookie_filename)
            if os.access(cookie_filename, os.F_OK):
                self.cj.load()
            self.opener = urllib2.build_opener(
                urllib2.HTTPRedirectHandler(),
                urllib2.HTTPHandler(debuglevel=0),
                urllib2.HTTPSHandler(debuglevel=0),
                urllib2.HTTPCookieProcessor(self.cj)
            )
            self.opener.addheaders = [
                ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                               'Windows NT 5.2; .NET CLR 1.1.4322)'))
            ]
            self.checkLogin(url1)
            fName = searchParams['firstName']
            lName = searchParams['lastName']
            mailId = searchParams['email']
            university = searchParams['school']
            university_choice = university
            if fName == 'EMPTY' or mailId == 'EMPTY':
                raise Exception('Info: Search has to be performed from Search page only, Please try again', 'Info')
            fSrchURL = self.formSearchURL(searchParams)
            linkedJSON = self.loadSearch(fSrchURL, fName)
            print "LinkedJSON"
            print linkedJSON
            recordJSON = self.formTrimmedJSON(linkedJSON)
            dbRecord = self.formDBRecord(recordJSON, mailId)


            client = self.connect2DB(dbHost, dbPort)
            # print "Client details : "+client.__str__()
            self.store2DB(dbRecord, mailId, client)
            return 'Success'
        except Exception as e:
            x,y = e.args
            return x
    
    def extractLinkedInPagination(self, params, dbHost, dbPort, dbName):
        '''
        function to extract all the students of university from LinkedIn search.
        '''
        # linkObj = Authenticate('bxm142230@utdallas.edu','bk11mandal#')
        searchBaseURL2 = 'https://www.linkedin.com/vsearch/p?{0}&openAdvancedForm=true&locationType=Y'

        link_firsthalf = 'https://www.linkedin.com/vsearch/p?'
        #University%20of%20Texas%20at%20Dallas
        link_secondhalf = '&openAdvancedForm=true&locationType=Y'
        paramString = ''
        # pKeys = params.keys() #getting the parameters.
        # for key in pKeys:       # for each parameter, check
        #     if key == 'email':
        #         continue
        #     val = params[key]
        #     if val is None or val == '':
        #         continue
        #     val = val.replace(' ',spaceV) #replace spaces with %20, for making URLs ahead
        #     val = val.replace(amper, amperV) # replace ampersands with %26, for making URLs ahead
        #     paramString = paramString + key + equalTo + val + amper #making the complete URL for the profile
        val = params['school']
        val = val.replace(' ',spaceV)
        paramString = paramString + val + amper
        
        # tX = ''
        # cX = ''
        # if 'title' in pKeys:
        #     tX = titleScopeParam #this is as per the variables in a linkedIn URL
        # if 'company' in pKeys:
        #     cX = companyScopeParam # as per variables in the linkedIn URL
        # if 'postalCode' in pKeys:
        #     lX = locationSelectParam # as per variable in the linkedIn URL
        # else:
        #     lX = locationNoSelectParam
        paramString = schoolScopeParam+paramString
        print "INSIDE PARAM_STRING "
        print paramString    

        srchURL = searchBaseURL2.format(paramString) 
        print "SRCH URL"
        print srchURL
        html = self.loadPage(srchURL)
        print "HTML RESULTS"
        print html[:30]
        soup = BeautifulSoup(html)
        
        # comments = spContent.findAll(text=lambda text:isinstance(text, Comment))
        # for c in comments:
        #     c.extract()
        #START WORK From here

        '''
        Complete below code the same way as loadPage and extractPerson
        '''
        # linkedJSON = self.loadSearch(fSrchURL, fName)
        #     recordJSON = self.formTrimmedJSON(linkedJSON)
        #     dbRecord = self.formDBRecord(recordJSON, mailId)
        #     client = self.connect2DB(dbHost, dbPort)
        #     # print "Client details : "+client.__str__()
        #     self.store2DB(dbRecord, mailId, client)

        # cLen = len(comments)
        # if cLen > 0 and cLen > 11:
        #     comment = comments[11]
        # if comment is None:
        #     for cmnt in comments:
        #         if firstName in cmnt:
        #             comment = cmnt
        # print "output COMMENTS :"
        # #print comment            
        # return comment

        linkedJSON = self.loadSearch(srchURL)
        # mod_results = soup.find_all("li",re.compile("^mod"))
        # if mod_results is None:
        #     print "NO MOD_RESULTS"
        # else:
        #     print "MOD RESULTS OBTAINED"
        # print mod_results
        print "Linked JSON"
        # print linkedJSON[:3000]

        rawResults = re.sub('\\\\u003c','<',linkedJSON)
        rawResults = re.sub('\\u003cB\\u003e','\"\"',rawResults)
        print "FORMING TRIMMED JSON"
        try:
            # self.formTrimmedJSONadvanced(rawResults)
            rawJSON = json.loads(rawResults)
            # print "RAW JSON"
            contentPart = rawJSON[contentKey]
            pagePart = contentPart[pageKey]
            # print "CONTENT PART"
            unifiedSearchPart = pagePart[unifiedSearchKey]
            searchPart = unifiedSearchPart[searchKey]
            # print searchPart
            # print "SEARCH PART"
            baseDataPart = searchPart[baseDataKey]

            '''
            Result Pagination Parts
            '''
            paginationPart = baseDataPart[resultPaginationKey]
            # pagesPaginationKey

            nextPageLinks = []
            for page in paginationPart[pagesPaginationKey]:
                keys = page.keys()
                isCurrentPage = page['isCurrentPage']
                pageURL = page['pageURL']
                pageNum = page['pageNum']
                pagelink = { 'isCurrentPage':isCurrentPage, 'pageNum':pageNum, 'pageURL':pageURL }
                # print pagelink
                
                nextPageLinks.append(pagelink)
            # print paginationPart
            
            '''
            Person Details
            '''
            resultsPart = searchPart[resultsKey]
            print "Getting Keys"
            for r in resultsPart:
                keyset = r.keys()
                if personKey in keyset:
                    personPart = r[personKey]
                # if personPart == 'person':
                #     continue
                # else:
                    print personPart['fmt_name']
                    '''
                    and probably get all essential details.
                    Collect all person details into person
                    Objects.
                    '''
                    personObj = r[personKey]
                    




        except Exception as e:
            print e

        
        # rawJSON = json.loads(rawResults)



            # further_part = m.find_all("a")
            # for atag in further_part:
            #     if atag.parent.name == 'h3':
            #         print atag['href']



        # fName = searchParams['firstName']
        # mailId = searchParams['email']
        # if fName == 'EMPTY' or mailId == 'EMPTY':
        #     raise Exception('Info: Search has to be performed from Search page only, Please try again', 'Info')
        # fSrchURL = self.formSearchURL(searchParams)
        # linkedJSON = self.loadSearch(fSrchURL, fName)
        # recordJSON = self.formTrimmedJSON(linkedJSON)
        # dbRecord = self.formDBRecord(recordJSON, mailId)
        # client = self.connect2DB(dbHost, dbPort)
        # print "Client details : "+client.__str__()
        # self.store2DB(dbRecord, mailId, client)
        return 'Success'

    
    def performFullSearch(self, searchParams, dbHost, dbPort, dbName):
        """ Performs search and Saves the information gathered into DB. This method almost performs everything this class is created for """
        print "inside Perform Search ... "
        try:
            #self.login = login
            #self.password = password
            # Simulate browser with cookies enabled
            self.cj = cookielib.MozillaCookieJar(cookie_filename)
            if os.access(cookie_filename, os.F_OK):
                self.cj.load()
            self.opener = urllib2.build_opener(
                urllib2.HTTPRedirectHandler(),
                urllib2.HTTPHandler(debuglevel=0),
                urllib2.HTTPSHandler(debuglevel=0),
                urllib2.HTTPCookieProcessor(self.cj)
            )
            self.opener.addheaders = [
                ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                               'Windows NT 5.2; .NET CLR 1.1.4322)'))
            ]
            self.checkLogin(url1)
            fName = searchParams['firstName']
            mailId = searchParams['email']
            if fName == 'EMPTY' or mailId == 'EMPTY':
                raise Exception('Info: Search has to be performed from Search page only, Please try again', 'Info')
            fSrchURL = self.formSearchURL(searchParams)
            linkedJSON = self.loadSearch(fSrchURL, fName)
            recordJSON = self.formTrimmedJSON(linkedJSON)
            dbRecord = self.formDBRecord(recordJSON, mailId)
            client = self.connect2DB(dbHost, dbPort)
            print "Client details : "+client.__str__()
            self.store2DB(dbRecord, mailId, client)
            return 'Success'
        except Exception as e:
            x,y = e.args
            return x

    def filterResult(self, filterParams, dbHost, dbPort, dbName):
        """Performs a filter based on the filter parameters """
        print "Inside Filter Result view ..."
        try:
            self.cj = cookielib.MozillaCookieJar(cookie_filename)
            if os.access(cookie_filename, os.F_OK):
                self.cj.load()
            self.opener = urllib2.build_opener(
                urllib2.HTTPRedirectHandler(),
                urllib2.HTTPHandler(debuglevel=0),
                urllib2.HTTPSHandler(debuglevel=0),
                urllib2.HTTPCookieProcessor(self.cj)
            )
            self.opener.addheaders = [
                ('User-agent', ('Mozilla/4.0 (compatible; MSIE 6.0; '
                               'Windows NT 5.2; .NET CLR 1.1.4322)'))
            ]
            self.checkLogin(url1)

            ## start here ##
            print " Data So Far : \n"+Person.objects.all()
            return 'Success'

        except Exception as e:
            x,y = e.args
            return x       
        
    def connect2DB(self, dbHost, dbPort):
        """ This definition connects to db using the details provided and returns the client"""
        print "inside connect2DB .. "
        try:
            client = pymongo.MongoClient(dbHost, dbPort)
            print "CLIENT DETAILS"
            print client
            return client
        except pymongo.errors.ServerSelectionTimeoutError as err:
            raise Exception('Error: There is some problem connecting to Database, Please check connection and retry again, Note: data is not cached', 'Error')
        
    def saveToDB(self, client, json):
        """ Persists the JSON to the db using the client """
        db = client.linkedinTest
        db.users.save(json)
        
    def findEntryInDB(self, db, email):
        """ Returns true if it finds an entry with the email provided """
        entries = db.d_b_record.find({'record.email':{'$eq':email}})
        if entries.count() is 0:
            return False
        return True
    
    def djangoTest(self):
        try:
            val = 24;
            c = val/0
            return 'bala'
        except:
            return 'SUCCESS'
    
    # IN USE
    def store2DB(self, json2Store, email, dbClient):
        """ Persists the document to the DB using the dbClient, if the record is already present, it simply replaces the document """
        #db = dbClient.linkedinTest
        print "Inside store2DB ... "
        db = dbClient.test2 # CHange the test2 to any other new database name as per requirement.
        print "DB client is : "+db.__str__()

        if self.findEntryInDB(db, email):
            db.d_b_record.replace_one({'record.email':email},json2Store)
        else:
            self.insertRecord(json2Store, db)
    
    def storeCSRecord(self, json2Store, pId, dbClient):
        print "STORING CS RECORD"
        print pId
        print dbClient
        db = dbClient.test2
        print db
        entries = db.c_s_person.find({'person.personId':{'$eq':pId}})
        print "Entries Count"
        print entries.count()
        if entries.count() is 0:
            print "No ENTRIES"
            print "Saving Record"+json2Store.__str__()
            db.c_s_person.save(json2Store)
        else:
            print "Found ENTRIES"
            db.c_s_person.replace_one({'person.personId':pId}, json2Store)
        # entries = db.c_s_person.find()
        
        
    # IN USE
    def insertRecord(self, record, db):
        """ Simple Insert into DB """
        print "saving record : "+record.__str__()
        db.d_b_record.save(record)
        
        
    def readSearchParams(self):
        """ Incase of UI issues, this method reads the search params and returns the JSON with search params """
        mailId = raw_input("Enter email ")
        firstName = raw_input('Enter First Name* ')
        lastName = raw_input('Enter Last Name ')
        school = raw_input('School ')
        title = raw_input('title ')
        params = {emailKey:mailId, 'firstName':firstName,'lastName':lastName, 'school':school, 'title':title}
        pJSON = json.dumps(params)
        return json.loads(pJSON) 
    
    def formSearchURL(self, params): #Here the parameters are converted to the URL.
        """ Creates the search url using the params """
        print "ENTERED FORM SEARCH URL"
        Links = []
        if params is None:
            return url1
        paramString = ''
        paramString2 = ''
        pKeys = params.keys() #getting the parameters.
        for key in pKeys:       # for each parameter, check
            if key == 'email':

                val2 = params[key]
                if(val2==' '):
                    continue
                val2 = val2.replace(' ',spaceV)
                val2 = val2.replace(amper, amperV)
                paramString2 = paramString2 + key + equalTo + val2 + amper
                continue
            if key == 'locations':
                continue
            val = params[key]
            if val is None or val == '':
                continue
            val = val.replace(' ',spaceV) #replace spaces with %20, for making URLs ahead
            val = val.replace(amper, amperV) #replace ampersands with %26, for making URLs ahead
            paramString = paramString + key + equalTo + val + amper #making the complete URL for the profile
            paramString2 = paramString2 + key + equalTo + val +amper
        print "INSIDE formSearchURL and PARAM_STRING "
        print paramString    
        print paramString2
        tX = ''
        cX = ''
        if 'title' in pKeys:
            tX = titleScopeParam #this is as per the variables in a linkedIn URL
        if 'company' in pKeys:
            cX = companyScopeParam # as per variables in the linkedIn URL
        if 'postalCode' in pKeys:
            lX = locationSelectParam # as per variable in the linkedIn URL
        else:
            lX = locationNoSelectParam
        srchURL = paramBaseURL.format(paramString, tX, cX, lX) 
        srchURL2 = paramBaseURL.format(paramString2, tX, cX, lX)
        print "1st SEARCH URL (without email)"
        print srchURL
        print "2nd SEARCH URL (with email)"
        print srchURL2
        Links.append(srchURL)

        Links.append(srchURL2)
        # paramBaseURL is defined at the top, the {0}, {1} etc. positions are filled with the respictive indexed parameters
        return Links
    
    def checkLogin(self, homeUrl):
        """ checks if the user has already logged in into Linkedin """
        print "Inside Checklogin"
        homepage = self.loadPage(homeUrl)
        print "homeURL loaded"
        homeSoup = BeautifulSoup(homepage)#, "html5lib")
        print "Soup formed"
        if homeSoup.find('form', 'login-form') is not None:
            self.loginPage()
            self.confirmLogin(homeUrl)
            
    def confirmLogin(self, homeUrl):
        """ Confirms if the user has already logged in, raises an exception if there is any issue with Credentials """
        # proxy_url = "http://notional-sign-110911.appspot.com/"
        homepage = self.loadPage(homeUrl)
        homeSoup = BeautifulSoup(homepage)
        if homeSoup.find('form', {'class':'login-form'}) is not None:
            raise Exception('Error: There is some problem signing into LinkedIn, Please check Credentials', 'Error')
             
    def loadPage(self, url, data=None):
        """
        Utility function to load HTML from URLs for us with hack to continue despite 404
        """

        
        print "LOADPAGE"
        # print "Full URL"
        # full_url = ''
        # full_url = proxy_url+url
        # full_url = proxy_url.join(url)
        # print full_url
        # print "URL"
        # print url
        # print proxy_url

        try:
            self.trialCount = self.trialCount+1;
            if data is not None:
                response = self.opener.open(url, data)
                print "Data Not None"
                # print response
            else:
                print "Data is None"
                response = self.opener.open(url)
                # print response
            self.trialCount = 0    
            return ''.join(response.readlines())
        except:
            print "LoadPage Exception"
            # If URL doesn't load for ANY reason, try again for 5 times...
            # Quick and dirty solution for 404 returns because of network problems
            # after 5 trials, the program will terminate
            if self.trialCount < 5:
                #print 'There is some problem loading the page, might be a network issue or Linkedin might be down. Retrying again.'
                return self.loadPage(url, data)
            else:
                errMsg = 'There is some problem loading the page - URL: {0}'.format(url)
                sys.exit(errMsg)

    def loginPage(self, homeURL='https://www.linkedin.com/', loginURL='https://www.linkedin.com/uas/login-submit'):
    # def loginPage(self, homeURL='www.linkedin.com/', loginURL='www.linkedin.com/uas/login-submit'):
        """
        Handle login. This should populate our cookie jar.
        """
        # proxy_url = 
        # proxy_url = "http://notional-sign-110911.appspot.com/"


        html = self.loadPage(homeURL)
        soup = BeautifulSoup(html)
        csrf = soup.find(id="loginCsrfParam-login")['value']        

        login_data = urllib.urlencode({
            'session_key': self.login,
            'session_password': self.password,
            'loginCsrfParam': csrf,
        })
        print "Login Now Processing"
        html = self.loadPage(loginURL, login_data)
        return

    def loadTitle(self, url=linkHome):
        """
        Simple function to test if the correct page has been loaded, by checking the title; This assumes that every page loaded has a title element.
        """
        html = self.loadPage(url)
        soup = BeautifulSoup(html)
        title = soup.find('title')
        if title is None:
            return None
        return title.string
    
    def printJSON(self, rJSON):
        keys = rJSON.keys()
        for key in keys:
            print key +' = '+rJSON[key]
        
    def printAdvSearchFields(self, searchFields):
        if searchFields is None:
            return
        for field in searchFields:
            if 'value' in field.keys():
                print field['labelName']+' : '+field['value']   
    
                  
    def loadSearch(self, url, firstName='results'):
        """
        Loads the search page using the url provided and returns raw search results
        """
        print " inside loadSearch .."

        '''
        97.77.104.22:80
        174.129.204.124:80
        '''
        proxy = {
            "http":"209.222.25.83:3128",
        }
        headers = {'Accept-Encoding': 'identity'}
        html2 = requests.get(url, proxies=proxy, headers=headers)
        print "HTML 2"
        # print html2.content
        # html = html2.content
        html = self.loadPage(url)
        print "SPAGE"
        # print sPage[:200]
        spContent = BeautifulSoup(html)
        
        #title = spContent.find('title')
        #if title is not None:
            #if title.string is not lSrchTitle:
                #sys.exit('There is some problem with url provided, it does not correspond to Linkedin Search')
        comment = None
        comments = spContent.findAll(text=lambda text:isinstance(text, Comment))
        print "COMMENTS"
        # print comments
        # print " >> BEAUTIFULSOUP FINDALL"
        #print comments
        cLen = len(comments)
        print "Length of COmments"+cLen.__str__()
        if cLen > 0 and cLen > 11:
            comment = comments[11]  
        if comment is None:
            for cmnt in comments:   
                if firstName in cmnt:
                    comment = cmnt
        print "output COMMENTS :"
        # print comment            
        return comment
                
    def formFullJSON(self, srchResult):
        """
        This is full JSON method, i.e. it forms the JSON with extensive information including all possible (or public) information. This increases the size of the document considerably
        """
        logging.info('::::::::::: JSON from the linkedIn URl ::::::::::::')
        
        if srchResult is None:
            sys.exit('There is some problem with loading search page and search results')
        rawResults = re.sub('\\\\u002d1', '\"\"', srchResult)
        print "-------------------------------------------------------------------------------"
        print "Form FULL JSON "
        print rawResults
        print "\n"
        try:
            rawJSON = json.loads(rawResults)
            fContent = rawJSON[contentKey]
            globalReqParams = fContent[gReqParamsKey]
            #below line is just to print request params, we can liberally remove /comment below line
            #self.printJSON(globalReqParams)
            fPageRes = fContent[pageKey]
            unifiedSearch = fPageRes[unifiedSearchKey]
            searchRes = unifiedSearch[searchKey]
            resultCount = searchRes['formattedResultCount']
            resultNo = int(resultCount)
            if resultNo == 0:
                print 'There are no matching results for the entered query'
                sys.exit('There are no matching results for the entered query')
            advSearchParams = searchRes[advSearchFormKey]
            baseData = searchRes[baseDataKey]
            resultCount = baseData[resultCountKey]
            print 'Total no of results matched your query params '+resultCount
            searchFields = advSearchParams[searchFieldsKey]
            #below line is just to print request params, we can liberally remove /comment below line
            #self.printAdvSearchFields(searchFields)
            results = searchRes[resultsKey]
            recObj = {recordKey : {gReqParamsKey:globalReqParams,advSearchFormKey:advSearchParams,baseDataKey:baseData,resultsKey:results}}
             # trying to send the value of recObj to the logging file.
            convertedRec = json.dumps(recObj)
            recObjJSON = json.loads(convertedRec) # loading the dump
            print json.dumps(recObjJSON, indent=4)
        except:
            sys.exit('There seems to be a problem with JSON, Might have occured if there is a change at LinkedIn Result structure or naming')
            
    def formTrimmedJSON(self, srchResult): ## The function being used primarily.
        """ Latest: forms the JSON with only general and mostly required information avoiding the redundant and actions information. """
        #logging.info(srchResult)
        if srchResult is None:
            raise Exception('Info: Either the query has not returned any results or there is some problem with linkedIn search', 'Info')
        rawResults = re.sub('\\\\u002d1', '\"\"', srchResult)
        try:
            rawJSON = json.loads(rawResults)
            fContent = rawJSON[contentKey]
            globalReqParams = fContent[gReqParamsKey]
            fPageRes = fContent[pageKey]
            unifiedSearch = fPageRes[unifiedSearchKey]
            searchRes = unifiedSearch[searchKey]
            resultCount = searchRes['formattedResultCount']
            resultNo = int(resultCount)
            if resultNo == 0:
                raise Exception('Info: There are no matching records for the query', 'Info')
            baseData = searchRes[baseDataKey]
            resultCount = baseData[resultCountKey]
            results = searchRes[resultsKey]
            allPersons = []
            for reslt in results:
                personObj = reslt[personKey]
                ## Pass the parameters to search from to the extractPerson function.
                frmtedPerson = self.extractPerson(personObj)
                '''
                Structure of the saved data can be changed from here.
                MongoDB structure decided from here.
                '''
                if frmtedPerson is not None:
                    allPersons.append(frmtedPerson)
                    print frmtedPerson
            recObj = {recordKey : {gReqParamsKey:globalReqParams, resultsKey:allPersons, resultCountKey:resultCount}}
            
            return recObj
        except:
            raise Exception('Error: There seems to be some problem with either the query or response JSON. Please note this might occur, if LinkedIn does not respond appropriately', 'Error')
 
    def formTrimmedJSON2(self, srchResult): ## The function being used primarily.
            """ Latest: forms the JSON with only general and mostly required information avoiding the redundant and actions information. """
            #logging.info(srchResult)
            if srchResult is None:
                raise Exception('Info: Either the query has not returned any results or there is some problem with linkedIn search', 'Info')
            rawResults = re.sub('\\\\u002d1', '\"\"', srchResult)
            try:
                rawJSON = json.loads(rawResults)
                fContent = rawJSON[contentKey]
                globalReqParams = fContent[gReqParamsKey]
                fPageRes = fContent[pageKey]
                unifiedSearch = fPageRes[unifiedSearchKey]
                searchRes = unifiedSearch[searchKey]
                resultCount = searchRes['formattedResultCount']
                resultNo = int(resultCount)
                if resultNo == 0:
                    raise Exception('Info: There are no matching records for the query', 'Info')
                baseData = searchRes[baseDataKey]
                resultCount = baseData[resultCountKey]
                results = searchRes[resultsKey]
                allPersons = []
                for reslt in results:
                    personObj = reslt[personKey]
                    ## Pass the parameters to search from to the extractPerson function.
                    frmtedPerson = self.extractPerson(personObj)
                    '''
                    Structure of the saved data can be changed from here.
                    MongoDB structure decided from here.
                    '''
                    if frmtedPerson is not None:
                        allPersons.append(frmtedPerson)
                        print frmtedPerson
                recObj = {recordKey : {gReqParamsKey:globalReqParams, resultsKey:allPersons, resultCountKey:resultCount}}
                return recObj
            except:
                raise Exception('Error: There seems to be some problem with either the query or response JSON. Please note this might occur, if LinkedIn does not respond appropriately', 'Error')


    def formTrimmedJSONadvanced(self, srchResult):
        
        try:
            rawJSON = json.loads(srchResult)
            print "RAW JSON"

            print rawJSON[:200]
            contentPart = rawJSON[contentKey]
            print "CONTENT PART"
            print contentPart[:200]
            pagePart = contentPart[pageKey]
            searchPart = pagePart[searchKey]
            baseDataPart = searchPart[baseDataKey]
            print "Base Data Part"
            print baseDataPart[:200]

            #extract data from baseData
            paginationPart = baseDataPart[resultPaginationKey]
            print "Pagination Part"
            print paginationPart[:200]
            nextPageLinks = []
            for page in paginationPart[pagesPaginationKey]:
                keys = page.keys()
                isCurrentPage = page['isCurrentPage']
                pageURL = page['pageURL']
                pageNum = page['pageNum']
                pagelink = { 'isCurrentPage':isCurrentPage, 'pageNum':pageNum, 'pageURL':pageURL }
                print pagelink
                
                nextPageLinks.append(pagelink)

            #extract person datas
            # resultsPart = searchPart[resultsKey]
            # personPart = resultsPart[personKey]

        except Exception as e:
            raise Exception('Error: There seems to be some problem with either the query or response JSON. Please note this might occur, if LinkedIn does not respond appropriately', 'Error')
    
    def formCSRecord(self, srchResult, dbHost, dbPort, dbName, mailId, locations):
        print "INSIDE FORM CS RECORD"
        # print srchResult[:300]
        if srchResult is None:
            raise Exception('Info: Either the query has not returned any results or there is some problem with linkedIn search', 'Info')
        rawResults = re.sub('\\\\u002d1', '\"\"', srchResult)
        # rawResults1 = re.sub('\\\\u003c','<',srchResult)
        # rawResults = re.sub('\\u003cB\\u003e','\"\"',rawResults1)

        # print rawResults[:2000]
        print "RAW RESULTS"
        try:
            rawJSON = json.loads(rawResults)
            print "RAW JSON"
            # print rawJSON
            fContent = rawJSON[contentKey]
            print "FCONTENT"
            # print fContent
            globalReqParams = fContent[gReqParamsKey]
            fPageRes = fContent[pageKey]
            unifiedSearch = fPageRes[unifiedSearchKey]
            searchRes = unifiedSearch[searchKey]
            print "SEARCHRES"
            # print searchRes
            resultCount = searchRes['formattedResultCount']
            resultCount = resultCount.replace(',','')
            resultNo = int(resultCount) #PROBLEM : 1,666 gives Invalid Literal error.
            if resultNo == 0:
                raise Exception('Info: There are no matching records for the query', 'Info')
            baseData = searchRes[baseDataKey]
            print "BASEDATA"
            # print baseData 
            resultCount = baseData[resultCountKey]
            print "RESULTCOUNT"
            print resultCount
            results = searchRes[resultsKey]
            print "RESULTS"
            # print results
            allPersons = []

            '''
            Related Person IDs:
            Below, the code collects the Person IDs related to 
            the current person and stores it. This helps to 
            get the data for 'Multiple' links in the displayed 
            results.
            '''
            relatedPids = []
            doUniversityCheck = True
            print "<<< FORMING PERSONS >>>"
            for reslt in results:
                personObj = reslt[personKey]
                # frmtedPerson = self.extractPerson(personObj)
                frmtedPerson = self.extractPerson(personObj,doUniversityCheck)
                ## Below we re-check without University check, to get the profiles that are possibly good.
                if frmtedPerson is None:
                    doUniversityCheck=False
                    print "FRMTEDPERSON is NONE"
                    print "University Check set to FALSE"
                    frmtedPerson = self.extractPerson(personObj,doUniversityCheck)
                if frmtedPerson is not None:
                    print "FRMTEDPERSON is not NONE"
                    relatedPids.append(frmtedPerson['person']['personId'])

            print "RELATED PIDS"
            print relatedPids
            print "UNIVERSITY CHECK == TRUE"
            doUniversityCheck = True
            for reslt in results:
                '''
                Updating the related PIDS, we also check for the University PIDs.
                '''
                # print reslt
                personObj = reslt[personKey]
                print "PERSON OBJECT"
                frmtedPerson = self.extractPerson(personObj, doUniversityCheck)
                print "FRMTEDPERSON type :"
                print type(frmtedPerson['person'])  
                pId = frmtedPerson['person']['personId'] 
                rPids=[]
                for e in relatedPids:
                    rPids.append(e)
                if pId in rPids:
                    rPids.remove(pId)
                frmtedPerson['person'].update({'relatedPids':rPids})
                print "Updating related Person Ids as list"
                print frmtedPerson['person']['relatedPids'] # added the related Person Ids.            
                if frmtedPerson is not None:
                    print "PERSON NOT NONE"
                    client = self.connect2DB(dbHost, dbPort)
                    print client
                    print "STORING .."
                    self.storeCSRecord(frmtedPerson, pId, client)
                else:
                    print "No Match"
        except Exception as e:
            print e
            raise Exception('Error: There seems to be some problem with either the query or response JSON. Please note this might occur, if LinkedIn does not respond appropriately', 'Error')

    '''
    Function to extract person details when doing
    full university search.
    '''
    def extractFullPerson(self, personObj):

        '''
        Extracts the person details from the json personObj
        '''           
        if personObj is None:
            print 'Person Object is None, returning None'
            return None;
        try:
            '''
            Extracting details
            '''
            keys = personObj.keys()

            if authTokenKey in keys:
                authToken = personObj[authTokenKey]
                
            authType = emptyString
            if authTypeKey in keys:
                authType = personObj[authTypeKey]
                
            connectCount = 0;
            if connecCountKey in keys:
                connectCount = personObj[connecCountKey]
                
            disLocale = emptyString
            if localeKey in keys:
                disLocale = personObj[localeKey]
                
            firstName = emptyString  
            if firstNameKey in keys:
                firstName = personObj[firstNameKey]
                
            lastName = emptyString
            if lastNameKey in keys:
                lastName = personObj[lastNameKey]
                
            curHeadLine = emptyString
            if headlineKey in keys:
                curHeadLine = personObj[headlineKey]

            curFullProfile1 = emptyString
            if profileLink1Key in keys:
                curFullProfile1 = personObj[profileLink1Key]

            curFullProfile2 = emptyString
            if profileLink2Key in keys:
                curFullProfile2 = personObj[profileLink2Key]

            curIndustry = emptyString
            if curIndustryKey in keys:
                curIndustry = personObj[curIndustryKey]

            curLocation = emptyString
            if curLocKey in keys:
                curLocation = personobj[curLocKey]

            encryptedId = emptyString
            # if encryptedIdKey

            logoBasedInfo = personObj[logoBaseKey]
            ghostImage = logoBasedInfo[genericGhostImageKey]
            imageKeys = logoBasedInfo.keys()
            if mediaPic100Key in imageKeys:
                isPicPresent = True
                photo100Pix = logoBasedInfo[mediaPic100Key]
                photo200Pix = logoBasedInfo[mediaPic200Key]
                photo400Pix = logoBasedInfo[mediaPic400Key]
                defPhoto = logoBasedInfo[mediaPicDefKey]
                profilePic = {profilePhoto:{genericGhostImageKey:ghostImage, mediaPicDefKey:defPhoto, mediaPic100Key:photo100Pix, mediaPic200Key:photo200Pix, mediaPic400Key:photo400Pix}}
            else:
                isPicPresent = False
                profilePic = {profilePhoto:{genericGhostImageKey:ghostImage}}

            if curEducation != emptyString:
                personFormed = { personKey:{} }

        except Exception as e:
            raise Exception('Error: There is some problem forming Person record from the information provided', 'Error')    


    def extractPerson(self, personObj, doUniversityCheck):
        """ Converts the person obj to required format """
        '''
        Arguments : personObj > person Object
                    doUniversityCheck > check whether the University Check is on (True or False)
        '''
        print "Extracting Person Details "
        if personObj is None:
            print 'Person Object is None - Returning None'
            return None;
        try:
            keys = personObj.keys()
            print keys
            authToken = emptyString
            if authTokenKey in keys:
                authToken = personObj[authTokenKey]
                
            authType = emptyString
            if authTypeKey in keys:
                authType = personObj[authTypeKey]
                
            connectCount = 0;
            if connecCountKey in keys:
                connectCount = personObj[connecCountKey]
                
            disLocale = emptyString
            if localeKey in keys:
                disLocale = personObj[localeKey]
                
            firstName = emptyString  
            if firstNameKey in keys:
                firstName = personObj[firstNameKey]
                
            lastName = emptyString
            if lastNameKey in keys:
                lastName = personObj[lastNameKey]
                
            curHeadLine = emptyString
            if headlineKey in keys:
                curHeadLine = personObj[headlineKey]
            
            curEducation = emptyString
            # Left off here.        

            curEducationHTMLparsed = ''
            '''
            Below portion by    ( )
            '''
            curFullProfile = emptyString
            for k in keys:
                goodMatch=False
                if k.startswith('link_nprofile_view_'):
                    curFullProfile = personObj[k]
                    html = self.loadPage(curFullProfile)
                    soup = BeautifulSoup(html)
                    edu_part = soup.find_all("div",re.compile("^education"))
                    edu_html_list = ''
                    # print "CONTENTS"

                    ###
                    #Below searchtext was used for searching persons from 
                    #a specific university 
                    ###
                    searchtext = "Bangladesh University" 
                    
                    # searchtext = university_choice
                    # further_part = edu_part[0].find_all("a")
                    # goodMatch=False
                    eduinfo=''
                    for e in edu_part:

                        # edu_html_list.append(str(e))
                        edu_html_list+=str(e)
                        further_part = e.find_all("a")
                        for f in further_part:
                            if(searchtext in f.contents[0]):
                                print "Search Text Found !"
                                eduinfo=f.contents[0]
                                print eduinfo
                                goodMatch=True

                            if(goodMatch==True):
                                break

                        if(goodMatch==True):
                            
                            print "Breaking for goodMatch TRUE"
                            break
                    
                    if(goodMatch==True):

                        curEducation = eduinfo
                        print "education : "+curEducation.__str__()
                        curEducationHTMLparsed = edu_html_list # Storing the html part too.
                                    
                    else:
                        '''
                        Change it Back
                        '''
                        print "RE-ATTEMPT OCCURING"
                        if(doUniversityCheck==False): 
                        ## Which means that is the re-attempt by deactivating University Search.
                            curEducation = ''
                            curEducation = eduinfo
                            curEducationHTMLparsed = edu_html_list # Storing the html part too.

                if (goodMatch==True):
                    break
                    
            print "curEducation extraction done"
            print curEducation

            curIndustry = emptyString
            if curIndustryKey in keys:
                curIndustry = personObj[curIndustryKey]
                
            curLocation = emptyString
            if curLocKey in keys:
                curLocation = personObj[curLocKey]
            
            prflName = emptyString
            if prflNameKey in keys:
                prflName = personObj[prflNameKey]
            
            profileId = 0
            if 'id' in keys:
                profileId = personObj['id']
                print "PROFILE ID : "
                print profileId
            
            isBookmark = False 
            if bookmarkKey in keys:
                isBookmark = personObj[bookmarkKey]
                
            isConnectEnabled = False
            if connectEnableKey in keys:
                isConnectEnabled = personObj[connectEnableKey]
                
            isContact = False    
            if contactKey in keys:
                isContact = personObj[contactKey]
                
            isHeadless = False
            if headlessKey in keys:
                isHeadless = personObj[headlessKey]
                
            isNameMatched = False
            if nameMatchKey in keys:
                isNameMatched = personObj[nameMatchKey]
                
            searchLink1 = emptyString
            if searchLink1Key in keys:
                searchLink1 = personObj[searchLink1Key]
                
            searchLink2 = emptyString
            if searchLink2Key in keys:
                searchLink2 = personObj[searchLink2Key]
                
            profileLink1 = emptyString
            if profileLink1Key in keys:
                profileLink1 = personObj[profileLink1Key]
                
            profileLink2 = emptyString
            if profileLink2Key in keys:
                profileLink2 = personObj[profileLink2Key]
                
            logoBasedInfo = personObj[logoBaseKey]
            ghostImage = logoBasedInfo[genericGhostImageKey]
            imageKeys = logoBasedInfo.keys()
            if mediaPic100Key in imageKeys:
                isPicPresent = True
                photo100Pix = logoBasedInfo[mediaPic100Key]
                photo200Pix = logoBasedInfo[mediaPic200Key]
                photo400Pix = logoBasedInfo[mediaPic400Key]
                defPhoto = logoBasedInfo[mediaPicDefKey]
                profilePic = {profilePhoto:{genericGhostImageKey:ghostImage, mediaPicDefKey:defPhoto, mediaPic100Key:photo100Pix, mediaPic200Key:photo200Pix, mediaPic400Key:photo400Pix}}
            else:
                isPicPresent = False
                profilePic = {profilePhoto:{genericGhostImageKey:ghostImage}}


            ## Check for the Current Education. ##
            if curEducation != '': #check that the Education is not None, only then send it ahead.
                print "CUR EDUCATION MAY NOT BE BUET"
                # personFormed = {personKey:{authTokenKey:authToken, authTypeKey:authType, connecCountKey:connectCount, localeKey:disLocale, firstNameKey:firstName, lastNameKey:lastName, headlineKey:curHeadLine, curEducationHTMLKey:curEducationHTMLparsed, curEducationKey:curEducation, curIndustryKey:curIndustry, curLocKey:curLocation, prflNameKey:prflName, personIdKey:profileId, bookmarkKey:isBookmark, connectEnableKey:isConnectEnabled, contactKey:isContact, headlessKey:isHeadless, nameMatchKey:isNameMatched, searchLink1Key:searchLink1, searchLink2Key:searchLink2, profileLink1Key:profileLink1, profileLink2Key:profileLink2, isProfilePic:isPicPresent, logoBaseKey:logoBasedInfo, profilePhoto:profilePic}}
                personFormed = {personKey:{authTokenKey:authToken, authTypeKey:authType, connecCountKey:connectCount, localeKey:disLocale, firstNameKey:firstName, lastNameKey:lastName, headlineKey:curHeadLine, curEducationHTMLKey:curEducationHTMLparsed, curEducationKey:curEducation, curIndustryKey:curIndustry, curLocKey:curLocation, prflNameKey:prflName, personIdKey:profileId, bookmarkKey:isBookmark, connectEnableKey:isConnectEnabled, contactKey:isContact, headlessKey:isHeadless, nameMatchKey:isNameMatched, searchLink1Key:searchLink1, searchLink2Key:searchLink2, profileLink1Key:profileLink1, profileLink2Key:profileLink2, isProfilePic:isPicPresent, logoBaseKey:logoBasedInfo, profilePhoto:profilePic}}
                print personFormed
                return personFormed
            
            else:
                print "None"
                return None
            
            # personFormed = {personKey:{authTokenKey:authToken, authTypeKey:authType, connecCountKey:connectCount, localeKey:disLocale, firstNameKey:firstName, lastNameKey:lastName, headlineKey:curHeadLine, curEducationHTMLKey:curEducationHTMLparsed, curEducationKey:curEducation, curIndustryKey:curIndustry, curLocKey:curLocation, prflNameKey:prflName, personIdKey:profileId, bookmarkKey:isBookmark, connectEnableKey:isConnectEnabled, contactKey:isContact, headlessKey:isHeadless, nameMatchKey:isNameMatched, searchLink1Key:searchLink1, searchLink2Key:searchLink2, profileLink1Key:profileLink1, profileLink2Key:profileLink2, isProfilePic:isPicPresent, logoBaseKey:logoBasedInfo, profilePhoto:profilePic}}
            
            return personFormed
        except Exception as e:
            print "Extract Person Exception :: "
            print e
            raise Exception('Error: There is some problem forming Person record from the information provided', 'Error')    
            
    def formDBRecord(self, recordJSON, email):
        """ Forms the DB record which is further saved into DB, this will be the final document structure which gets stored in DB"""
        try:
            record = recordJSON[recordKey]
            searchParams = record[gReqParamsKey]
            resultCount = record[resultCountKey]
            result = record[resultsKey]
            utcD = datetime.datetime.utcnow()
            utcDate = datetime.datetime.isoformat(utcD)
            dbRecord = {recordKey : {emailKey:email, searchParamsKey:searchParams, userUpdateKey:False, resultCountKey:resultCount, resultsKey:result, dateCreateKey:utcDate, dateUpdateKey:utcDate, createByKey:systemVal, updateByKey:systemVal, emailSentKey:False, emailSentCountKey:0}}
            return dbRecord
        except:
            raise Exception('Error : There is some problem with forming the record to store, might have happened because of change in LinkedIn JSOn Structure. Contact Administrator to verify formDBRecord definition', 'Error')

#linkedInTool = Authenticate(username, password)