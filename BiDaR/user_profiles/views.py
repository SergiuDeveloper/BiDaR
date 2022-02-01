from cgi import test
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, response
from django.shortcuts import render
import requests
import json

from SPARQLWrapper import SPARQLWrapper, JSON

def ProfiletView(request, user_id):
    # TODO make query for user_id profile

    context = {"title": f'{user_id.replace("_"," ")} Profile'}
    categories = []
    context["name"] = user_id.replace("_"," ")

    context["categories"] = categories
    # context["list"] = [1,2,3,4,5]

    # url = 'http://localhost:8080/add_interest'
    # data = {
    #     'name': "Andrei Ghiran",
        # 'interest': "http://dbpedia.org/resource/Eminem"
    # }
    # headers = {"Access-Control-Allow-Origin": "*"}
    # requests.post(url, data=json.dumps(data), headers=headers)

    url = 'http://localhost:8080/query_all_data'
    data = {
        'name': user_id.replace("_"," ")
    }
    headers = {"Access-Control-Allow-Origin": "*"}
    response = requests.post(url, data=json.dumps(data), headers=headers)

    content = response.json()
    response.close()
    interests = []
    skills = []
    knows = []
    artists = []

    for item in content:
        if item[1] == "interest":
            interests.append((item[2], item[3]))
        elif item[1] == "skills":
            skills.append((item[2], item[3]))
        elif item[1] == "knows":
            knows.append((item[2], item[3]))
        elif item[1] == "artist":
            artists.append((item[2], item[3]))
        elif item[1] == "gender":
            context["gender"] = item[2]
        elif item[1] == "age":
            context["age"] = item[2]
        elif item[1] == "Country":
            context["country"] = item[2]
        elif item[1] == "City":
            context["city"] = item[2]
        elif item[1] == "jobTitle":
            context["jobTitle"] = item[2]
        elif item[1] == "language":
            context["language"] = item[2]

        
    interests.sort()
    skills.sort()
    knows.sort()
    artists.sort()

    categories.append({'name' : 'Interests', 'values' : interests})
    categories.append({'name' : 'Skills', 'values' : skills})
    categories.append({'name' : 'Knows', 'values' : knows})
    categories.append({'name' : 'Favourite Artists', 'values' : artists})
    
    return render(request, 'profile/user_profile.html', context)

def AddUserView(request):
    context= {"title": "Add user"}
    return render(request, 'profile/add_user.html', context)


def PickUserView(request):
    context= {"title": "Pick user"}
    return render(request, 'profile/pick_user.html', context)

