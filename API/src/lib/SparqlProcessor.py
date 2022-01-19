import re
import spacy
import concurrent.futures

from SPARQLWrapper import SPARQLWrapper, JSON

from .TextProcessor import TextProcessor


class SparqlProcessor:

    __sparql = SPARQLWrapper('http://dbpedia.org/sparql')
    __nlp = spacy.load('en_core_web_sm')

    @staticmethod
    def query_information_multithreaded(entities, language, resultsLimit, searchDepth=1):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for entity in entities:
                future = executor.submit(SparqlProcessor.__query_information, entity, language, resultsLimit)
                futures.append(future)

            results = []
            remaining = []
            for future in futures:
                entity, triples, processed_triples = future.result()
                results.extend(processed_triples)
                remaining.extend([triple[0] if triple[0] != entity else triple[2] for triple in triples])

            searchDepth = searchDepth - 1
            if searchDepth > 0:
                results.extend(SparqlProcessor.query_information_multithreaded(remaining, language, resultsLimit, searchDepth))

        results = set([result for result in results if len(result) > 0])

        return results

    @staticmethod
    def __query_information(entity, language, resultsLimit):
        if entity[:4] != 'http':
            entity = entity.capitalize()
            entity = 'http://dbpedia.org/resource/{}'.format(entity)
        
        try:
            SparqlProcessor.__sparql.setQuery("""
                SELECT DISTINCT ?s ?p ?o WHERE {
                    {
                        ?s ?p ?o
                        FILTER (?s = <%s> && !(CONTAINS(STR(?p), "hypernym")) && !(CONTAINS(STR(?p), "wikiPage")) && !(CONTAINS(STR(?p), "label")))
                    }
                    UNION 
                    {
                        ?s ?p ?o
                        FILTER (?o = <%s> && !(CONTAINS(STR(?p), "hypernym")) && !(CONTAINS(STR(?p), "wikiPage")) && !(CONTAINS(STR(?p), "label")))
                    }
                }
                LIMIT %d
            """ % (entity, entity, resultsLimit))
            SparqlProcessor.__sparql.setReturnFormat(JSON)
            results = SparqlProcessor.__sparql.query().convert()['results']['bindings']
        except:
            return entity, [], []

        processed_triples = [(re.split('/|#', result['s']['value'])[-1], re.split('/|#', result['p']['value'])[-1], re.split('/|#', result['o']['value'])[-1]) for result in results]
        languages = TextProcessor.detect_languages([' '.join(triple) for triple in processed_triples], SparqlProcessor.__nlp)

        processed_triples = [processed_triples[i] for i in range(len(processed_triples)) if languages[i] == language]
        triples = [(results[i]['s']['value'], results[i]['p']['value'], results[i]['o']['value']) for i in range(len(results)) if languages[i] == language]

        return entity, triples, processed_triples