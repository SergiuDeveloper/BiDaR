from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from SPARQLWrapper import SPARQLWrapper, JSON

def ProfiletView(request, user_id):
    # TODO make query for user_id profile

    context = {}
    # categories = []
    # context["name"] = "Ghran Andrei"
    # context["categories"] = categories
    # context["list"] = [1,2,3,4,5]

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

    # # for result in results["results"]["bindings"]:
    # #     print(f'{result["genre"]["value"]} {result["lable"]["value"]}' )

    # categories.append({'name' : 'music genres', 'values' : results["results"]["bindings"]})

    # print(context)
    return render(request, 'profile/user_profile.html', context)

def searchPreference(request):
    text = request.GET.get('text')

    # TODO make query base on the text and return results

    return JsonResponse(["a", "b", "c"], safe=False)