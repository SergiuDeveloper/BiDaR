from django.views.generic import TemplateView
from django.shortcuts import render

from SPARQLWrapper import SPARQLWrapper, JSON

class ProfileEdtView(TemplateView):
    template_name = r"D:\Facultate\WADE\project\BiDaR\BiDaR\user_profiles\templates\user_profile.html"

    def get_context_data(self, **kwargs):
        context = {}
        categories = [{'name': "a", "values" : [1,2,3]}, {'name': "b", "values" : [2,4,5]}, {'name': "c", "values" : [1,7,3,5]}]
        context["categories"] = categories
        context["list"] = [1,2,3,4,5]

        query = """            
            SELECT DISTINCT ?genre ?lable
            {
                ?genre a <http://dbpedia.org/ontology/MusicGenre>.
                ?genre <http://www.w3.org/2000/01/rdf-schema#label> ?lable.
            FILTER( lang(?lable) = "en" )
            } LIMIT 10
        """
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")

        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results["results"]["bindings"]:
            print(f'{result["genre"]["value"]} {result["lable"]["value"]}' )

        categories.append({'name' : 'music genres', 'values' : results["results"]["bindings"]})

        return context