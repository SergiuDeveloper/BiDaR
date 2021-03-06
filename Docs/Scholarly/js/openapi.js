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
                            "description": "List of triples (subject predicate object), which represent facts queried recursively from DBpedia"
                        }
                    }
                }
            },
            "/related_to_interests": {
                "post": {
                    "description": "Queries DBpedia in order to retrieve data related to the nouns identified in the request body. The method used is POST in order to place data in the request body",
                    "requestBody": {
                        "description": "The name of the user making the querry and a list containing the nouns identified in the querry",
                        "required": true,
                        "content": {
                            "schema": {
                                "schema": {
                                    "type": "string"
                                }
                            },
                            "schema2":{
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "List of triples (subject predicate object), which represent the related facts queried from DBpedia"
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
                            "required": false,
                            "description": "The person's list of known people"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "interests",
                            "in": "header",
                            "required": false,
                            "description": "The person's list of interests"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "skills",
                            "in": "header",
                            "required": false,
                            "description": "The person's list of skills"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "favoriteArtists",
                            "in": "header",
                            "required": false,
                            "description": "The person's list of favorite artists"
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
            },
            "/add_data": {
                "post": {
                    "description": "Adds data related to an existing user",
                    "parameters": [{
                            "schema": {
                                "type": "string"
                            },
                            "name": "name",
                            "in": "header",
                            "required": true,
                            "description": "The name of the data entity"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "data",
                            "in": "header",
                            "required": true,
                            "description": "The value"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "section",
                            "in": "header",
                            "required": true,
                            "description": "The section"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Return a 200 status and the lable and external data source reference to the newly added data"
                        }
                    }
                }
            },
            "/remove_data": {
                "post": {
                    "description": "Removes data related to an existing user",
                    "parameters": [{
                            "schema": {
                                "type": "string"
                            },
                            "name": "name",
                            "in": "header",
                            "required": true,
                            "description": "The name of the data entity"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "data",
                            "in": "header",
                            "required": true,
                            "description": "The value"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "section",
                            "in": "header",
                            "required": true,
                            "description": "The section"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Return a 200 status and True if data was deleted successfuly "
                        }
                    }
                }
            },
            "/autocomplete_suggestions": {
                "post": {
                    "description": "Provides autocomplete suggestions for partially specified resource names",
                    "parameters": [{
                            "schema": {
                                "type": "string"
                            },
                            "name": "input_text",
                            "in": "header",
                            "required": true,
                            "description": "The input text for which the autocomplete suggestions should be provided"
                        },
                        {
                            "schema": {
                                "type": "string"
                            },
                            "name": "type",
                            "in": "header",
                            "required": true,
                            "description": "The resource type"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Return a 200 status and a list of 10 sugestions of resources from the external data source that match the provided text"
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