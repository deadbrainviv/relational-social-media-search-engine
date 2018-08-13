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
import unicodedata

logging.basicConfig(filename='log_file.txt',level=logging.INFO)

def get_facebook_entries(sort_param):
    results = []
    db_host = "localhost"
    db_port = 27017
    db_client = FBDb.connect(db_host, db_port)
    db = db_client.facebook_db
    cursor = db.buet3.find()
    for result in cursor:
        if sort_param == "ground":
            print "hello"
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

    dict = {}
    if request.POST.has_key("groundtruth"):
        for item in request.POST.getlist('groundtruth'):
            if dict.has_key(item.split("__splitby___")[0]):
                dict.get(item.split("__splitby___")[0]).append(item.split("__splitby___")[1])
            else:
                list = []
                list.append(item.split("__splitby___")[1])
                dict[item.split("__splitby___")[0]] = list
    else:
        print "No groud truth marked!"

    # for k, v in dict.iteritems():
    #     print k, " : ", v

    db_client = FBDb.connect()
    db = db_client.facebook_db
    cursor = db.buet3.find()
    for person in cursor:
        person["profiles"] = sorted(person["profiles"], key=itemgetter("score"), reverse=True)
        if person["person"] in dict.keys():
            list = dict.get(person["person"])
            for profile in person["profiles"]:
                if isProfileInList(profile["profile"], list):
                    profile["actual"] = "yes"
                    print profile["profile"], "is going to be now ", profile["actual"]
        db_client.facebook_db.buet3.update(
            {"_id": person["_id"]},
            {
                "person": person["person"],
                "profiles": person["profiles"],
            }
        )

    metadata = {}
    metadata["empty"] = counter_empty
    metadata["one"] = counter_one
    metadata["some"] = counter_some
    metadata["total"] = counter_total
    context = {
        "entries": people,
        "metadata": metadata,
    }

    print "views.py: inputgroundtruth End"
    return render(request, 'testApp/social_graph.html', context)

def isProfileInList(profile, list):
    for item in list:
        unicodedata.normalize('NFKD', item).encode('ascii', 'ignore')
        if item == profile:
            return True
    return False

def inputgroundtruth1(request):
    print "views.py: inputgroundtruth Start"
    people = []
    results = get_facebook_entries("ground")
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

    # result["showscore"] = False
    # result["showscore1"] = False
    # result["showscore2"] = False
    # result["showjacc"] = False
    # result["watson"] = False
    # result["profiles"] = sorted(result["profiles"], key=itemgetter("score1"), reverse=True)
    # for profile in result["profiles"]:
    #     if profile["score1"] > 0:
    #         result["showscore1"] = True

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

