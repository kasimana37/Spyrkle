class Abstract_Page(object):
    """docstring for Page"""
    def __init__(self, notebook, name):
        super(Abstract_Page, self).__init__()
        self.notebook = notebook
        self.name = name
        self.static_urls = set()
        self.libs_urls = set()
        
        self.notebook.add_page(self)
        self.css_rules = {}
        # self.js_scripts = {}
        self.reset_css()

    def has_css(self) :
        return len(self.css_rules) > 0

    def register_static(self, url) :
        self.static_urls.add(url) 
    
    def register_lib(self, url) :
        self.lib_urls.add(url)

    def clear_css(self) :
        self.css_rules = {}

    def set_css_rule(self, name, lst) :
        self.css_rules[name] = lst

    def reset_css(self) :
        pass

    def get_css(self) :
        res = []
        for n, rules in self.css_rules.items() :
            str_rules = '; '.join(rules)
            res.append( "%s {%s} " % (n, str_rules) ) ;
        return '\n'.join(res)

    def get_html(self) :
        raise NotImplemented("Must be implemented in child")

class Notes(Abstract_Page):
    """docstring for Notes"""
    def __init__(self, notebook, name): # the class Note contains two arguments: 1. notebook and 2. name. notebook comes from notebook.py, name is a string E.g. notes = pages.Notes(BOOK, "Notes on life")
        super(Notes, self).__init__(notebook, name) # unsure what this one does 
        self.notes_html = [] # 'notes_html' is an attribute of class Notes, is an empty list to put in hmtl url later 

    def add_note_html(self, html, static_urls=[], lib_urls=[]) :
        self.notes_html.append(html) # add html into the list notes_html
        
        for e in static_urls :
            self.register_static(e)

        for e in static_libs :
            self.register_static(e)

    def add_note(self, title, body, img_src=None, code=None, add_line_reference=True) :

        if add_line_reference :
            import traceback
            try:
                raise TypeError("Oups!")
            except Exception as err:
                line_data = "<div class='uk-text-meta'>{filename}: {line}</div>".format(filename=traceback.extract_stack()[0].filename, line=traceback.extract_stack()[0].lineno)
        else :
            line_data = ""

        if img_src :    
            img = """
            <div class="uk-card-media-bottom">
                <img src="{img_src}" alt="">
            </div>
            """.format(img_src = img_src)
        else :
            img = ""

        if code :
            lines = code.splitlines()
            l0 = None
            for l in lines :
                if len(l) != 0 :
                    l0 = l 
                    break

            if not l0 :
                code=""
            else :
                indent = len(l0) - len(l0.strip()) 
                strip_lines = [ l[indent:] for l in lines ]
                code = "<pre class='uk-text-left'>%s</pre>" % '\n'.join(strip_lines)
        else :
            code = ""

        html = """
        <div class="uk-card uk-card-default">
            <div class="uk-card-body">
                <h3 class="uk-card-title">{title}</h3>
                {line}
                <p>{body}</p>
            </div>
            {code}
            {img}
        </div>
        """.format(line=line_data, title=title, body=body, code=code, img=img)
        self.notes_html.append(html)

    def add_bullet_points_note(self, title, points, img_src=None, add_line_reference=True) :
        
        if add_line_reference :
            import traceback
            try:
                raise TypeError("Oups!")
            except Exception as err:
                line_data = "<div class='uk-text-meta'>{filename}: {line}</div>".format(filename=traceback.extract_stack()[0].filename, line=traceback.extract_stack()[0].lineno)
        else :
            line_data = ""

        
        if img_src :    
            img = """
            <div class="uk-card-media-bottom">
                <img src="{img_src}" alt="">
            </div>
            """.format(img_src = img_src)
        else :
            img = ""
       
        lis = "<li>"+"</li><li>".join(points)+"</li>"

        html = """
        <div class="uk-card uk-card-default">
            <div class="uk-card-body">
                <h3 class="uk-card-title">{title}</h3>
                {line}
                <ul class="uk-list uk-list-bullet">{lis}</ul>
            </div>
            {img}
        </div>
        """.format(line=line_data, title=title, lis=lis, img=img)
        self.notes_html.append(html)

    def get_html(self) :
        html="""
        <div class="uk-grid-small uk-child-width-1-4@m uk-child-width-1-1@s uk-text-center" uk-grid >
        {notes}
        </div>
        """.format(notes = "\n".join(self.notes_html))

        return html

