from .core_pages import Abstract_Page

class GraphCrawler(object):
    """docstring for GraphCrawler"""
    def __init__(self, roots, parents_to_children=True):
        super(GraphCrawler, self).__init__()
        self.roots = roots
        self.parents_to_children = parents_to_children

    def get_next(self, node) :
        raise NotImplemented("Must be implemented in child")

    def get_node_uid(self, node) :
        raise NotImplemented("Must be implemented in child")
    
    def get_node_label(self, node) :
        raise NotImplemented("Must be implemented in child")

    def get_node_parameters():
        return {}

    def get_edge_parameters():
        return {}
    
    def get_node_attributes():
        return {}
    
    def get_edge_attributes():
        return {}

class Abstract_Graph(Abstract_Page):
    """docstring for DAG"""
    def __init__(self, notebook, name):
        super(Abstract_Graph, self).__init__(notebook, name)
        self._init()

    def _init(self) :
        self.caption = ""
        self.nodes, self.edges = {}, {}
        self.node_labels = set()

    def set_caption(self, caption) :
        self.caption = caption

    def force_set(self, nodes, edges) :
        self._init()
        for n in self.nodes :
            self.node_labels.add(d)

        self.nodes = nodes
        self.edges = edges

    def parse(self, fct, *args, **kwargs) :
        self.nodes, self.edges = fct(*args, **kwargs)
    
    def resolve_node_name(self, base_name, autoinc) :
        if not autoinc :
            return base_name

        name = base_name
        i = 1
        while name in self.node_labels :
            name = base_name + "_%d" % i 
            i += 1

        return name

    def crawl(
        self,
        crawler,
        autoincrement_names=True,
        reset=False
    ) :

        def _derive(root, nodes, edges, node_labels) :
            root_name = self.resolve_node_name(crawler.get_node_label(root), autoincrement_names)
            node_labels.add(root_name)
            root_uid = crawler.get_node_uid(root)
            if root_uid :
                nodes[root_uid] = {
                    "label": root_name,
                    "attributes": {
                        "label": root_name
                    }
                }

                nodes[root_uid]["attributes"].update(crawler.get_node_attributes(root))
                self.nodes[root_uid]["label"] = self.nodes[root_uid]["label"] + "(%s)" % ( len(self.nodes[root_uid]["attributes"]) -1 )

                nodes[root_uid].update(crawler.get_node_parameters(root))

                for d in crawler.get_next(root) :
                    if d is not root :
                        child_uid = crawler.get_node_uid(d)
                        if child_uid :
                            if crawler.parents_to_children :
                                con = (root_uid, child_uid)
                            else :
                                con = (child_uid, root_uid)
                            
                            self.edges[con] = {}
                            self.edges[con]["attributes"] = crawler.get_edge_attributes(con[0], con[1])
                            
                            self.edges[con].update(crawler.get_edge_parameters(con[0], con[1]))

                            _derive(d, nodes, edges, node_labels)

        if reset :
            self._init()
    
        for root in crawler.roots :
            _derive(root, self.nodes, self.edges, self.node_labels)

class DagreGraph(Abstract_Graph) :
    """"""

    def __init__(self, notebook, name):
        super(DagreGraph, self).__init__(notebook, name)
        self.graph_attributes = {}

    def set_attributes(self, dct) :
        self.graph_attributes = dct

    def reset_css(self) :
        self.css_rules = {}
        self.css_rules["text"] = (
            "font-weight: 300",
            'font-family: "Helvetica Neue", Helvetica, Arial, sans-serif',
            'font-size: 14px'
        )

        self.css_rules[".node rect"] = (
            "stroke: #999",
            'fill: #fff',
            'stroke-width: 1.5px'
        )

        self.css_rules[".edgePath path"] = (
            "stroke: #333",
            'stroke-width: 1.5px'
        )    

    def get_html(self) :
        def _pseudo_jsonify(dct) :
            attrs = [ ]
            for k, v in dct.items() :
                if type(v) is dict :
                    vv = _pseudo_jsonify(v)
                    attrs.append("'%s': {%s}" % (k, vv))
                else :
                    attrs.append("'%s': '%s'" % (k, v))

            return ','.join(attrs)

        def _set_nodes() :
            res = []
            for node_id, params in self.nodes.items() :
                attrs = _pseudo_jsonify(params)
                res.append( "g.setNode('{node_id}', {{ {attributes} }} );".format(node_id = node_id, attributes = attrs ))
            
            return '\n'.join(res)

        def _set_edges() :
            res = []
            for n1, n2 in self.edges :
                res.append( "g.setEdge('%s', '%s')" % (n1, n2) ) ;
            return '\n'.join(res)

        graph_attributes = "{%s}" % _pseudo_jsonify(self.graph_attributes)
        
        template = """
        <script src="{libs}/d3/js/d3.v4.min.js" charset="utf-8"></script>
        <script src="{libs}/dagre-d3/js/dagre-d3.js"></script>
        
        <div class="uk-card uk-card-body uk-text-center">
            {caption}
        </div>
        <div class="uk-grid">
            <svg class="uk-width-expand@s" id="svg-canvas" ></svg>
            <div class="uk-width-1-2@s uk-width-1-4@m uk-container">
                <div class="uk-card uk-card-default">
                    <h3 class="uk-card-title uk-margin uk-text-center"> Graph attributes</h3>
                    <div class="uk-card-body" id="graph-attributes"></div>
                </div>
                <div class="uk-card uk-card-default">
                    <h3 class="uk-card-title uk-margin uk-text-center"> Node attributes</h3>
                    <div class="uk-card-body" id="node-attributes"></div>
                </div>
            </div>
        </div>


        <script id="js">
            var show_attributes = function(attributes, div_id){{
                html = `<ul class="uk-list uk-list-striped">`
                for (const [key, value] of Object.entries( attributes) ) {{
                    html = html + `<li> ${{key}}: ${{value}}</li>`
                }}
                html = html + '</ul>'
                $('#'+div_id).html(html)
            }}

            show_attributes({graph_attributes}, "graph-attributes")

            // Create the input graph
            var g = new dagreD3.graphlib.Graph()
              .setGraph({{}})
              .setDefaultEdgeLabel(function() {{ return {{}}; }});

            {nodes}
            g.nodes().forEach(function(v) {{
              var node = g.node(v);
              // Round the corners of the nodes
              node.rx = node.ry = 5;
            }});

            {edges}
            // Create the renderer
            var render = new dagreD3.render();

            // Set up an SVG group so that we can translate the final graph.
            var svg = d3.select("svg"),
                svgGroup = svg.append("g");

            // Run the renderer. This is what draws the final graph.
            render(d3.select("svg g"), g);

            svgGroup.selectAll("g.node").on('click', function(name){{ show_attributes(g.node(name)['attributes'], 'node-attributes') }} )

            // Center the graph
            svg.attr("height", g.graph().height + 40);
        </script>
        """.format(nodes = _set_nodes(), edges= _set_edges(), graph_attributes=graph_attributes, caption=self.caption, libs=self.notebook.lib_folder)

        return template

