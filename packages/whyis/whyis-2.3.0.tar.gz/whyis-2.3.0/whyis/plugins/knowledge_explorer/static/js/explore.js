function explore() {
    app.factory('edgeNames', function() {
        // Maps each type of edge interaction with its name.
        return {
            "http://purl.obolibrary.org/obo/CHEBI_48705": "Agonist",
            "http://purl.obolibrary.org/obo/MI_0190": "Molecule Connection",
            "http://purl.obolibrary.org/obo/CHEBI_23357": "Cofactor",
            "http://purl.obolibrary.org/obo/CHEBI_25212": "Metabolite",
            "http://purl.obolibrary.org/obo/CHEBI_35224": "Effector",
            "http://purl.obolibrary.org/obo/CHEBI_48706": "Antagonist",
            "http://purl.obolibrary.org/obo/GO_0048018": "Receptor Agonist Activity",
            "http://purl.obolibrary.org/obo/GO_0030547":"Receptor Inhibitor Activity",
            "http://purl.obolibrary.org/obo/MI_0915": "Physical Association",
            "http://purl.obolibrary.org/obo/MI_0407": "Direct Interaction",
            "http://purl.obolibrary.org/obo/MI_0191": "Aggregation",
            "http://purl.obolibrary.org/obo/MI_0914": "Association",
            "http://purl.obolibrary.org/obo/MI_0217": "Phosphorylation Reaction",
            "http://purl.obolibrary.org/obo/MI_0403": "Colocalization",
            "http://purl.obolibrary.org/obo/MI_0570": "Protein Cleavage",
            "http://purl.obolibrary.org/obo/MI_0194": "Cleavage Reaction"
        }
    });

    app.factory("edgeTypes", function() {
        // Maps edge interaction types to values for Cytoscape visualization
        return {
            "tri" : {
                "shape": "triangle",
                "color": "#FED700",
                "uris": [
                    "http://purl.obolibrary.org/obo/CHEBI_48705",
                    "http://purl.obolibrary.org/obo/CHEBI_23357",
                    "http://purl.obolibrary.org/obo/CHEBI_25212",
                    "http://purl.obolibrary.org/obo/MI_2254",
                    "http://purl.obolibrary.org/obo/GO_0048018"
                ],
                "filter": false
            },
            "tee" : {
                "shape": "tee",
                "color": "#BF1578",
                "uris": [
                    "http://purl.obolibrary.org/obo/CHEBI_48706",
                    "http://purl.obolibrary.org/obo/MI_2255",
                ],
                "filter": false
            },
            "cir" : {
                "shape": "circle",
                "color": "#6FCCDD",
                "uris": [
                    "http://purl.obolibrary.org/obo/GO_0005488",
                    "http://purl.obolibrary.org/obo/GO_0048037",
                    "http://purl.obolibrary.org/obo/GO_0051087",
                    "http://purl.obolibrary.org/obo/NCIT_C40468",
                    "http://purl.obolibrary.org/obo/NCIT_C40483",
                    "http://purl.obolibrary.org/obo/NCIT_C40492"
                ],
                "filter": false
            },
            "dia" : {
                "shape": "diamond",
                "color": "#7851A1",
                "uris": [
                    "http://purl.obolibrary.org/obo/PATO_0002133",
                    "http://semanticscience.org/resource/Metabolism"
                ],
                "filter": false
            },
            "squ" : {
                "shape": "square",
                "color": "#A0A0A0",
                "uris": [
                    "http://purl.obolibrary.org/obo/MI_1157",
                    "http://purl.obolibrary.org/obo/MI_0194",
                    "http://purl.obolibrary.org/obo/MI_2048",
                ],
                "filter": false
            },
            "non" : {
                "shape": "triangle",
                "color": "#A7CE38",
                "uris": [
                    "http://purl.obolibrary.org/obo/MI_0190",
                    "http://purl.obolibrary.org/obo/CHEBI_35224",
                    "http://purl.obolibrary.org/obo/MI_0407",
                    "http://purl.obolibrary.org/obo/MI_0914"
                ],
                "filter": false
            },
            "other": {
                "shape": "triangle",
                "color": "#888",
                "uris": [],
                "filter": false,
                'label' : true
            }
        }
    });

    app.factory("nodeTypes",function() {
        // Maps node types to values for Cytoscape visualization
        return {
            // "triangle" : {
            //     "shape": "triangle",
            //     "size": "70",
            //     "color": "#FED700",
            //     "uris": ["http://semanticscience.org/resource/activator"]
            // },
            // "star" : {
            //     "shape": "star",
            //     "size": "70",
            //     "color": "#BF1578",
            //     "uris": ["http://semanticscience.org/resource/inhibitor"]
            // },
            "square" : {
                "shape": "square",
                "size": "50",
                "color": "#EA6D00",
                "uris": ["http://purl.uniprot.org/core/Protein"]
            },
            "rect" : {
                "shape": "roundrectangle",
                "size": "60",
                "color": "#112B49",
                "uris": ["http://semanticscience.org/resource/SIO_010056"]
            },
            "circle" : {
                "shape": "ellipse",
                "size": "60",
                "color": "#16A085",
                "uris": ["http://semanticscience.org/resource/Drug"]
            },
            "other" : {
                "shape": "ellipse",
                "size": "50",
                "color": "#FF7F50",
                "uris": [],
            }
        }
    });

    app.factory("getNodeFeature",['nodeTypes', function(nodeTypes) {
        // Gets the node feature of a given uri.
        return function(feature, uris) {
            var keys = Object.keys(nodeTypes);
            for (var i = 0; i < keys.length; i++) {
                for (var j = 0; j < uris.length; j++) {
                    if (nodeTypes[keys[i]]["uris"].indexOf(uris[j]) > -1) {
                        return nodeTypes[keys[i]][feature];
                    }
                }
            }
            return nodeTypes["other"][feature];
        };
    }]);


    app.factory("getEdgeFeature", ['edgeTypes', 'edgeNames', function(edgeTypes) {
        // Gets the edge feature of a given uri.
        return function(feature, uris) {
            for (var k = 0; k < uris.length; k++) {
                var uri = uris[k];
                if (feature == "name") { return edgeNames[uri]; }
                else {
                    var keys = Object.keys(edgeTypes);
                    for (var i = 0; i < keys.length; i++) {
                        console.log(uri,keys[i], edgeTypes[keys[i]]["uris"]);
                        if (edgeTypes[keys[i]]["uris"].indexOf(uri) > -1) {
                            return edgeTypes[keys[i]][feature];
                        }
                    }
                }
            }
            return edgeTypes["other"][feature];
        }
    }]);

    app.factory("links",
                ["$http", "$q", 'getLabel', 'getEdgeFeature', 'getNodeFeature',
                 function($http, $q, getLabel, getEdgeFeature, getNodeFeature) {

          function links(entity, view, elements, update, maxP, distance) {
              if (distance == null) distance = 1;
              if (maxP == null) maxP = 0.93;
              var results = [];
              if (!elements.nodes) {
                elements.nodes = [];
                elements.nodeMap = {};
                function node(uri, label, types) {
                    if (!elements.nodeMap[uri]) {
                        elements.nodeMap[uri] = { group: 'nodes', data: { uri:uri, id: uri, label: label} };
                        var nodeEntry = elements.nodeMap[uri];
                        function processTypes() {
                            if (nodeEntry.data['@type']) {
                                var types = nodeEntry.data['@type'];
                                nodeEntry.classes = types.join(' ');
                                nodeEntry.data.shape = getNodeFeature("shape", types);
                                nodeEntry.data.color = getNodeFeature("color", types);
                            }
                        }
                        //nodeEntry.data.linecolor = "#E1EA38";
                        if (types) {
                            nodeEntry.data['@type'] = types;
                            processTypes();
                        } else {
                            nodeEntry.data.described = true;
                            $http.get(ROOT_URL+'about',{ params: {uri:uri,view:'describe'}, responseType:'json'})
                                .then(function(response) {
                                    response.data.forEach(function(x) {
                                        console.log(x);
                                        if (x['@id'] == uri) {
                                            $.extend(nodeEntry.data, x);
                                            processTypes();
                                            console.log(nodeEntry);
                                        }
                                    });
                                    if (update) update()
                                });
                        }
                        if (! nodeEntry.data.label) {
                            $http.get(ROOT_URL+'about',{ params: {uri:uri,view:'label'}})
                                .then(function(response) {
                                    nodeEntry.data.label = response.data;
                                    if (update) update();
                                });
                        }
                    }
                    return elements.nodeMap[uri];
                }
                elements.node = node;
            }
            if (!elements.edges) {
                elements.edges = [];
                elements.edgeMap = {};
                function edge(edge) {
                    var edgeKey = [edge.source, edge.link, edge.target].join(' ');
                    edge.uri = edge.link;
                    if (!elements.edgeMap[edgeKey]) {
                        elements.edgeMap[edgeKey] = { group: 'edges', data: edge };
                        var edgeEntry = elements.edgeMap[edgeKey];
                        edgeEntry.id = edgeKey;
                        if (edgeEntry.data['link_types']) {
                            var types = edgeEntry.data['link_types'];
                            edgeEntry['@types'] = types;
                            edgeEntry.classes = types.join(' ');
                            edgeEntry.data.shape = getEdgeFeature("shape", types);
                            edgeEntry.data.color = getEdgeFeature("color", types);
                            if (getEdgeFeature("label",types) && types.length > 0) {
                                edgeEntry.data.label = types[0].label;
                            }
                        }
                        if (edgeEntry.data.zscore)
                            edgeEntry.data.width = Math.abs(edgeEntry.data.zscore) + 1;
                        else
                            edgeEntry.data.width = 1 + edgeEntry.data.probability;
                        if (edgeEntry.data.zscore < 0)
                            edgeEntry.data.negation = true;
                        //elements.edges.push(edgeEntry);
                    }
                    return elements.edgeMap[edgeKey];
                }
                elements.edge = edge;
            }

            var p = $http.get(ROOT_URL+'about',{ params: {uri:entity,view:view, }, responseType:'json'})
                .then(function(response) {
                    response.data.forEach(function(edge) {
                        if (edge.probability < maxP) {
                            console.log(edge.probability, maxP, "skipping", edge);
                            return;
                        }
                        elements.nodes.push(elements.node(edge.source, edge.source_label, edge.source_types));
                        elements.nodes.push(elements.node(edge.target, edge.target_label, edge.target_types));
                        elements.edges.push(elements.edge(edge));
                    });
                });
            if (!elements.all) {
                elements.all = function() {
                    return elements.nodes.concat(elements.edges);
                }
                elements.empty = function() {
                    newElements = {
                        edges : [],
                        edgeMap : elements.edgeMap,
                        edge : elements.edge,
                        nodes : [],
                        nodeMap : elements.nodeMap,
                        node : elements.node,
                        all : function() {
                            return newElements.nodes.concat(newElements.edges);
                        }
                    }
                    return newElements;
                }
            }
            return p;
        }
        return links;
    }]);

    app.factory("getSummary",['listify',function(listify) {
        var summaryProperties = [
            'http://www.w3.org/2004/02/skos/core#definition',
            'http://purl.org/dc/terms/abstract',
            'http://purl.org/dc/terms/description',
            'http://purl.org/dc/terms/summary',
            'http://www.w3.org/2000/01/rdf-schema#comment',
            "http://purl.obolibrary.org/obo/IAO_0000115",
            'http://www.w3.org/ns/prov#value',
            'http://semanticscience.org/resource/hasValue'
        ];
        function getSummary(ldEntity) {
            console.log(ldEntity);
            for (var i=0; i<summaryProperties.length; i++) {
                if (ldEntity[summaryProperties[i]] != null) {
                    var summary =  listify(ldEntity[summaryProperties[i]])[0];
                    if (summary['@value']) summary = summary['@value'];
                    return summary;
                }
            }
        };
        return getSummary;
    }]);

    app.service('generateLink', function() {
        return function(uri, view) {
            uri = window.encodeURIComponent(uri);
            var result = ROOT_URL+"about?";
            if (view) result += 'view='+view+'&';
            result += 'uri='+uri;
            return result;
        };
    });

    app.filter('kglink', function(generateLink) {
        return generateLink;
    });

    app.service("getView", [ '$http', '$q', function($http, $q) {
        var promises = {};
        function getView(uri, view, responseType) {
	    responseType = responseType == null ? 'json' : responseType;
            if (!promises[uri]) promises[uri] = {};
            if (!promises[uri][view]) {
                promises[uri][view] = $q.defer();
                $http.get(ROOT_URL+'about',{ params: {uri:uri,view:view}, responseType})
                    .then(function(response) {
                        promises[uri][view].resolve(response.data);
                    });
            }
            return promises[uri][view].promise;
        };
        return getView;
    }]);

    app.directive("kgCard", ["$http", 'links', '$timeout', '$mdSidenav', "resolveEntity", 'getSummary', 'getView',
                             function($http, links, $timeout, $mdSidenav, resolveEntity, getSummary, getView) {
	return {
            scope: {
                src : "=?",
                entity : "=?",
                compact : "=?",
            },
            transclude: true,
            templateUrl: ROOT_URL+'static/html/card.html',
	    restrict: "E",
            link: function(scope, element, attrs) {
                scope.cache = {};
                if (scope.entity == null) {
                    if (scope.src == null) {
                        scope.src = NODE_URI;
                    }
                    if (scope.src == NODE_URI) {
                        scope.entity = ATTRIBUTES;
                    } else {
                        getView(scope.src, 'attributes')
                            .then(function(attributes) {
                                scope.entity = attributes;
                            });
                    }
                }
            }
        }
    }]);

    app.directive("explore", ["$http", 'links', '$timeout', '$mdSidenav', "resolveEntity", 'getSummary', 'getView',
                              function($http, links, $timeout, $mdSidenav, resolveEntity, getSummary, getView) {
	return {
            scope: {
                elements : "=?",
                style : "=?",
                layout : "=?",
                title : "=?",
                start: "@?",
                startList: "=?"
            },
            templateUrl: ROOT_URL+'static/html/explore.html',
	    restrict: "E",
            link: function(scope, element, attrs) {
                scope.toggleSidebar = function() {
                    $mdSidenav("explore").toggle();
                }
                $mdSidenav("explore").close();
                $mdSidenav("explore_details").close();
                scope.selectedEntities = null;
                scope.searchText = null;
                scope.ROOT_URL = ROOT_URL;

                scope.searchTextChange = function(text) {
                    scope.searchText = text;
                }

                scope.selectedItemChange = function(entity) {
                    scope.selectedEntities = [entity];
                }

                scope.remove = function() {
                    var selected = scope.cy.$(':selected');
                    scope.cy.remove(selected);
                    var selectedMap = {};
                    selected.forEach(function(d) {
                        selectedMap[d.id()] = d;
                    });
                    scope.elements.nodes = scope.elements.nodes.filter(function(d) {
                        return selectedMap[d.data.id] == null;
                    });
                    scope.elements.edges = scope.elements.edges.filter(function(d) {
                        return selectedMap[d.data.id] == null
                            && selectedMap[d.data.source] == null
                            && selectedMap[d.data.target] == null ;
                    });

                }

                scope.loading = [];
                function incomingOutgoing(entities) {
                    if (entities == null) {
                        var entities = scope.cy.$('node:selected').map(function(d) {return d.id()});
                    }
                    entities.forEach(function(e) {
                        scope.loading.push(e);
                        console.log(scope.probThreshold);
                        links(e, 'incoming', scope.elements, render, scope.probThreshold, scope.numSearch).then(function() {
                            return links(e, 'outgoing', scope.elements, render, scope.probThreshold, scope.numSearch);
                        }).then(function() {
                            update();
                            scope.loading = scope.loading.filter(function(d) { return d != e});
                            console.log(scope.loading);
                        });
                    })
                }
                scope.incomingOutgoing = incomingOutgoing;
                scope.add = function() {
                    if (scope.selectedEntities) {
                        incomingOutgoing(scope.selectedEntities.map(function(d) { return d.node}))
                    } else if (scope.searchText && scope.searchText.length > 3) {
                        resolveEntity(scope.searchText).then(function (entities) {
                            incomingOutgoing(entities.map(function(d) { return d.node}))
                        });
                    }
                }

                scope.incoming = function(entities) {
                    if (entities == null) {
                        var entities = scope.cy.$('node:selected').map(function(d) {return d.id()});
                    }
                    entities.forEach(function(e) {
                        scope.loading.push(e);
                        links(e, 'incoming', scope.elements, render, scope.probThreshold, scope.numSearch).then(function() {
                            update();
                            scope.loading = scope.loading.filter(function(d) { return d != e});
                            console.log(scope.loading);
                        });
                    })
                }

                scope.outgoing = function(entities) {
                    if (entities == null) {
                        var entities = scope.cy.$('node:selected').map(function(d) {return d.id()});
                    }
                    entities.forEach(function(e) {
                        scope.loading.push(e);
                        links(e, 'outgoing', scope.elements, render, scope.probThreshold, scope.numSearch).then(function() {
                            update();
                            scope.loading = scope.loading.filter(function(d) { return d != e});
                            console.log(scope.loading);
                        });
                    })
                }

                if (!scope.style) {
                    scope.style = cytoscape.stylesheet()
                        .selector('node')
                        .css({
                            'min-zoomed-font-size': 8,
                            'text-valign': 'center',
                            'border-width': 0,
                            'cursor': 'pointer',
                            'color' : 'white',
                            'font-size': 'mapData(rank,0,1,8,16)',
//                            'font-size' : '8px',
                            'text-wrap': 'wrap',
                            'text-max-width': 'mapData(rank,0,1,100,200)',
                            //'text-outline-width' : 3,
                            //'text-outline-opacity' : 1,
                            'text-background-opacity' : 1,
                            'text-background-shape' : 'roundrectangle',
                            'text-background-padding' : '1px',
                            'width': 'mapData(rank,0,1,100,200)',
                            'height': 'mapData(rank,0,1,30,60)',
                        })
                        .selector('node[color]')
                        .css({
                            'background-color': 'data(color)',
                            'text-background-color': 'data(color)',
                            'shape': 'data(shape)',
                            //'text-outline-color' : 'data(color)',
                            //'border-color': 'data(linecolor)',
//                            'height': 'data(size)',
//                            'width': 'data(size)',
                        })
                        .selector('node[label]')
                        .css({
                            'content': 'data(label)',
                        })
                        .selector('edge')
                        .css({
                            'width':'data(width)',
                            'target-arrow-shape': 'data(shape)',
                            'curve-style' : 'bezier',
                            'target-arrow-color': 'data(color)',
                            'line-color': 'data(color)'
                        })
                        .selector('edge[label]')
                        .css({
                            'font-size' : '6px',
                            'source-text-offset': '0.5em',
                            'text-wrap':'wrap',
                            'text-max-width':'5em',
                            'source-label': 'data(label)',
                        })
                        .selector('edge[negation]')
                        .css({
                            'line-style':'dotted',
                        })
                        .selector(':selected')
                        .css({
                            //'background-color': '#D8D8D8',
                            'border-color': '#b2d7fd',
                            'border-width': 2,
                            'line-color': '#b2d7fd',
                            'target-arrow-color': '#b2d7fd',
                            'source-arrow-color': '#b2d7fd',
                            'opacity':1,
                        })
                        .selector('.highlighted')
                        .css({
                            'background-color': '#000000',
                            'line-color': '#000000',
                            'target-arrow-color': '#000000',
                            'transition-property': 'background-color, line-color, target-arrow-color, height, width',
                            'transition-duration': '0.5s'
                        })
                        .selector(':locked')
                        .css({
                            'background-color': '#7f8c8d'
                        })
                        .selector('.faded')
                        .css({
                            'opacity': 0.25,
                            'text-opacity': 0
                        })
                }

                /*
                 * CYTOSCAPE IMPLEMENTATION
                 */
                scope.neighborhood = [];
                if (!scope.layout)
                    scope.layout = {
                        name: 'cose-bilkent',
                        animate: false,
                        //randomize: true,
                        nodeDimensionsIncludeLabels: true,
                        //fit: false,
                        //padding: [20,20,20,20],
                        idealEdgeLength: 60,
                        //circle: true,
                        //concentric: function(){
                            //var rank = scope.pageRank.rank(this);
                            //console.log(this, rank, this.degree());
                            //return scope.pageRank.ordinal[rank];
                            //this.indegree() + this.outdegree();
                            //return this.degree() * 10;
                        //},
                        //maxSimulationTime: parseInt(scope.numLayout) * 1000
                    };

                scope.selected = [];
                scope.selectedNodes = [];
                scope.selectedEdges = [];

                scope.cy = cytoscape({
                    container: $(element).find('.graph'),
                    style: scope.style,
                    elements: [] ,
                    hideLabelsOnViewport: true ,
                    ready: function(){
                        scope.cy = cy = this;
                        cy.boxSelectionEnabled(true);

                        // Clicking on whitespace removes all CSS changes
                        cy.on('vclick', function(e){
                            if( e.cyTarget === cy ){
                                cy.elements().removeClass('faded');
                                cy.elements().removeClass("highlighted");
                                scope.bfsrun = false;
                                scope.neighborhood = [];
                            }
                        });

                        // When an element is selected
                        cy.on('select unselect', function(e){
                            scope.$apply(function() {
                                scope.selected =  scope.cy.$(':selected');
                                scope.selectedNodes =  scope.cy.$('node:selected');
                                scope.selectedEdges =  scope.cy.$('edge:selected');
                                scope.selectedEdges.forEach(function(d) {
                                    updateDetails(d.data());
                                });
                                if (scope.selected.length != 0) $mdSidenav("explore_details").open();
                                if (scope.selected.length == 0) $mdSidenav("explore_details").close();
                                console.log(scope.selected.map(function(d) {return d.data()}));
                            });
                        });
                    }
                });

                function updateDetails(data) {
                    data.loading = 0;
                    data.loaded = 0;
                    if (! data.label) {
                        data.loading += 1;
                        $http.get('about',{ params: {uri:data.uri,view:'label'}})
                            .then(function(response) {
                                data.label = response.data;
                                data.loaded += 1;
                                if (update) render();
                            });
                    }
                    function updateTypes(data) {
                        if (data['@type'] == null) return;
                        data.types = data['@type'].map(function(d) {
                            var result = {
                                uri: d,
                            };
                            console.log(d);
                            data.loading += 1;
                            $http.get(ROOT_URL+'about',{ params: {uri:d,view:'label'}})
                                .then(function(response) {
                                    result.label = response.data;
                                    data.loaded += 1;
                                });
                            return result;
                        });
                    }
                    if (! data.described) {
                        data.described = true;
                        data.loading += 1;
                        $http.get(ROOT_URL+'about',{ params: {uri:data.uri,view:'describe'}, responseType:'json'})
                            .then(function(response) {
                                response.data.forEach(function(x) {
                                    if (x['@id'] == data.uri) {
                                        $.extend(data, x);
                                    }
                                });
                                data.summary = getSummary(data);
                                updateTypes(data);
                                data.loaded += 1;
                                render();
                            });
                    } else {
                        if (data.types == null)
                            updateTypes(data);
                        data.summary = getSummary(data);
                        if (data.summary && data.summary['@value']) data.summary = data.summary['@value'];
                    }
                }


                /*
                 * OPTIONS
                 */
                scope.showLabel = true;
                scope.bfsrun = false;
                scope.numSearch = 1;
                scope.numLayout = 20;
                scope.probThreshold = BASE_RATE;
                scope.found = -1;
                scope.once = false;
                scope.query = "none";
                scope.filter = {
                    "customNode": {
                        "activator": true,
                        "inhibitor": true,
                        "protein": true,
                        "disease": true,
                        "drug": true,
                        "undef": true
                    },
                    "customEdge": {
                        "activation": true,
                        "inhibition": true,
                        "association": true,
                        "reaction": true,
                        "cleavage": true,
                        "interaction": true
                    }
                }


                /*
                 * HELPER FUNCTIONS
                 */

                // Error Handling
                scope.handleError = function(data,status, headers, config) {
                    scope.error = true;
                    scope.loading = false;
                };
                // Returns a list of the requested attribute of the selected nodes.
                scope.getSelected = function(attr) {
                    if (!scope.cy) return [];
                    var selected = scope.cy.$('node:selected');
                    var query = [];
                    selected.nodes().each(function(i,d) { query.push(d.data[attr]); });
                    return query;
                };

                /*
                 * NODE FUNCTIONS
                 */

                // Gets the details of a node by opening the uri in a new window.
                scope.getDetails = function(query) {
                    query.forEach(function(uri) { window.open(ROOT_URL+'about?uri='+uri); });
                };
                // Shows BFS animation starting from selected nodes
                scope.showBFS = function(query) {
                    scope.bfsrun = true;
                    query.forEach(function(id) {
                        cy.elements().removeClass("highlighted");
                        var root = "#" + id;
                        var bfs = cy.elements().bfs(root, function(){}, true);
                        var i = 0;
                        var highlightNextEle = function(){
                            bfs.path[i].addClass('highlighted');
                            bfs.path[i].removeClass('faded');
                            if( i < bfs.path.length - 1){
                                i++;
                                if (scope.bfsrun) {
                                    setTimeout(highlightNextEle, 50);
                                } else { i = bfs.path.length; }
                            }
                        };
                        highlightNextEle();
                    });
                };
                // Lock/unlock the selected elements
                scope.lock = function(query, lock) {
                    query.forEach(function(id) {
                        var node = "#" + id;
                        if (lock) { cy.$(node).lock(); }
                        else { cy.$(node).unlock(); }
                    });
                }
                if (!scope.elements) scope.elements = {};


                function updateCentrality() {
                    var nodes = scope.cy.nodes();
                    var pr = nodes.betweennessCentrality({weight:function(edge) {
                        return edge.data("probability");
                    }} );
                    nodes.forEach(function(node) {
                        var rank = pr.betweennessNormalized(node);
                        node.data("rank",rank);
                        console.log(node.data(), rank);
                    });
                }

                scope.update = update;
                function render() {
                    elements = scope.elements.all();
                    var eles = scope.cy.add(elements);
                    updateCentrality();
                    scope.cy.style().update();
                }
                function update() {
                    var elements = [];
                    if (scope.elements && scope.elements.all) {
                        scope.thisElement = scope.cy.$id(scope.start);
                        elements = scope.elements.all();
                        var eles = scope.cy.add(elements);
                        //setTimeout(function(){
                        updateCentrality();
                        scope.cy.style().update();
                        scope.cy.layout(scope.layout).run();
                        //    scope.$apply(function(){ scope.loading = false; });
                        //}, 1000);
                        scope.cy.resize();
                    }
                };


                //scope.$watchCollection('elements.edges', update);

                if (scope.start) {
                    incomingOutgoing([scope.start]);
                }
                scope.$watch("startList",function() {
                    incomingOutgoing(scope.startList);
                });

            }
        }
    }]);
}
explore();
