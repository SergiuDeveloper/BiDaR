import re

from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace, FOAF, RDF, SDO

from threading import Thread, Lock
from time import time

from .SparqlProcessor import SparqlProcessor


class OntologyProcessor:

    __NAMESPACES = {
        'mo': 'http://purl.org/ontology/mo',
        'dbo': 'http://dbpedia.org/ontology',
        'dc': 'http://purl.org/dc/elements/1.1',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'tl': 'http://purl.org/NET/c4dm/timeline.owl#',
        'event': 'http://purl.org/NET/c4dm/event.owl#',
        'foaf': 'http://xmlns.com/foaf/0.1',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'sh': 'http://www.w3.org/ns/shacl#',
        'schema': 'http://schema.org'
    }

    def __init__(self, ontology_file_path, format):
        self.__ontology_file_path = ontology_file_path
        self.__format = format

        self.__graph = Graph()
        self.__graph_lock = Lock()

        for namespace, url in OntologyProcessor.__NAMESPACES.items():
            self.__graph.bind(namespace, Namespace(url))
        try:
            self.__graph.parse(ontology_file_path)
        except:
            pass

        self.__backup_daemon_running = False
    
    def activate_backup_daemon(self, timeout):
        self.__backup_daemon_running = True

        backup_daemon = Thread(target=self.__backup_daemon_logic, args=(timeout,))
        backup_daemon.start()

    def deactivate_backup_daemon(self):
        self.__backup_daemon_running = False

    def get_all_persons(self):
        triples = self.__graph.triples((None, RDF.type, FOAF.Person))
        triples_knows = self.__graph.triples((None, SDO.knows, None))
        persons = set([re.split('/|#', triple[0].n3())[-1].replace('_', ' ')[:-1] for triple in triples])
        persons_knows = set([re.split('/|#', triple[0].n3())[-1].replace('_', ' ')[:-1] for triple in triples_knows])
        return list(persons.intersection(persons_knows))

    def query_interests(self, name):
        person = URIRef('http://example.org/person/{}'.format(name.replace(' ', '_')))
        interests = []
        for predicate in [SDO.Country, SDO.City, SDO.jobTitle, SDO.language, SDO.knows, FOAF.interest, SDO.skills, SDO.artist]:
            interests.extend([triple[2] for triple in self.__graph.triples((person, predicate, None))])

        interests = [re.split('/|#', interest.n3())[-1][:-1].replace('_', ' ') for interest in interests]
        
        sparql_processor = SparqlProcessor()
        results = sparql_processor.query_information_multithreaded(interests, 'en', 3, 3)
        return list(set(results))

    def query_all_data(self, name):
        person = URIRef('http://example.org/person/{}'.format(name.replace(' ', '_')))
        results1 = list(self.__graph.triples((person, None, None)))
        results2 = list(self.__graph.triples((None, None, person)))

        results1 = [(
            re.split('/|#', result[0].n3())[-1][:-1].replace('_', ' '),
            re.split('/|#', result[1].n3())[-1][:-1].replace('_', ' '),
            re.split('/|#', result[2].n3())[-1][:-1].replace('_', ' ')
        ) for result in results1]
        results2 = [(
            re.split('/|#', result[0].n3())[-1][:-1].replace('_', ' '),
            re.split('/|#', result[1].n3())[-1][:-1].replace('_', ' '),
            re.split('/|#', result[2].n3())[-1][:-1].replace('_', ' ')
        ) for result in results2]

        results1.extend(results2)

        results1 = [(
            result[0][1:] if len(result[0][1:]) == 0 else result[0][1:] if result[0][0] == '\"' else result[0],
            result[1][1:] if len(result[1][1:]) == 0 else result[1][1:] if result[1][0] == '\"' else result[1],
            result[2][1:] if len(result[2][1:]) == 0 else result[2][1:] if result[2][0] == '\"' else result[2]
        ) for result in results1]

        return list(set(results1))

    def add_person(self, name, age, gender, country, city, job_title, language, friends, interests, skills, favorite_artists):
        self.__graph_lock.acquire()

        person = URIRef('http://example.org/person/{}'.format(name.replace(' ', '_')))

        self.__graph.add((person, RDF.type, FOAF.Person))
        self.__graph.add((person, FOAF.name, Literal(name)))
        self.__graph.add((person, FOAF.age, Literal(age)))
        self.__graph.add((person, FOAF.gender, Literal(gender)))

        country_name = country
        country = URIRef('http://example.org/country/{}'.format(country.replace(' ', '_')))
        self.__graph.add((country, RDF.type, SDO.Country))
        self.__graph.add((country, FOAF.name, Literal(country_name)))
        self.__graph.add((person, SDO.Country, country))

        city_name = city
        city = URIRef('http://example.org/city/{}'.format(city.replace(' ', '_')))
        self.__graph.add((city, RDF.type, SDO.City))
        self.__graph.add((city, FOAF.name, Literal(city_name)))
        self.__graph.add((person, SDO.City, city))

        job_title_name = job_title
        job_title = URIRef('http://example.org/jobTitle/{}'.format(job_title.replace(' ', '_')))
        self.__graph.add((job_title, RDF.type, SDO.jobTitle))
        self.__graph.add((job_title, FOAF.name, Literal(job_title_name)))
        self.__graph.add((person, SDO.jobTitle, job_title))

        language_name = language
        language = URIRef('http://example.org/language/{}'.format(language.replace(' ', '_')))
        self.__graph.add((language, RDF.type, SDO.language))
        self.__graph.add((language, FOAF.name, Literal(language_name)))
        self.__graph.add((person, SDO.language, language))

        for friend in friends:
            name = Literal(friend)
            friend = URIRef('http://example.org/person/{}'.format(friend.replace(' ', '_')))
            self.__graph.add((friend, RDF.type, FOAF.Person))
            self.__graph.add((friend, FOAF.name, name))
            self.__graph.add((person, SDO.knows, friend))

        for interest in interests:
            name = Literal(interest)
            interest = URIRef('http://example.org/interest/{}'.format(interest.replace(' ', '_')))
            self.__graph.add((interest, RDF.type, FOAF.interest))
            self.__graph.add((interest, FOAF.name, name))
            self.__graph.add((person, FOAF.interest, interest))

        for skill in skills:
            name = Literal(skill)
            skill = URIRef('http://example.org/skill/{}'.format(skill.replace(' ', '_')))
            self.__graph.add((skill, RDF.type, SDO.skills))
            self.__graph.add((skill, FOAF.name, name))
            self.__graph.add((person, SDO.skills, skill))

        for favorite_artist in favorite_artists:
            name = Literal(favorite_artist)
            favorite_artist = URIRef('http://example.org/artist/{}'.format(favorite_artist.replace(' ', '_')))
            self.__graph.add((favorite_artist, RDF.type, SDO.artist))
            self.__graph.add((favorite_artist, FOAF.name, name))
            self.__graph.add((person, SDO.artist, favorite_artist))

        self.__graph_lock.release()

    def __backup_daemon_logic(self, timeout):
        last_execution_time = time()
        while self.__backup_daemon_running:
            current_time = time()
            if current_time - last_execution_time >= timeout:
                last_execution_time = current_time
                self.__graph_lock.acquire()
                self.__graph.serialize(destination=self.__ontology_file_path, format=self.__format)
                self.__graph_lock.release()
