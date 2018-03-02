import logging
import httplib
import requests
from operator import itemgetter
from threading import Thread

from bs4 import BeautifulSoup
from bson.json_util import dumps
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader, RequestContext
from pymongo import MongoClient

from FBExecute import *
from People import People
from SignAndSearch import Authenticate
from models import Employee, CSPerson, DBRecord
from .forms import UploadFileForm

logging.basicConfig(filename='log_file.txt',level=logging.INFO)

def batchSearch(request):
    form = UploadFileForm(request.POST, request.FILES)
    print request.FILES['linkedFile']
    #fname = dirname(abspath(request.FILES['linkedFile']))
    workbook = None
    
    print "Form is Valid"
    filehandle = request.FILES['linkedFile']

    '''
    Below we have used PyExcel for excel sheet operations, follow online documents
    for more details into the SDK.
    '''
    workbook = filehandle.get_sheet()
    workbook.name_columns_by_row(1)
    records = workbook.to_records()
    message = ''
    sParams = {}
    linkObj = Authenticate('anandrox1991@gmail.com','chandraisgr8')
    failReads = 0
    successReads = 0
    sParamsList = []
    locationsList = []
    for r in records:
        if r['Full Name']=='' or r['Full Name']=='?':
            if r['Email']:
                print ""
            else:
                if r['No.'] == '':
                    l = str(r['Name']).split("/")
                    for i in l:
                        locationsList.append(i)
    # LIST SAVED TO SESSION"

    res = CSPerson.objects.order_by('person.firstName')
    allpeople = []
    for r in res:
        res1 = r['person']
        allpeople.append(People(res1['firstName'],res1['lastName'],''))

    print allpeople.__str__()

    for r in records:
        if r is None:
            failReads = failReads + 1
            continue
        sParams = {}
        goodRecord = False
        '''
        Peculiar possibilities based on the doc provided.
        '''
        if r['Name']=='Total':
            break
        if r['Name']=='Arizona':
            continue

        if r['Full Name']!='' or r['Full Name']!='?':
            thename = r['Full Name']
            thename = re.sub(r'\(.+?\)\s*', '', thename )
            print "Cleaned Full Name : "+thename
            if thename.strip()=='':
                continue
            # name = r['Full Name'].split(' ')
            name = thename.strip().split(' ')
            goodRecord = True
            if name:

                nlist = list(name)                
                '''
                Still no check for the cases for middle names.
                '''
                if len(nlist)>=2:
                    sParams['firstName'] = name[0].strip() #Removing Trailing Spaces
                    sParams['lastName'] = name[1].strip()
                else:
                    # sParams['firstName'] = ''
                    # sParams['lastName'] = ''
                    sParams['firstName']=name[0]
                    sParams['lastName']=''
        
        else:
            goodRecord = True
            sParams['firstName']=''
            sParams['lastName']=''

        print "Checking for "+sParams['firstName']+", "+sParams['lastName']
        '''
        Check for record already available.
        '''
        inrecords = False
        # for p in allpeople:
        #     # print "Inside People Records .."
        #     if ((p.firstName.lower()==sParams['firstName'].lower()) and (p.lastName.lower()==sParams['lastName'].lower())):
        #         print p.firstName+" "+p.lastName+" already in records"
        #         print "moving to next record ..."
        #         inrecords = True
        #         break

        # if inrecords==True:
        #     print "It's True"
        #     continue

        # print "CONTINUE DID NOT EXECUTE"

        if locationsList:
            sParams['locations'] = locationsList
        # request.session['locations']=locationsList
        # print "LOCATION LIST SAVED TO SESSION"

        if r['Email']:
            # print ""
            sParams['email'] = r['Email']

        else: 
            print "No Email"
            sParams['email'] = ' '
            goodRecord = True


        if goodRecord is True:     
            print "CALLING PERFORM CS SEARCH"
            resp = Authenticate.performCSSearch(linkObj, sParams, 'localhost', 27017, 'test2')
        # print "sparams : "
            # print sParams
            # resp = 'Success'
            if resp.startswith('Success'):
                print "Successfully found"
                successReads = successReads + 1
            else :
                print "Unfortunately Not Found"
                failReads = failReads + 1
    

        # if goodRecord is True:
            sParamsList.append(sParams)
    # print "INITIATING SEARCH OPERATION"
    print locationsList
    print "DONE WITH"
    for s in sParamsList:
        print s
        # resp = Authenticate.performCSSearch(linkObj, s, 'localhost', 27017, 'test2')
        # resp = Authenticate.performSearch(linkObj, s, 'localhost', 27017, 'test2')
        # resp = 'Success'
        
    message = 'The records from the uploaded file have been processed. '
    message = message + 'Success : ' + str(successReads)+' Failed : ' + str(failReads)
    msg = {'type':'I','message':message}
    context = { 'msg':msg }
    if successReads!=0:
        return render(request, 'testApp/searchGrad.html', context)
    else:
        msg = {'type':'I','message':message}
        context = { 'msg':msg }
        return render(request,'testApp/message.html', context)
        
def index1(request):
    latest_question_list = [1,2,3,4]
    template = loader.get_template('testApp/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))

def index(request):
    link = Authenticate('anandrox1991@gmail.com','chandraisgr8')
    return HttpResponse(Authenticate.djangoTest(link))

def filter(request):
    cVal = request.POST.get('profileId', '')
    try:
        vals = cVal.split('id')
        if len(vals) < 2:
            raise Exception('Error: Something went wrong, please try again later', 'Error')
        email = vals[0]
        profileId = vals[1]
        rec = DBRecord.objects(record__email=email)
        if rec is None:
            raise Exception('Error: Something went wrong, please try again later', 'Error')
        actualRd = None
        rd = rec[0]['record']
        reslts = rd['results']
        for p in reslts:
            print p['person']['personId']
            if p['person']['personId'] == int(profileId):
                actualRd = p
                break;
        if actualRd is None:
            raise Exception('Error: Something went wrong, please try again later', 'Error')
        DBRecord.objects(record__email=vals[0]).update(record__resultCount=1, set__record__results=[actualRd])
        msg = {'type':'I','message':'Record has been updated Successfully'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    except:
        msg = {'type':'E','message':'Something went wrong in updating a record, Please try again later'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    
def formSearch(request):
    print "Inside form search ... "
    firstName = request.POST.get('fname', 'Empty')
    lastName = request.POST.get('lname', 'Empty')
    email = request.POST.get('email', 'Empty')
    school = request.POST.get('university', 'Empty')
    distance = request.POST.get('distance', 'Empty')
    countryCode = request.POST.get('country',  'Empty')
    keywords = request.POST.get('keywords', 'Empty')
    params = {'email':email, 'firstName':firstName, 'lastName':lastName, 'school':school, 'countryCode':countryCode, 'keywords':keywords}
    
    print "Searching : "+params.__str__() 
    # Authenticating a linkedin profile to start with.
    linkObj = Authenticate('anandrox1991@gmail.com','chandraisgr8')
    url1='https://www.linkedin.com/'
    linkObj.checkLogin(url1) #checks that the login is successful.
     
    print "Linkedin Object :: "+linkObj.__str__()
    resp = Authenticate.performSearch(linkObj, params, 'localhost', 27017, 'test2')
    if resp.startswith('Success'):
        print request
        return results(request)
    else:
        if resp.startswith('Error'):
            type = 'E'
        else:
            type = 'I'
        message = resp
        msg = {'type':type, 'message':message}
        context = {
                   'msg':msg
                    }
        return render(request, 'testApp/message.html', context)
    

def searchUnderGrad(request): ## Added By, Bikramjit edu.bmandal@gmail.com
    print "Inside grad search ... "
    myclient = MongoClient()
    db = myclient.test2
    # firstName = request.POST.get('fname', 'Empty')
    # lastName = request.POST.get('lname', 'Empty')
    personemail = request.POST.get('email','Empty')
    university = request.POST.get('university','Empty')
    #print "Values received from request : "+firstName.__str__()+", "+lastName.__str__()+", "+email.__str__()
    #resp = Authenticate.performSearch(linkObj, params, 'localhost', 27017, 'test')
    #resp = Authenticate.filterResult(linkObj, filterParams, 'localhost', 27017, 'test')
    # results = Lesson.objects(__raw__={'subject.subject_name': 'Math'})
    #entries = db.d_b_record.find({'record.email':{'$eq':personemail}})#(__raw__={'person.fmt_location':'Taiwan'})
    '''
    Below we match the email in the records and fetch the 
    person IDs that are related to the given email.

    We need to filter the output further to 
    see if it has the college name present.

    Also other keywords to search for.

    '''
    entries = db.d_b_record.aggregate(
        [
            {
                "$match": {   "record.email": personemail }# Text Search for College Name and Country Name}
            },
            {
                "$group": {   "_id": "$record.results.person.personId"  }
            }
        ])
    
    ent_list = list(entries)
    # print "ENTRIES "
    # print ent_list

    """
    Helps to convert the Cursor function output to
    JSON readable output using BSON.JSON_UTIL library.
    """
    idlist = []
    entries_list = []
    if ent_list:
        parsed_bson = dumps(ent_list[0]) 

    #print parsed_bson

        '''
        Helps to read the json from the output of the 
        above statement.

        Will now use this method to read the details from the outputs 
        that can be presented in the output.
        '''
        parsed_json = json.loads(parsed_bson.__str__())
    #    print "\n Length of parsed_bson : "+len(parsed_json).__str__()
        #print "\n\n IDs : "+parsed_json['_id'][0].__str__()+", "+parsed_json['_id'][1].__str__()

    #    print "\n PARSED_JSON : "+parsed_json.__str__()+" \n"
        #print "IDs that match : "
        idlist = []
        for e in parsed_json['_id']:
            print e
            idlist.append(e)
    #print "ID List :"
    if idlist:
        idlist1 = [int(s) for s in idlist]
        #print idlist1
        # entries_list = [] # list, will store all details.
        for ide in idlist1: # for each of the entries in parsed_json we send add the values to list.

            #print "value : "+e.__str__()

            persons_filter = DBRecord.objects(record__results__person__personId=ide)
            #print "Persons are ... "
            # if persons_filter is None:
            # msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
            # context = {
            #     'msg':msg,}
            # return render(request,'testApp/message.html', context)

            for p in persons_filter:
                #print " "+p.record.results.__str__()
                #print " The IDs are :"

                res1 = p['record']
                count = res1['resultCount']
                print "result count : "+str(count)
                email = res1['email']
                print "email : "+str(email)
                isMultiple = False
                # if count > 1:
                #     isMultiple = True
                x = res1['results'][0]
                nperson = {'email':email, 'isMultiple':isMultiple, 'personData':x['person']}
                # for p1 in p.record.results:
                #     print p1.person.personId.__str__()+", "+p1.person.firstName.__str__()+", "+p1.person.lastName.__str__()+", "+p1.person.fmt_industry.__str__()
                #     nperson = { 'personId':p1.person.personId, 'personPhoto':p1.person.profilePhoto.profilePhoto.media_picture_link_100,'firstName':p1.person.firstName, 'lastName':p1.person.lastName, 'fmt_industry':p1.person.fmt_industry, 'fmt_location':p1.person.fmt_location, 'workinfo':p1.person.fmt_headline }
                
                entries_list.append(nperson) # appending the details of one person to the list.    
     
    # findlist = DBRecord.objects(__raw__={'record.results.person.personId':{'$in':idlist1}})
    # search_list = []
    #linkObj = Authenticate('bigdatafall2015@gmail.com','chandraisgr8')
    # print "Linkedin Object :: "+linkObj.__str__()
    
    # for p in findlist:
    #     for j in p.record.results:
    #         print j.person.firstName
    #         profile_page = j.person.link_nprofile_view_3
    #         linkObj = Authenticate('anandrox1991@gmail.com','chandraisgr8')
    #         # html = Authenticate.loadPage(linkObj, profile_page, data=None)
    #         url1='https://www.linkedin.com/'
    #         linkObj.checkLogin(url1)
    #         html = linkObj.loadPage(profile_page)
    #         goodMatch = False
    #         soup = BeautifulSoup(html)
    #         #print soup
    #         print "Profile Page"
    #         print profile_page

    #         edu_part = soup.find_all("div",re.compile("^education"))
    #         # edu_all = list(edu_part)
    #         for e in edu_part:
    #             searchtext = university
    #             print searchtext
    #             fur_part = e.find_all("a")
    #             for f in fur_part:
                    
    #         # print "CONTENTS"
    #         # searchtext = "University of Texas at Dallas"
            
    #                 eduinfo = ''
    #                 # print "CONTENTS"
    #                 # print "content : "+str(f.contents[0])
                    

    #                 # print str(flist[0]).split('\n')
    #                 if (searchtext in f.contents[0]):
    #                     print "Search Text found !!"
    #                     goodMatch=True
    #                     eduinfo = f.contents[0]
    #                     break
    #                 else:
    #                     print "No text match"
    #             # print "goodMatch value"
    #             # print goodMatch
    #             # print eduinfo
    #             if goodMatch==True:
    #                 break
    #         print "goodMatch value"
    #         print goodMatch
    #         if(goodMatch==True):
    #             nperson = {
    #                 'personId':j.person.personId,
    #                 'personPhoto':j.person.profilePhoto.profilePhoto.media_picture_link_200,
    #                 'firstName':j.person.firstName,
    #                 'lastName':j.person.lastName,
    #                 'fmt_industry':j.person.fmt_industry,
    #                 'fmt_location':j.person.fmt_location,
    #                 'workinfo':j.person.fmt_headline,
    #                 'eduinfo': eduinfo
    #             }
    #             # print nperson
    #             search_list.append(nperson)
    #             print "FouNd a good match, so appended to the list"
    #         else:
    #             print "This wasn't a good match, not appending to list"



    # each JSON can be 
    print "List of Matching results .. sending"
    # print search_list

    ctx = { 'entries':entries_list }

    '''
    If List is Empty
    '''
    if not entries_list:
        ctx = {'entries':entries_list, 'message':'NO MATCHING ENTRY IS PRESENT'}
    context=ctx
    # print "\n Entries appended to list and rendered to searchGrad.html "
    #return render(request, 'testApp/allresults.html', context)
    return render(request,'testApp/searchGrad.html',context)
    
def mergedUpdate(request):
    context = RequestContext(request)
    print "<<<<< INSIDE mergeUpdate >>>>> \n"
    myclient = MongoClient()
    db = myclient.test
    print "\n\n\n Inside mergedUpdate \n\n"
    email = ''
    isMultiple = False
    entries_list = []
    return_list = []
    res = []
    #return_list = []
    if request.method=='GET':
        
        entries_list = request.GET['selectedIDs[]']
        print "first entry"
        res = entries_list.strip('"[]').split('","')
        res = [int(i) for i in res]
        print res

        
    if entries_list:
        # fill the return list with merged results.
        # also, merge the data in the database.
        print "\n\n\n\nmergedUpdate returns \n"
        print "list we got : "

        '''
        We use json.loads(string) method to convert the GET request list 
        to a parseable JSON. Now, we can iterate over them using for loop.
        (bikramjit, edu.bmandal@gmail.com)
        '''
        print "Entries List below : "
        entry_int_list = entries_list
        #entry_int_list = [int(i) for i in entry_int_list]
        print entry_int_list
        parsed_list = json.loads(entries_list.__str__())
        #print "parsed_list : "+parsed_list.__str__()
        new_parsed_list = json.dumps(parsed_list)
        #print "new parsed_list :"+json.loads(new_parsed_list).__str__()
        final_parsed_list = json.loads(new_parsed_list)
        print "final_parsed_list : "+final_parsed_list.__str__()
        merge_list = []


        person_filter = DBRecord.objects(record__results__person__personId=final_parsed_list[0].__str__())
        email = person_filter[0].record.email

        nperson = { 'personId':final_parsed_list[0], 
                    'profilePhoto':person_filter[0].record.results[0].person.profilePhoto.profilePhoto.media_picture_link_100,
                    'firstName':person_filter[0].record.results[0].person.firstName, 
                    'lastName':person_filter[0].record.results[0].person.lastName, 
                    'link_nprofile_view_3':person_filter[0].record.results[0].person.link_nprofile_view_3,
                    'link_nprofile_view_4':person_filter[0].record.results[0].person.link_nprofile_view_4,
                    'fmt_industry':[], 
                    'fmt_location':[], 
                    'fmt_headline':[],
                    'workinfo':[],
                    'education':[]
                    }

        print "Intial nperson JSOn : "+nperson.__str__()
    
        # Using mongoengine to get the objects.
        findlist = DBRecord.objects(__raw__={'record.results.person.personId':{'$in':res}})
        print "PyMongo Print : "
        # Printing from the mongoengine objects.
        industry = ""
        headlines = ""
        locations = ""
        educations = person_filter[0].record.results[0].person.education
        for i in findlist:
            for j in i.record.results:
                ind = j.person.fmt_industry
                headl = j.person.fmt_headline
                loc = j.person.fmt_location
                educ = j.person.education
                if any(str(educ) in s for s in educations.split(',')):
                    print educ+" there"
                else:
                    educations+=str(j.person.education)+","
                if any(str(ind) in s for s in industry.split(',')):
                    print ind+" there"
                else:
                    industry+=str(j.person.fmt_industry)+","

                print(j.person.personId)

                if any(str(headl) in s for s in headlines.split('|')):
                    print headl+"(present)"
                else:
                    headlines+=str(j.person.fmt_headline)+"|"

                if any(str(loc) in s for s in locations.split(',')):
                    print loc+"(present)"
                else:
                    locations+= str(j.person.fmt_location)+","
                print(loc)
        print "FMT_INDUSTRY : "+industry
        print "FMT_HEADLINE : "+headlines
        print "FMT_LOCATION : "+locations
        print "EDUCATION : "+educations

        """
        Update in the database, combining the embedded documents.
        """

        '''
        for e in final_parsed_list: # printing to check if values received are right.
            print e.__str__()
            final_list = db.d_b_record.aggregate([{"$unwind": "$record.results"},{"$group": { '_id': "$record.results.person.personId", 'headline':{"$addToSet":"$record.results.person.fmt_headline"}, 'location':{"$addToSet":"$record.results.person.fmt_location"}, 'industry':{"$addToSet":"$record.results.person.fmt_industry"}}},{'$match': {'_id': {'$eq':int(e)}}}])
            
            #print "final_list : "+str(final_list)
            filter_list = list(final_list)
            #print "filter_list : "+str(filter_list)
            parsed_bson = dumps(filter_list[0])
            print "parsed_bson : "+str(parsed_bson)
            parsed_json = json.loads(parsed_bson, encoding='ascii')
            #print "Merge Update JSON : \n"+parsed_json.__str__()
            #print "final_list > industry :"+parsed_json['industry'][0]
            for i in parsed_json['industry']:
                print ";;"+i
            nperson['fmt_industry'].append(parsed_json['industry'])
            nperson['fmt_location'].append(parsed_json['location'])
            nperson['workinfo'].append(parsed_json['headline'])
        '''
        nperson['fmt_industry']=industry
        nperson['fmt_headline']=headlines
        nperson['fmt_location']=locations
        nperson['education']=educations
        nperson['workinfo']=headlines
        print "Final nperson JSON : "+nperson.__str__()

        x = nperson
        sperson = {'email':email, 'isMultiple':isMultiple, 'personData':x}
        return_list.append(sperson) #this list will be returned to website.    
        print "RETURN LIST : "+str(return_list)
        ctx = { 'entries':return_list }
        context=ctx
        print "\n Entries appended to list and rendered to searchGrad.html "
        
    else:
        print "\n\n\n\nmergedupdate not working \n"

        #render page with new results.
    #return HttpResponse(context)
    return render(request,'testApp/allresults.html',context)
    #return render(request,'testApp/searchGrad.html',context)

def remove(request):
    email_id = request.POST.get('email', 'EMPTY')
    if email_id == 'EMPTY':
        msg = {'type':'E','message':'Please enter valid email address'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    res = DBRecord.objects(record__email=email_id)
    res.delete()
    msg = {'type':'I','message':'If there was a record with the entered email address, It has been removed from the database'}
    context = {
        'msg':msg,}
    return render(request,'testApp/message.html', context)
        
def retrive(request):
    employList = Employee.objects(email=request.POST['email'])
    context = {
               'employList':employList
               }
    return render(request, 'testApp/employ.html', context)
	
def employ(request):
    #link = Authenticate('bigdatafall2015@gmail.com','chandraisgr8')
    return HttpResponse('FName:{0} last Name : {1}, school : {2}'.format(request.POST.get('fname', 'EMPTY'), request.POST.get('lname', 'EMPTY'), request.POST.get('school','EMPTY')))

	
def detail(request, question_id):
    return render(request, 'testApp/readForm.html')

def results(request): #Accessing mongoengine to get data.
    #res = DBRecord.objects.all()
    res = DBRecord.objects.order_by('record.results.person.firstName', '-record.results.person.connectionCount')
    if res is None:
        msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    persons = []
    for r in res:
        res1 = r['record']
        count = res1['resultCount']
        email = res1['email']
        isMultiple = False
        if count > 1:
            isMultiple = True
        x = res1['results'][0]
        person = {'email':email, 'isMultiple':isMultiple, 'personData':x['person']}
        persons.append(person)
    context = {
               'records':persons}
    return render(request, 'testApp/results.html', context)

# Created by Bikramjit Mandal (edu.bmandal@gmail.com)
def allresults(request): #Accessing mongoengine to get data.
    #res = DBRecord.objects.all()
    # res = DBRecord.objects.order_by('record.results.person.firstName', '-record.results.person.connectionCount')
    res = CSPerson.objects.order_by('person.firstName')
    
    print "INSIDE ALL RESULTS"
    print "SESSION VARIABLE locations"
    # print request.session.get('locations')
    locations = ['Arizona','Seattle','California','Canada','Georgia','Texas','Portland','Waterloo']

    if res is None:
        msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    persons = []
    personIdsRead = []
    for r in res:
        # res1 = r['record']
        # count = res1['resultCount']se
        # email = res1['email']
        res1 = r['person']
        relatedPids = res1['relatedPids']
        # personIdsRead.append(res1['personId'])
        isMultiple = False

        if len(relatedPids) != 0:
            isMultiple = True
            for rpid in relatedPids:
                personIdsRead.append(rpid) #append the Person Ids for the ones that are similar.
        # print email
        # if count > 1:
        #     isMultiple = True
        # x = res1['results'][0]
        # person = {'email':email, 'isMultiple':isMultiple, 'personData':x['person']}

        '''
        Below part extracts the education details.
        To be displayed in a better way on UI.
        Use Jquery
        '''
        soup = BeautifulSoup(res1['educationHtml'])
        edu_list = []
        edu_part = soup.find_all("div",re.compile("^education"))
        for e in edu_part:
            temp_list = '';
            temp_list2 = [];
            further_part = e.find_all("header")
            time_part = e.find_all("span","time")
            # further_part_headers = e.find_all("header");
            # for f in further_part:
            temp_list2 = [header.a.contents[0] for header in further_part]
            contents_1 = "";
            for each in temp_list2:
                contents_1 += each

                
            fl = list(further_part)
            # list1 = [header.a for a in further_part]
            for f in fl:
                if "h5" not in str(f):
                    # temp_list.append(f.contents[0])
                    temp_list = temp_list+','+f.contents[0];
                # edu_list=f.contents[1:]
            # [item.encode('utf-8') for item in temp_list]
            timelist = "";
            for t in time_part:
                timelist = timelist+t;
            print "CONTENTS_1"
            print contents_1
            edu_list.append(contents_1.encode('utf-8')+timelist)
        
        print "LIST OF EDUCATION CREATED"
        print edu_list
        # [item.encode('utf-8') for item in edu_list]
        edujson = json.dumps(edu_list)
        print "EDUCATION JSON "
        print edujson
        s = edujson[1:-1]
        s = s[1:-1]
        # print s
        # edu_list = s.split("\", \"")
        # print edu_list

        if res1['personId'] not in personIdsRead:
            person_loc = res1['fmt_location']
            person_loc_list = person_loc.split(' ')
            # for i in person_loc_list:
                # if any(i in s for s in locations):
            person = { 'isMultiple':isMultiple, 'education_all':edu_list, 'personData':r['person']}
            persons.append(person)
    context = {
               'entries':persons
               }
    return render(request, 'testApp/searchGrad.html', context)

def update(request, email_id):
    res = DBRecord.objects(record__email=email_id)
    if res is None:
        msg = {'type':'E','message':'There seems to be some problem fetching records for the entered URL, Please try again later'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    persons = []
    r = res[0]
    res1 = r['record']
    count = res1['resultCount']
    email = res1['email']
    isMultiple = False
    if count > 1:
        isMultiple = True
    reslts = res1['results']
    for x in reslts:
        person = {'email':email, 'isMultiple':isMultiple, 'personData':x['person']}
        persons.append(person)
    context = {
               'entries':persons}
    return render(request, 'testApp/searchGrad.html', context)

def updateByID(request, personId):
    '''
    Update function to update related personIds.
    '''
    res = CSPerson.objects(person__personId=personId)

    if res is None:
        msg = {'type':'E','message':'There seems to be some problem fetching records for the entered URL, Please try again later'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    persons = []
    r = res[0]
    res1 = r['person']
    isMultiple = False
    if len(res1['relatedPids']) != 0:
        isMultiple = True
    reslts = res1['relatedPids'] #List of related Pids
    reslts.append(res1['personId']) #Adding it's own personId too.
    print "Update from List"
    print reslts
    finalres = CSPerson.objects(person__personId__in=reslts)
    for x in finalres:
        person = { 'isMultiple':isMultiple, 'personData':x['person']}
        persons.append(person)
    context = {
               'entries':persons}
    return render(request, 'testApp/searchGrad.html', context)
    
def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)

def search(request):
    return render(request, 'testApp/search.html')

def utdsearch(request):

    # params = {'email':email, 'firstName':firstName, 'lastName':lastName, 'school':school, 'countryCode':countryCode, 'keywords':keywords}
    school = 'University of Texas at Dallas'
    params = { 'school':school }
    print "Searching : "+params.__str__() 
    # Authenticating a linkedin profile to start with.
    linkObj = Authenticate('bxm142230@utdallas.edu','bk11mandal#')
    url1='https://www.linkedin.com/'
    linkObj.checkLogin(url1) #checks that the login is successful.
     
    print "Linkedin Object :: "+linkObj.__str__()
    resp = Authenticate.extractLinkedInPagination(linkObj, params, 'localhost', 27017, 'test2')
    if resp.startswith('Success'):
        print "SUCCESS"
        context = { 'entries':'all searches' }
        return render(request,'testApp/utdsearch.html',context)
    else:
        if resp.startswith('Error'):
            type = 'E'
        else:
            type = 'I'
        message = resp
        msg = {'type':type, 'message':message}
        context = {
                   'msg':msg
                    }
        return render(request, 'testApp/message.html', context)

def searchgrad2(request):
    print "Inside SearchGrad 2 .."
    res = DBRecord.objects.order_by('record.results.person.firstName','-record.results.person.connectionCount')
    if res is None:
        msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
        context = {
            'msg':msg,}
        return render(request,'testApp/message.html', context)
    persons = []
    for r in res:
        res1 = r['record']
        count = res1['resultCount']
        email = res1['email']
        isMultiple = False
        if count > 1:
            isMultiple = True
        x = res1['results'][0]
        person = {'email':email, 'isMultiple':isMultiple, 'personData':x['person']}
        persons.append(person)
    context = {
               'entries':persons}
    return render(request, 'testApp/searchGrad.html', context)

def searchgrad(request):
    print "Inside Searchgrad ... "
    findlist=DBRecord.objects.all()
    search_list = []
    linkObj = Authenticate('anandrox1991@gmail.com','chandraisgr8')
    url1='https://www.linkedin.com/'
    linkObj.checkLogin(url1) #checks that the login is successful.
            
    for p in findlist:
        for j in p.record.results:
            print j.person.firstName+" "+j.person.lastName
            profile_page = j.person.link_nprofile_view_3
            # print profile_page
            # html = Authenticate.loadPage(linkObj, profile_page, data=None)
            html = linkObj.loadPage(profile_page)
            soup = BeautifulSoup(html)
            goodMatch = False
            #print soup
            edu_part = soup.find_all("div",re.compile("^education"))
            # print "CONTENTS"
            searchtext = "Bangladesh University"
            # further_part = edu_part[0].find_all("a")
            eduinfo=''
            ## Checking the education parts below
            for e in edu_part:
                # print searchtext
                further_part = e.find_all("a")
                for f in further_part:
                    '''
                    # Function is looking for any mention of the University in the 
                    # content of the tags under the Education section of the profile.
                    '''
                    #print f.contents[0]
                    if (searchtext in f.contents[0]):
                        print "Search Text found !!"
                        eduinfo=f.contents[0]
                        print eduinfo
                        goodMatch=True
                    
                    if (goodMatch==True):
                        break

                if (goodMatch==True):
                    break               

                # print "goodMatch value"
                # print goodMatch
            if(goodMatch==True):
                nperson = {
                    'personId':j.person.personId,
                    'personPhoto':j.person.profilePhoto.profilePhoto.media_picture_link_200,
                    'firstName':j.person.firstName,
                    'lastName':j.person.lastName,
                    'fmt_industry':j.person.fmt_industry,
                    'fmt_location':j.person.fmt_location,
                    'workinfo':j.person.fmt_headline,
                    'eduinfo': eduinfo
                }
                print nperson
                search_list.append(nperson)
                
                    # print "Found a match, so appending to the list"
            else:
                print "no match"
            
    


    # each JSON can be 
    print "List of Matching Search Results .. sending"
    #print search_list

    ctx = { 'entries':search_list }
    context=ctx
    return render(request, 'testApp/searchGrad.html', context)
    #return render(request, 'testApp/grad-search.html', context)

def upload(request):
    return render(request, 'testApp/upload.html')

def delete(request):
    return render(request, 'testApp/delete.html')

def get_facebook_entries(sort_param):
    results = []
    db_host = "localhost"
    db_port = 27017
    db_client = FBDb.connect(db_host, db_port)
    db = db_client.facebook_db
    cursor = db.buet3.find()
    for result in cursor:
        if sort_param == "ground":
            result["showscore"] = False
            result["showscore1"] = False
            result["showscore2"] = False
            result["showjacc"] = False
            result["watson"] = False
            result["profiles"] = sorted(result["profiles"], key=itemgetter("score1"), reverse=True)
            for profile in result["profiles"]:
                if profile["score1"] > 0:
                    result["showscore1"] = True
        elif sort_param == "combined":
            result["showscore"] = False
            result["showscore1"] = False
            result["showscore2"] = False
            result["showjacc"] = False
            result["watson"] = False
            result["profiles"] = sorted(result["profiles"], key=itemgetter("score2"), reverse=True)
            for profile in result["profiles"]:
                if profile["score2"] > 0:
                    result["showscore2"] = True
                if profile.has_key("jaccard") and profile["jaccard"] > 0.0:
                    result["showjacc"] = True
        else:
            result["showscore"] = False
            result["showscore1"] = False
            result["showscore2"] = False
            result["showjacc"] = False
            result["watson"] = False
            result["profiles"] = sorted(result["profiles"], key=itemgetter("score1", "score2", "score"), reverse=True)
            for profile in result["profiles"]:
                if profile["score"] > 0:
                    result["showscore"] = True
                if profile["score1"] > 0:
                    result["showscore1"] = True
                if profile["score2"] > 0:
                    result["showscore2"] = True
                if profile.has_key("jaccard") and profile["jaccard"] > 0.0:
                    result["showjacc"] = True
                if profile.has_key("watson") and profile["watson"]:
                    result["watson"] = True
        results.append(result)
    return results

def facebook(request):
    print "Method facebook called!"
    results = get_facebook_entries("default")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    watson = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
        if person["watson"]:
            watson = watson + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    metadata["watson"] = watson
    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebook"
    }
    return render(request, 'testApp/searchGrad.html', context)

def socialgraph(request):
    print "views.py: socialgraph Start"
    people = []
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0

    db_client = FBDb.connect()
    db = db_client.facebook_db
    cursor = db.buet3.find()
    for person in cursor:
        person["profiles"] = sorted(person["profiles"], key=itemgetter("score"), reverse=True)
        # update counters
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
        people.append(person)

    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    context = {
        "entries": people,
        "metadata": metadata,
    }

    print "views.py: socialgraph End"
    return render(request, 'testApp/social_graph.html', context)

def inputgroundtruth(request):
    print "views.py: inputgroundtruth Start"
    results = get_facebook_entries("ground")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebooktwo"
    }
    print "views.py: inputgroundtruth End"
    return render(request, 'testApp/searchGrad.html', context)

def improvedsocialgraph(request):
    print "Method facebookthree called!"
    results = get_facebook_entries("combined")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebookthree"
    }
    return render(request, 'testApp/searchGrad.html', context)

def facialrecognition(request):
    print "Method facebookthree called!"
    jaccard_cutoff_html = request.POST.get("jaccard_cutoff_html")
    if not jaccard_cutoff_html:
        jaccard_cutoff_html = 0.01
    jaccard_cutoff_html = float(jaccard_cutoff_html)
    print "jaccard_cutoff_html:", jaccard_cutoff_html
    results = get_facebook_entries("combined")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    people_having_profiles = 0
    people_having_profiles1 = 0
    outputs = []
    for result in results:
        flag = False
        for profile in result["profiles"]:
            if profile.has_key("score_jaccard_sim"):
                flag = True
        if flag:
            output = {}
            output["person"] = result["person"]
            output["profiles"] = []
            for profile in result["profiles"]:
                if profile.has_key("score_jaccard_sim") and profile["score_jaccard_sim"] >= jaccard_cutoff_html:
                    output["profiles"].append(profile)
            outputs.append(output)
            if len(output["profiles"]) > 0:
                people_having_profiles = people_having_profiles + 1
            people_having_profiles1 = people_having_profiles1 + 1
    if jaccard_cutoff_html == 0.01:
        people_having_profiles = people_having_profiles1
    context = {
        "entries1": outputs,
        "metadata": metadata,
        "type": "facebookthreeand",
        "selectedvalue": jaccard_cutoff_html,
        "people_having_profiles": people_having_profiles
    }
    return render(request, 'testApp/searchGrad.html', context)

def lists(request):
    print "views.py: fetchVisualRecogResults Start"
    results = []
    db_host = "localhost"
    db_port = 27017
    db_client = FBDb.connect(db_host, db_port)
    db = db_client.facebook_db
    cursor = db.buet3.find()
    for result in cursor:
        result["watson"] = False
        result["profiles"] = sorted(result["profiles"], key=itemgetter("score2"), reverse=True)
    for profile in result["profiles"]:
        if profile.has_key("watson") and profile["watson"]:
            result["watson"] = True
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    watson = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
        if person["watson"]:
            watson = watson + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    metadata["watson"] = watson
    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebookfour"
    }
    print "views.py: fetchVisualRecogResults End"
    return render(request, 'testApp/searchGrad.html', context)

def facebookfive(request):
    print "Method facebookfive called!"
    results = get_facebook_entries("default")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    watson = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
        if person["watson"]:
            watson = watson + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    metadata["watson"] = watson
    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebookfive"
    }
    return render(request, 'testApp/searchGrad.html', context)

def facebooksix(request):
    print "Method facebooksix called!"
    results = get_facebook_entries("default")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    watson = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
        if person["watson"]:
            watson = watson + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    metadata["watson"] = watson

    positives = 0
    non_positives = 0
    no_profile = 0
    ground_truth = {}
    for person in results:
        for profile in person["profiles"]:
            if profile.has_key("actual") and profile["actual"] == "yes":
                positives = positives + 1
                ground_truth[person["person"]] = profile["profile"]
            if profile.has_key("actual") and profile["actual"] != "yes":
                non_positives = non_positives + 1
        if len(person["profiles"]) == 0:
            no_profile = no_profile + 1

    tp1 = 0.0
    tn1 = 0.0
    fp1 = 0.0
    fn1 = 0.0
    tp2 = 0.0
    tn2 = 0.0
    fp2 = 0.0
    fn2 = 0.0
    tp3 = 0.0
    tn3 = 0.0
    fp3 = 0.0
    fn3 = 0.0
    tp4 = 0.0
    tn4 = 0.0
    fp4 = 0.0
    fn4 = 0.0
    tp5 = 0.0
    tn5 = 0.0
    fp5 = 0.0
    fn5 = 0.0

    false_positives_1 = {}
    false_negatives_1 = {}
    false_positives_2 = {}
    false_negatives_2 = {}
    false_positives_3 = {}
    false_negatives_3 = {}
    false_positives_4 = {}
    false_negatives_4 = {}
    false_positives_5 = {}
    false_negatives_5 = {}

    for k, v in ground_truth.iteritems():

        for person in results:

            if person["person"] == k:

                profile_facebook_pos = []
                profile_facebook_neg = []
                profile_facebook = person["profiles"][0]["profile"]
                profile_facebook_pos.append(profile_facebook)
                for p in person["profiles"]:
                    if p["profile"] != profile_facebook:
                        profile_facebook_neg.append(p["profile"])
                if profile_facebook and profile_facebook == v:
                    tp1 = tp1 + 1
                if profile_facebook and profile_facebook != v:
                    fp1 = fp1 + 1
                    false_positives_1[k] = profile_facebook
                if v in profile_facebook_neg:
                    fn1 = fn1 + 1
                    false_negatives_1[k] = v
                if v not in profile_facebook_neg:
                    tn1 = tn1 + len(profile_facebook_neg)

                profile_social_pos = []
                profile_social_neg = []
                person["profiles"] = sorted(person["profiles"], key=itemgetter("score"), reverse=True)
                profile_social = person["profiles"][0]["profile"]
                profile_social_pos.append(profile_social)
                for p in person["profiles"]:
                    if p["profile"] != profile_social:
                        profile_social_neg.append(p["profile"])
                if profile_social and profile_social == v:
                    tp2 = tp2 + 1
                if profile_social and profile_social != v:
                    fp2 = fp2 + 1
                    false_positives_2[k] = profile_social
                if v in profile_social_neg:
                    fn2 = fn2 + 1
                    false_negatives_2[k] = v
                if v not in profile_social_neg:
                    tn2 = tn2 + len(profile_social_neg)

                profile_gt_pos = []
                profile_gt_neg = []
                person["profiles"] = sorted(person["profiles"], key=itemgetter("score1"), reverse=True)
                profile_gt = person["profiles"][0]["profile"]
                profile_gt_pos.append(profile_gt)
                for p in person["profiles"]:
                    if p["profile"] != profile_gt:
                        profile_gt_neg.append(p["profile"])
                if profile_gt and profile_gt == v:
                    tp3 = tp3 + 1
                if profile_gt and profile_gt != v:
                    fp3 = fp3 + 1
                    false_positives_3[k] = profile_gt
                if v in profile_gt_neg:
                    fn3 = fn3 + 1
                    false_negatives_3[k] = v
                if v not in profile_gt_neg:
                    tn3 = tn3 + len(profile_gt_neg)

                profile_combined_pos = []
                profile_combined_neg = []
                person["profiles"] = sorted(person["profiles"], key=itemgetter("score2"), reverse=True)
                profile_combined = person["profiles"][0]["profile"]
                profile_combined_pos.append(profile_combined)
                for p in person["profiles"]:
                    if p["profile"] != profile_combined:
                        profile_combined_neg.append(p["profile"])
                if profile_combined and profile_combined == v:
                    tp4 = tp4 + 1
                if profile_combined and profile_combined != v:
                    fp4 = fp4 + 1
                    false_positives_4[k] = profile_combined
                if v in profile_combined_neg:
                    fn4 = fn4 + 1
                    false_negatives_4[k] = v
                if v not in profile_combined_neg:
                    tn4 = tn4 + len(profile_combined_neg)

                profile_jacc_pos = []
                profile_jacc_neg = []
                for p in person["profiles"]:
                    if not p.has_key("jaccard"):
                        p["jaccard"] = 0.0
                person["profiles"] = sorted(person["profiles"], key=itemgetter("jaccard"), reverse=True)
                profile_jacc = person["profiles"][0]["profile"]
                profile_jacc_pos.append(profile_jacc)
                for p in person["profiles"]:
                    if p["profile"] != profile_jacc:
                        profile_jacc_neg.append(p["profile"])
                if profile_jacc and profile_jacc == v:
                    tp5 = tp5 + 1
                if profile_jacc and profile_jacc != v:
                    fp5 = fp5 + 1
                    false_positives_5[k] = profile_jacc
                if v in profile_jacc_neg:
                    fn5 = fn5 + 1
                    false_negatives_5[k] = v
                if v not in profile_jacc_neg:
                    tn5 = tn5 + len(profile_jacc_neg)

    precision1 = tp1 / (tp1 + fp1)
    precision2 = tp2 / (tp2 + fp2)
    precision3 = tp3 / (tp3 + fp3)
    precision4 = tp4 / (tp4 + fp4)
    precision5 = tp5 / (tp5 + fp5)
    precision = {}
    precision["precision1"] = precision1
    precision["precision2"] = precision2
    precision["precision3"] = precision3
    precision["precision4"] = precision4
    precision["precision5"] = precision5

    recall1 = tp1 / (tp1 + fn1)
    recall2 = tp2 / (tp2 + fn2)
    recall3 = tp3 / (tp3 + fn3)
    recall4 = tp4 / (tp4 + fn4)
    recall5 = tp5 / (tp5 + fn5)
    recall = {}
    recall["recall1"] = recall1
    recall["recall2"] = recall2
    recall["recall3"] = recall3
    recall["recall4"] = recall4
    recall["recall5"] = recall5

    f1 = {}
    f1["f1_1"] = 2*precision1*recall1/(precision1+recall1)
    f1["f1_2"] = 2*precision2*recall2/(precision2+recall2)
    f1["f1_3"] = 2*precision3*recall3/(precision3+recall3)
    f1["f1_4"] = 2*precision4*recall4/(precision4+recall4)
    f1["f1_5"] = 2*precision5*recall5/(precision5+recall5)

    f2 = {}
    f2["f2_1"] = 5.0*tp1/(5.0*tp1 + 4.0*fn1 + fp1)
    f2["f2_2"] = 5.0*tp2/(5.0*tp2 + 4.0*fn2 + fp2)
    f2["f2_3"] = 5.0*tp3/(5.0*tp3 + 4.0*fn3 + fp3)
    f2["f2_4"] = 5.0*tp4/(5.0*tp4 + 4.0*fn4 + fp4)
    f2["f2_5"] = 5.0*tp5/(5.0*tp5 + 4.0*fn5 + fp5)

    accuracy = {}
    accuracy["accuracy1"] = (tp1 + tn1) / (tp1 + tn1 + fp1 + fn1)
    accuracy["accuracy2"] = (tp2 + tn2) / (tp2 + tn2 + fp2 + fn2)
    accuracy["accuracy3"] = (tp3 + tn3) / (tp3 + tn3 + fp3 + fn3)
    accuracy["accuracy4"] = (tp4 + tn4) / (tp4 + tn4 + fp4 + fn4)
    accuracy["accuracy5"] = (tp5 + tn5) / (tp5 + tn5 + fp5 + fn5)

    tnr = {}
    tnr["tnr1"] = tn1 / (tn1 + fp1)
    tnr["tnr2"] = tn2 / (tn2 + fp2)
    tnr["tnr3"] = tn3 / (tn3 + fp3)
    tnr["tnr4"] = tn4 / (tn4 + fp4)
    tnr["tnr5"] = tn5 / (tn5 + fp5)

    true_positives = {}
    true_positives["tp1"] = tp1
    true_positives["tp2"] = tp2
    true_positives["tp3"] = tp3
    true_positives["tp4"] = tp4
    true_positives["tp5"] = tp5

    false_positives = {}
    false_positives["fp1"] = fp1
    false_positives["fp2"] = fp2
    false_positives["fp3"] = fp3
    false_positives["fp4"] = fp4
    false_positives["fp5"] = fp5

    false_negatives = {}
    false_negatives["fn1"] = fn1
    false_negatives["fn2"] = fn2
    false_negatives["fn3"] = fn3
    false_negatives["fn4"] = fn4
    false_negatives["fn5"] = fn5

    true_negatives = {}
    true_negatives["tn1"] = tn1
    true_negatives["tn2"] = tn2
    true_negatives["tn3"] = tn3
    true_negatives["tn4"] = tn4
    true_negatives["tn5"] = tn5

    false_positives_dict = {}
    false_positives_dict["false_positives_1"] = false_positives_1
    false_positives_dict["false_positives_2"] = false_positives_2
    false_positives_dict["false_positives_3"] = false_positives_3
    false_positives_dict["false_positives_4"] = false_positives_4
    false_positives_dict["false_positives_5"] = false_positives_5

    false_negatives_dict = {}
    false_negatives_dict["false_negatives_1"] = false_negatives_1
    false_negatives_dict["false_negatives_2"] = false_negatives_2
    false_negatives_dict["false_negatives_3"] = false_negatives_3
    false_negatives_dict["false_negatives_4"] = false_negatives_4
    false_negatives_dict["false_negatives_5"] = false_negatives_5

    metadata["positives"] = positives
    metadata["non_positives"] = non_positives
    metadata["precision"] = precision
    metadata["recall"] = recall
    metadata["accuracy"] = accuracy
    metadata["tnr"] = tnr
    metadata["f1"] = f1
    metadata["f2"] = f2
    metadata["true_positives"] = true_positives
    metadata["false_positives"] = false_positives
    metadata["false_negatives"] = false_negatives
    metadata["true_negatives"] = true_negatives
    metadata["false_positives_dict"] = false_positives_dict
    metadata["false_negatives_dict"] = false_negatives_dict

    e1profiles = {}

    for person in results:
        for profile in person["profiles"]:
            if profile["actual"] == "yes":
                e1profiles[profile["profile"]] = profile

    e1profiles_list = []

    for k,v in e1profiles.iteritems():
        e1profiles_list.append(v)

    e1profiles_list = sorted(e1profiles_list, key=itemgetter("name"))

    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebooksix",
        "e1profiles": e1profiles_list,
        "e1profilescount": len(e1profiles_list)
    }
    return render(request, 'testApp/searchGrad.html', context)

def facebookseven(request):
    print "Method facebookfive called!"
    results = get_facebook_entries("default")
    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    watson = 0
    for person in results:
        if person["showscore"]:
            score = score + 1
        if person["showscore1"]:
            score1 = score1 + 1
        if person["showscore2"]:
            score2 = score2 + 1
        if person["showjacc"]:
            jacc = jacc + 1
        if person["watson"]:
            watson = watson + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    metadata["watson"] = watson
    verified_list = []
    for result in results:
        for profile in result["profiles"]:
            if profile["actual"] == "yes":
                verified_list.append(profile["profile"])
    for result in results:
        profiles_new = []
        for profile in result["profiles"]:
            if profile["profile"] not in verified_list:
                profiles_new.append(profile)
        result["profiles"] = profiles_new
    for result in results:
        has_newscore = False
        for profile in result["profiles"]:
            if profile.has_key("newscore"):
                has_newscore = True
                break
        if has_newscore:
            for profile in result["profiles"]:
                if not profile.has_key("newscore"):
                    profile["newscore"] = 0.0
        if has_newscore:
            result["profiles"] = sorted(result["profiles"], key=itemgetter("newscore"), reverse=True)

    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebookseven"
    }
    return render(request, 'testApp/searchGrad.html', context)

def markProfile(request):
    #for result in results:
        #print result["person"], result["profiles"]
    db_host = "localhost"
    db_port = 27017
    db_client = FBDb.connect(db_host, db_port)
    cursor = db_client.facebook_db.buet3.find()

    params_dict = {}
    facebook_profiles1 = []
    submit = request.POST.get("facebook_form_submit")
    if submit == "Reset Ground Truth!":
        for person in cursor:
            for profile in person["profiles"]:
                profile["actual"] = "na"
            db_client.facebook_db.buet3.update(
                {"_id": person["_id"]},
                {
                    "person": person["person"],
                    "profiles": person["profiles"]
                }
            )

    elif submit == "Submit changes!":
        facebook_profiles = request.POST.getlist("facebook_profile")
        #print facebook_profiles
        for facebook_profile in facebook_profiles:
            if facebook_profile.startswith("yes__"):
                facebook_profiles1.append(facebook_profile.split("yes__")[1])
                params_dict[facebook_profile.split("yes__")[1]] = "yes"
            if facebook_profile.startswith("no__"):
                facebook_profiles1.append(facebook_profile.split("no__")[1])
                params_dict[facebook_profile.split("no__")[1]] = "no"
            if facebook_profile.startswith("ver__"):
                facebook_profiles1.append(facebook_profile.split("ver__")[1])
                params_dict[facebook_profile.split("ver__")[1]] = "yes"
        for person in cursor:
            for profile in person["profiles"]:
                if profile["profile"] in facebook_profiles1:
                    profile["actual"] = params_dict[profile["profile"]]
            db_client.facebook_db.buet3.update(
                {"_id": person["_id"]},
                {
                    "person": person["person"],
                    "profiles": person["profiles"]
                }
            )

    cursor = db_client.facebook_db.buet3.find()
    # for person in cursor:
    #     for profile in person["profiles"]:
    #         if profile["profile"] in facebook_profiles1:
    #             print person["person"], " ==> ", profile["profile"]

    all_facebook_profiles = []
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        for profile in person["profiles"]:
            all_facebook_profiles.append(profile["profile"])
    all_facebook_profiles = list(set(all_facebook_profiles))
    social_graph_scores_dict = {}
    friend_of_verified_person_scores_dict = {}
    add_social_and_verified_scores_dict = {}
    print "############################## Finding relationships from Social Graph (Starts) ##############################"
    for facebook_profile in all_facebook_profiles:
        social_graph_score = 0
        counter_score1 = 0
        cursor = db_client.facebook_db.buet3.find()
        for person in cursor:
            for profile in person["profiles"]:
                if profile.has_key("friends"):
                    friends = profile["friends"]
                    if friends:
                        for friend in friends:
                            if facebook_profile == friend:
                                social_graph_score = social_graph_score + 1
                                social_graph_scores_dict[facebook_profile] = social_graph_score
                            if facebook_profile == friend and profile["actual"] == "yes":
                                counter_score1 = counter_score1 + 1
                                friend_of_verified_person_scores_dict[facebook_profile] = counter_score1
    for facebook_profile in all_facebook_profiles:
        score = 0
        if facebook_profile in social_graph_scores_dict.keys():
            score = score + social_graph_scores_dict[facebook_profile]
        if facebook_profile in friend_of_verified_person_scores_dict.keys():
            score = score + friend_of_verified_person_scores_dict[facebook_profile]
            add_social_and_verified_scores_dict[facebook_profile] = score
    print "############################## Finding relationships from Social Graph (Ends) ##############################"
    cursor = db_client.facebook_db.buet3.find()
    for person in cursor:
        for profile in person["profiles"]:
            if profile["profile"] in social_graph_scores_dict.keys():
                profile["score"] = social_graph_scores_dict[profile["profile"]]
            else:
                profile["score"] = 0;
            if profile["profile"] in friend_of_verified_person_scores_dict.keys():
                profile["score1"] = friend_of_verified_person_scores_dict[profile["profile"]]
            else:
                profile["score1"] = 0;
            if profile["profile"] in add_social_and_verified_scores_dict.keys():
                profile["score2"] = add_social_and_verified_scores_dict[profile["profile"]]
            else:
                profile["score2"] = 0;
        person["profiles"] = sorted(person["profiles"], key=itemgetter("score1", "score2", "score"), reverse=True)
        #print person
        db_client.facebook_db.buet3.update(
            {"_id": person["_id"]},
            {
                "person": person["person"],
                "profiles": person["profiles"]
            }
        )

    results = get_facebook_entries("default")

    counter_empty = 0
    counter_one = 0
    counter_some = 0
    counter_total = 0
    for person in results:
        counter_total = counter_total + 1
        if len(person["profiles"]) == 0:
            counter_empty = counter_empty + 1
        if len(person["profiles"]) == 1:
            counter_one = counter_one + 1
        if len(person["profiles"]) > 0:
            counter_some = counter_some + 1
    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    score = 0
    score1 = 0
    score2 = 0
    jacc = 0
    watson = 0
    for person in results:
        if person["showscore"] == True:
            score = score + 1
        if person["showscore1"] == True:
            score1 = score1 + 1
        if person["showscore2"] == True:
            score2 = score2 + 1
        if person["showjacc"] == True:
            jacc = jacc + 1
        if person["watson"] == True:
            watson = watson + 1
    metadata["score"] = score
    metadata["score1"] = score1
    metadata["score2"] = score2
    metadata["jacc"] = jacc
    metadata["watson"] = watson

    positives = 0
    non_positives = 0
    no_profile = 0
    ground_truth = {}
    for person in results:
        for profile in person["profiles"]:
            if profile.has_key("actual") and profile["actual"] == "yes":
                positives = positives + 1
                ground_truth[person["person"]] = profile["profile"]
            if profile.has_key("actual") and profile["actual"] != "yes":
                non_positives = non_positives + 1
        if len(person["profiles"]) == 0:
            no_profile = no_profile + 1

    tp1 = 0.0
    tn1 = 0.0
    fp1 = 0.0
    fn1 = 0.0
    tp2 = 0.0
    tn2 = 0.0
    fp2 = 0.0
    fn2 = 0.0
    tp3 = 0.0
    tn3 = 0.0
    fp3 = 0.0
    fn3 = 0.0
    tp4 = 0.0
    tn4 = 0.0
    fp4 = 0.0
    fn4 = 0.0
    tp5 = 0.0
    tn5 = 0.0
    fp5 = 0.0
    fn5 = 0.0

    false_positives_1 = {}
    false_negatives_1 = {}
    false_positives_2 = {}
    false_negatives_2 = {}
    false_positives_3 = {}
    false_negatives_3 = {}
    false_positives_4 = {}
    false_negatives_4 = {}
    false_positives_5 = {}
    false_negatives_5 = {}

    for k, v in ground_truth.iteritems():

        for person in results:

            if person["person"] == k:

                profile_facebook_pos = []
                profile_facebook_neg = []
                profile_facebook = person["profiles"][0]["profile"]
                profile_facebook_pos.append(profile_facebook)
                for p in person["profiles"]:
                    if p["profile"] != profile_facebook:
                        profile_facebook_neg.append(p["profile"])
                if profile_facebook and profile_facebook == v:
                    tp1 = tp1 + 1
                if profile_facebook and profile_facebook != v:
                    fp1 = fp1 + 1
                    false_positives_1[k] = profile_facebook
                if v in profile_facebook_neg:
                    fn1 = fn1 + 1
                    false_negatives_1[k] = v
                if v not in profile_facebook_neg:
                    tn1 = tn1 + len(profile_facebook_neg)

                profile_social_pos = []
                profile_social_neg = []
                person["profiles"] = sorted(person["profiles"], key=itemgetter("score"), reverse=True)
                profile_social = person["profiles"][0]["profile"]
                profile_social_pos.append(profile_social)
                for p in person["profiles"]:
                    if p["profile"] != profile_social:
                        profile_social_neg.append(p["profile"])
                if profile_social and profile_social == v:
                    tp2 = tp2 + 1
                if profile_social and profile_social != v:
                    fp2 = fp2 + 1
                    false_positives_2[k] = profile_social
                if v in profile_social_neg:
                    fn2 = fn2 + 1
                    false_negatives_2[k] = v
                if v not in profile_social_neg:
                    tn2 = tn2 + len(profile_social_neg)

                profile_gt_pos = []
                profile_gt_neg = []
                person["profiles"] = sorted(person["profiles"], key=itemgetter("score1"), reverse=True)
                profile_gt = person["profiles"][0]["profile"]
                profile_gt_pos.append(profile_gt)
                for p in person["profiles"]:
                    if p["profile"] != profile_gt:
                        profile_gt_neg.append(p["profile"])
                if profile_gt and profile_gt == v:
                    tp3 = tp3 + 1
                if profile_gt and profile_gt != v:
                    fp3 = fp3 + 1
                    false_positives_3[k] = profile_gt
                if v in profile_gt_neg:
                    fn3 = fn3 + 1
                    false_negatives_3[k] = v
                if v not in profile_gt_neg:
                    tn3 = tn3 + len(profile_gt_neg)

                profile_combined_pos = []
                profile_combined_neg = []
                person["profiles"] = sorted(person["profiles"], key=itemgetter("score2"), reverse=True)
                profile_combined = person["profiles"][0]["profile"]
                profile_combined_pos.append(profile_combined)
                for p in person["profiles"]:
                    if p["profile"] != profile_combined:
                        profile_combined_neg.append(p["profile"])
                if profile_combined and profile_combined == v:
                    tp4 = tp4 + 1
                if profile_combined and profile_combined != v:
                    fp4 = fp4 + 1
                    false_positives_4[k] = profile_combined
                if v in profile_combined_neg:
                    fn4 = fn4 + 1
                    false_negatives_4[k] = v
                if v not in profile_combined_neg:
                    tn4 = tn4 + len(profile_combined_neg)

                profile_jacc_pos = []
                profile_jacc_neg = []
                for p in person["profiles"]:
                    if not p.has_key("jaccard"):
                        p["jaccard"] = 0.0
                person["profiles"] = sorted(person["profiles"], key=itemgetter("jaccard"), reverse=True)
                profile_jacc = person["profiles"][0]["profile"]
                profile_jacc_pos.append(profile_jacc)
                for p in person["profiles"]:
                    if p["profile"] != profile_jacc:
                        profile_jacc_neg.append(p["profile"])
                if profile_jacc and profile_jacc == v:
                    tp5 = tp5 + 1
                if profile_jacc and profile_jacc != v:
                    fp5 = fp5 + 1
                    false_positives_5[k] = profile_jacc
                if v in profile_jacc_neg:
                    fn5 = fn5 + 1
                    false_negatives_5[k] = v
                if v not in profile_jacc_neg:
                    tn5 = tn5 + len(profile_jacc_neg)

    precision1 = tp1 / (tp1 + fp1)
    precision2 = tp2 / (tp2 + fp2)
    precision3 = tp3 / (tp3 + fp3)
    precision4 = tp4 / (tp4 + fp4)
    precision5 = tp5 / (tp5 + fp5)
    precision = {}
    precision["precision1"] = precision1
    precision["precision2"] = precision2
    precision["precision3"] = precision3
    precision["precision4"] = precision4
    precision["precision5"] = precision5

    recall1 = tp1 / (tp1 + fn1)
    recall2 = tp2 / (tp2 + fn2)
    recall3 = tp3 / (tp3 + fn3)
    recall4 = tp4 / (tp4 + fn4)
    recall5 = tp5 / (tp5 + fn5)
    recall = {}
    recall["recall1"] = recall1
    recall["recall2"] = recall2
    recall["recall3"] = recall3
    recall["recall4"] = recall4
    recall["recall5"] = recall5

    f1 = {}
    f1["f1_1"] = 2 * precision1 * recall1 / (precision1 + recall1)
    f1["f1_2"] = 2 * precision2 * recall2 / (precision2 + recall2)
    f1["f1_3"] = 2 * precision3 * recall3 / (precision3 + recall3)
    f1["f1_4"] = 2 * precision4 * recall4 / (precision4 + recall4)
    f1["f1_5"] = 2 * precision5 * recall5 / (precision5 + recall5)

    f2 = {}
    f2["f2_1"] = 5.0 * tp1 / (5.0 * tp1 + 4.0 * fn1 + fp1)
    f2["f2_2"] = 5.0 * tp2 / (5.0 * tp2 + 4.0 * fn2 + fp2)
    f2["f2_3"] = 5.0 * tp3 / (5.0 * tp3 + 4.0 * fn3 + fp3)
    f2["f2_4"] = 5.0 * tp4 / (5.0 * tp4 + 4.0 * fn4 + fp4)
    f2["f2_5"] = 5.0 * tp5 / (5.0 * tp5 + 4.0 * fn5 + fp5)

    accuracy = {}
    accuracy["accuracy1"] = (tp1 + tn1) / (tp1 + tn1 + fp1 + fn1)
    accuracy["accuracy2"] = (tp2 + tn2) / (tp2 + tn2 + fp2 + fn2)
    accuracy["accuracy3"] = (tp3 + tn3) / (tp3 + tn3 + fp3 + fn3)
    accuracy["accuracy4"] = (tp4 + tn4) / (tp4 + tn4 + fp4 + fn4)
    accuracy["accuracy5"] = (tp5 + tn5) / (tp5 + tn5 + fp5 + fn5)

    tnr = {}
    tnr["tnr1"] = tn1 / (tn1 + fp1)
    tnr["tnr2"] = tn2 / (tn2 + fp2)
    tnr["tnr3"] = tn3 / (tn3 + fp3)
    tnr["tnr4"] = tn4 / (tn4 + fp4)
    tnr["tnr5"] = tn5 / (tn5 + fp5)

    true_positives = {}
    true_positives["tp1"] = tp1
    true_positives["tp2"] = tp2
    true_positives["tp3"] = tp3
    true_positives["tp4"] = tp4
    true_positives["tp5"] = tp5

    false_positives = {}
    false_positives["fp1"] = fp1
    false_positives["fp2"] = fp2
    false_positives["fp3"] = fp3
    false_positives["fp4"] = fp4
    false_positives["fp5"] = fp5

    false_negatives = {}
    false_negatives["fn1"] = fn1
    false_negatives["fn2"] = fn2
    false_negatives["fn3"] = fn3
    false_negatives["fn4"] = fn4
    false_negatives["fn5"] = fn5

    true_negatives = {}
    true_negatives["tn1"] = tn1
    true_negatives["tn2"] = tn2
    true_negatives["tn3"] = tn3
    true_negatives["tn4"] = tn4
    true_negatives["tn5"] = tn5

    false_positives_dict = {}
    false_positives_dict["false_positives_1"] = false_positives_1
    false_positives_dict["false_positives_2"] = false_positives_2
    false_positives_dict["false_positives_3"] = false_positives_3
    false_positives_dict["false_positives_4"] = false_positives_4
    false_positives_dict["false_positives_5"] = false_positives_5

    false_negatives_dict = {}
    false_negatives_dict["false_negatives_1"] = false_negatives_1
    false_negatives_dict["false_negatives_2"] = false_negatives_2
    false_negatives_dict["false_negatives_3"] = false_negatives_3
    false_negatives_dict["false_negatives_4"] = false_negatives_4
    false_negatives_dict["false_negatives_5"] = false_negatives_5

    metadata["positives"] = positives
    metadata["non_positives"] = non_positives
    metadata["precision"] = precision
    metadata["recall"] = recall
    metadata["accuracy"] = accuracy
    metadata["tnr"] = tnr
    metadata["f1"] = f1
    metadata["f2"] = f2
    metadata["true_positives"] = true_positives
    metadata["false_positives"] = false_positives
    metadata["false_negatives"] = false_negatives
    metadata["true_negatives"] = true_negatives
    metadata["false_positives_dict"] = false_positives_dict
    metadata["false_negatives_dict"] = false_negatives_dict

    context = {
        "entries1": results,
        "metadata": metadata,
        "type": "facebooksix"
    }

    return render(request, 'testApp/searchGrad.html', context)

def sortView(request):
    print "SORT TYPE"
    print request.POST.get('sort_type','')
    sort_type = request.POST.get('sort_type','')
    res = None
    if sort_type == 'byname':
        print "Sort by Name"
        # res = DBRecord.objects.order_by('record.results.person.firstName', '-record.results.person.connectionCount')
        res = CSPerson.objects.order_by('person.firstName','-person.connectionCount')

        # Facebook code starts
        fb_entries = {}
        res = set(res)
        people = []
        for res1 in res:
            name = res1['person']['firstName'] + " " + res1['person']['lastName']
            name = name.strip()
            name = name.replace(".", "")
            name = name.replace(",", "")
            name = name.lower()
            people.append(name)
        people = list(set(people))
        for person in people:
            #print person
            fb_data = facebook(person)
            fb_entries[person] = fb_data
            #print person, " ==> ", fb_data
            #print "--------------------------------------------------------------------------------------------------------------"
        # Facebook code ends

        if res is None:
            msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
            context = {
                'msg':msg,}
            return render(request,'testApp/message.html', context)

    if sort_type == 'bynamed':
        print "Sort by Name : decreasing order"
        # res = DBRecord.objects.order_by('-record.results.person.firstName')
        res = CSPerson.objects.order_by('-person.firstName')

        # Facebook code starts
        fb_entries = {}
        res = set(res)
        people = []
        for res1 in res:
            name = res1['person']['firstName'] + " " + res1['person']['lastName']
            name = name.strip()
            name = name.replace(".", "")
            name = name.replace(",", "")
            name = name.lower()
            people.append(name)
        people = list(set(people))
        for person in people:
            # print person
            fb_data = facebook(person)
            fb_entries[person] = fb_data
            # print person, " ==> ", fb_data
            # print "--------------------------------------------------------------------------------------------------------------"
            # Facebook code ends

        if res is None:
            msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
            context = {
                'msg':msg,}
            return render(request,'testApp/message.html', context)

    if sort_type == 'byconnections':
        print "Sort by Connections : Ascending order"
        # res = DBRecord.objects.order_by('record.results.person.connectionCount')
        # res = DBRecord.objects(record__results__person__connectionCount=501)
        res = CSPerson.objects.order_by('person.connectionCount')

        # Facebook code starts
        fb_entries = {}
        res = set(res)
        people = []
        for res1 in res:
            name = res1['person']['firstName'] + " " + res1['person']['lastName']
            name = name.strip()
            name = name.replace(".", "")
            name = name.replace(",", "")
            name = name.lower()
            people.append(name)
        people = list(set(people))
        for person in people:
            # print person
            fb_data = facebook(person)
            fb_entries[person] = fb_data
            # print person, " ==> ", fb_data
            # print "--------------------------------------------------------------------------------------------------------------"
            # Facebook code ends

        if res is None:
            msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
            context = {
                'msg':msg,}
            return render(request,'testApp/message.html', context)

    if sort_type == 'byconnectionsd':
        print "Sort by Connections : decreasing order"
        # res = DBRecord.objects.order_by('-record.results.person.connectionCount')
        res = CSPerson.objects.order_by('-person.connectionCount')

        # Facebook code starts
        fb_entries = {}
        res = set(res)
        people = []
        for res1 in res:
            name = res1['person']['firstName'] + " " + res1['person']['lastName']
            name = name.strip()
            name = name.replace(".", "")
            name = name.replace(",", "")
            name = name.lower()
            people.append(name)
        people = list(set(people))
        for person in people:
            # print person
            fb_data = facebook(person)
            fb_entries[person] = fb_data
            # print person, " ==> ", fb_data
            # print "--------------------------------------------------------------------------------------------------------------"
            # Facebook code ends

        if res is None:
            msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
            context = {
                'msg':msg,}
            return render(request,'testApp/message.html', context)

    if sort_type == 'byemail':
        print "Sort by Email : alphabetical"
        # res = DBRecord.objects.order_by('record.results.email')
        res = CSPerson.objects.order_by('person.firstName')

        # Facebook code starts
        fb_entries = {}
        res = set(res)
        people = []
        for res1 in res:
            name = res1['person']['firstName'] + " " + res1['person']['lastName']
            name = name.strip()
            name = name.replace(".", "")
            name = name.replace(",", "")
            name = name.lower()
            people.append(name)
        people = list(set(people))
        for person in people:
            # print person
            fb_data = facebook(person)
            fb_entries[person] = fb_data
            # print person, " ==> ", fb_data
            # print "--------------------------------------------------------------------------------------------------------------"
            # Facebook code ends

        if res is None:
            msg = {'type':'E','message':'Currently, there are no records. Please perform Search or add few records'}
            context = {
                'msg':msg,}
            return render(request,'testApp/message.html', context)

    persons = []
    personIdsRead = []

    for r in res:
        
        isMultiple = False
        
        res1 = r['person']
        
        '''
        For extracting the education details.
        Use JQuery on the UI to better display this detail.
        '''
        soup = BeautifulSoup(res1['educationHtml'])
        edu_list = []
        edu_part = soup.find_all("div",re.compile("^education"))
        for e in edu_part:
            temp_list2 = []; # list to store the educaiton information
            further_part = e.find_all("header")
            time_part = e.find_all("span","time")
            
            #for the contents of the a tags
            temp_list2 = [header.a.contents[0] for header in further_part]
            contents_1 = "";
            for each in temp_list2:
                contents_1 += each

            # for the contents of the time tags.
            timelist = "";
            for t in time_part:
                timelist = timelist+t;

            # for f in further_part:
            fl = list(further_part)
            for f in fl:
                if "h5" not in str(f):
                    edu_list.append(f.contents[0])

            edu_list.append(contents_1.encode('utf-8')+timelist)

        # [item.encode('utf-8') for item in edu_list]
        edujson = json.dumps(edu_list)
        # print edujson
        s = edujson[1:-1]
        s = s[1:-1]
        # print s
        # edu_list = s.split("\", \"")
        # print edu_list

        relatedPids = res1['relatedPids']
        isMultiple = False

        if len(relatedPids) != 0:
            isMultiple = True
            for rpid in relatedPids:
                personIdsRead.append(rpid) #append the Person Ids for the ones that are similar.
        
        if res1['personId'] not in personIdsRead:
            # person = { 'isMultiple':isMultiple, 'personData':r['person']}
            name = res1["firstName"] + " " + res1["lastName"]
            name = name.strip()
            name = name.replace(".", "")
            name = name.replace(",", "")
            name = name.lower()
            res1["fbData"] = fb_entries[name]

            print name, " ==> "
            for itr in res1["fbData"]:
                if itr is not None:
                    print itr
            print "========================================================================================================"

            person = {'isMultiple':isMultiple, 'education_all':edu_list, 'personData':res1}
            persons.append(person)
            context = {
               'entries':persons
            }
    return render(request, 'testApp/searchGrad.html', context)
    # person = {'email':email, 'isMultiple':isMultiple, 'education_all':edujson, 'personData':x['person']}
    # return render(request, 'testApp/tempresult.html',context)

