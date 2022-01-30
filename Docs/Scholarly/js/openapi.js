window.onload = function() {
    populateSwaggerUI()
}

function populateSwaggerUI() {
    spec = {
        "openapi": "3.0.2",
        "info": {
            "title": "BiDaR API",
            "version": "1.0"
        },
        "servers": [{
            "url": "https://bidar.api/v1"
        }],
        "paths": {
            "/semantic_web_data": {
                "post": {
                    "description": "Queries DBpedia in order to retrieve facts about all the nouns identified in the request body. The NLP processor automatically determines the language of the request and only retrieves entries that are written in that language. The method used is POST in order to place data in the request body",
                    "parameters": [{
                            "schema": {
                                "type": "integer"
                            },
                            "name": "resultsLimit",
                            "in": "query",
                            "required": true,
                            "description": "The number of results to return per noun"
                        },
                        {
                            "schema": {
                                "type": "integer"
                            },
                            "name": "searchDepth",
                            "in": "query",
                            "required": true,
                            "description": "The depth for which to query data recursively"
                        }
                    ],
                    "requestBody": {
                        "description": "The text for which the NLP processing pipeline should be executed, in order to retrieve DBpedia facts",
                        "required": true,
                        "content": {
                            "schema": {
                                "schema": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "List of triples (subject predicate object), which represent facts queries recursively from DBpedia"
                        }
                    }
                }
            },
            "/query_all_data": {
                "post": {
                    "description": "Queries the internal ontology in order to retrieve all data related to a specific person. The method used is POST in order to place data in the request body",
                    "parameters": [{
                        "schema": {
                            "type": "string"
                        },
                        "name": "name",
                        "in": "header",
                        "required": true,
                        "description": "The name of the person"
                    }],
                    "responses": {
                        "200": {
                            "description": "List of triples (subject predicate object), which represent entries in the internal ontology, related to the specified person"
                        }
                    }
                }
            },
            "/query_interests": {
                "post": {
                    "description": "Queries the internal ontology in order to a specific person's country, city, job title, language, list of known people, skills, interests and favorite artists. The method used is POST in order to place data in the request body",
                    "parameters": [{
                        "schema": {
                            "type": "string"
                        },
                        "name": "name",
                        "in": "header",
                        "required": true,
                        "description": "The name of the person"
                    }],
                    "responses": {
                        "200": {
                            "description": "List of triples (subject predicate object), which represent entries in the internal ontology, related to the specified person"
                        }
                    }
                }
            },
            "/add_person": {
                "post": {
                    "description": "Add a person entry in the internal ontology",
                    "parameters": [{
                            "schema": {
                                "type": "string"
                            },
                            "name": "name",
                            "in": "header",
                            "required": true,
                            "description": "The name of the person"
                        },
                        {
                            "schema": {
                                "type": "integer"
                            },
                            "name": "age",
                            "in": "header",
                            "required": true,
                            "description": "The age of the person"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "gender",
                            "in": "header",
                            "required": true,
                            "description": "The gender of the person"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "country",
                            "in": "header",
                            "required": true,
                            "description": "The country of residence for the person"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "city",
                            "in": "header",
                            "required": true,
                            "description": "The city of residence for the person"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "jobTitle",
                            "in": "header",
                            "required": true,
                            "description": "The person's job title"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "language",
                            "in": "header",
                            "required": true,
                            "description": "The person's language"
                        },
                        {
                            "schema": {
                                "type": "array"
                            },
                            "name": "friends",
                            "in": "header",
                            "required": true,
                            "description": "The person's list of known people"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "interests",
                            "in": "header",
                            "required": true,
                            "description": "The peron's list of interests"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "skills",
                            "in": "header",
                            "required": true,
                            "description": "The peron's list of skills"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "favoriteArtists",
                            "in": "header",
                            "required": true,
                            "description": "The peron's list of favorite artists"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of triples (subject predicate object), which represent entries in the internal ontology, related to the newly added person"
                        }
                    }
                }
            },
            "/get_all_persons": {
                "get": {
                    "description": "Retrieves a list of names for all the people entries in the internal ontology",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "description": "List of names for all the people entries in the internal ontology"
                        }
                    }
                }
            }
        }
    };

    const ui = SwaggerUIBundle({
        spec: spec,
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ],
        plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout"
    })
    window.ui = ui
}