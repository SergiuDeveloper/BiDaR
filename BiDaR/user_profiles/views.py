from cgi import test
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse, response
from django.shortcuts import render
import requests
import json

from SPARQLWrapper import SPARQLWrapper, JSON

def ProfiletView(request, user_id):
    # TODO make query for user_id profile

    context = {}
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

        

    # query = """            
    #     SELECT DISTINCT ?genre ?lable
    #     {
    #         ?genre a <http://dbpedia.org/ontology/MusicGenre>.
    #         ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?lable.
    #     FILTER( lang(?lable) = "en" )
    #     } LIMIT 10
    # """
    # sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    # sparql.setQuery(query)

    # sparql.setReturnFormat(JSON)
    # results = sparql.query().convert()

    # for result in results["results"]["bindings"]:
    #     print(f'{result["genre"]["value"]} {result["lable"]["value"]}' )

    categories.append({'name' : 'Interests', 'values' : interests})
    categories.append({'name' : 'Skills', 'values' : skills})
    categories.append({'name' : 'Knows', 'values' : knows})
    categories.append({'name' : 'Favourite Artists', 'values' : artists})
    
    return render(request, 'profile/user_profile.html', context)


def searchPreference(request):
    print("searchPreference call")
    text = request.GET.get('search_text')
    # TODO make query base on the text and return results
    query = 'SELECT ?ref ?label WHERE { ?ref rdfs:label ?label FILTER ( regex(?label , "^' + text.replace("_"," ") + '", "i") && langMatches(lang(?label ),"en") ). } ORDER BY ?label LIMIT 5'
    # SELECT ?ref ?label WHERE { ?ref rdfs:label ?label FILTER ( regex(?label , "^Romani", "i") && langMatches(lang(?label ),"en") ). } ORDER BY strlen(str(?label)) LIMIT 5
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return JsonResponse(results["results"]["bindings"], safe=False)


def addPreference(request):
    user = request.GET.get('user')
    interest = request.GET.get('interest')

    url = 'http://localhost:8080/add_interest'
    data = {
        'name': user,
        'interest': interest
    }
    headers = {"Access-Control-Allow-Origin": "*"}
    requests.post(url, data=json.dumps(data), headers=headers)

    return JsonResponse([], safe=False)

def LogIn(request):
    context= {}
    return render(request, 'profile/log_in.html', context)

