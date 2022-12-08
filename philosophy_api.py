import graphene
from graphene import *
from flask import Flask
from graphql_server.flask import GraphQLView

philosophers = []

class Quote(ObjectType):
    text = Field(String)

class PhilosophyDomain(graphene.Enum):
    STOICISM = 1,
    NIHILISM = 2,
    BUDDISM = 3,
    METAPHYSICS = 4
    
class Philosopher(ObjectType):
    name = Field(String)
    quotes = Field(List(Quote))
    domain = Field(PhilosophyDomain)

class Query(ObjectType):

    getAllPhilosophers = Field(List(Philosopher), description="Find all the philosophers in the dataset.")
    def resolve_getAllPhilosophers(parent, info):
        return philosophers

    getPhilosopherByName = Field(List(Philosopher), name=Argument(String, default_value="Marcus"), description="Find a philosopher by the full or part of the name")
    def resolve_getPhilosopherByName(parent, info, name):
        found = []
        for philosopher in philosophers:
            if name in philosopher.name and philosopher not in found:
                found.append(philosopher)
        return found

    whoSaidThis = Field(List(Philosopher), quote=Argument(String, default_value="Momento"), description="Find the philosopher(s) given a part of a quote")
    def resolve_whoSaidThis(parent, info, quote):
        found = []
        for philosopher in philosophers:
            for quote_object in philosopher.quotes:
                if quote in quote_object.text and philosopher not in found:
                    found.append(philosopher)
        return found
    
    findMarcusQuote = Field(Quote, number=Argument(Int, default_value=0), description="Find a specific quote of Marcus Aurelius")
    def resolve_findMarcusQuote(parent, info, number):
        return philosophers[0].quotes[number]
    
    findByDomain = Field(List(Philosopher), domain=Argument(String, default_value="STOICISM"), description="Find every philosopher by their domain")
    def resolve_findByDomain(parent, info, domain):
        found = []
        for philosopher in philosophers:
            if domain.upper() in str(philosopher.domain) and philosopher not in found:
                found.append(philosopher)
        return found

def seed_philosophers():
    marcus_aurelius = Philosopher(name="Marcus Aurelius", quotes=[ Quote(text="Momento Mori"), Quote(text="Amor Fati"), Quote(text="The happiness of your life depends upon the quality of your thoughts."), Quote(text="You have power over your mind - not outside events. Realize this, and you will find strength."), Quote(text="Don't go on discussing what a good person should be. Just be one."), Quote(text="If you won't keep track of what your own soul’s doing how can you not be unhappy?") ], domain=PhilosophyDomain.STOICISM)
    epictetus = Philosopher(name="Epictetus", quotes=[ Quote(text="You become what you give your attention to."), Quote(text="It's not what happens to you, but how you react to it that matters."), Quote(text="First say to yourself what you would be; and then do what you have to do")], domain=PhilosophyDomain.STOICISM)
    seneca = Philosopher(name="Lucius Annaeus Seneca", quotes=[ Quote(text="We suffer more often in imagination than in reality"), Quote(text="Luck is what happens when preparation meets opportunity."), Quote(text="He who is brave is free.")], domain=PhilosophyDomain.STOICISM)
    aristotle = Philosopher(name="Aristotle", quotes=[ Quote(text="Quality is not an act, it is a habit."), Quote(text="A friend to all is a friend to none.")], domain=PhilosophyDomain.METAPHYSICS)
    socrates = Philosopher(name="Socrates", quotes=[ Quote(text="The only true wisdom is in knowing you know nothing."), Quote("Wisdom begins in wonder.")], domain=PhilosophyDomain.METAPHYSICS)
    
    philosophers.extend([marcus_aurelius, epictetus, seneca, aristotle, socrates])

def format_query_output(output):
    html = '<nav><ul><li><a href="/">Home</a></li><li><a href="/graphql">/graphqli</a></li><li><a href="/philosophers">/philosophers</a></li><li><a href="/philosopher/name/Marcus">/philosopher/name/{name}</a></li><li><a href="/whosaidthis/life">/whosaidthis/{quote}</a></li><li><a href="/philosopher/domain/stoicism">/philosopher/domain/{domain}</a></li></ul></nav>'
    keys = output.keys()
    key = list(keys)[0]

    html += "<section>"
    for items in output[key]:
        for key, value in items.items():
            html += "<h2>" + str(key).capitalize() + "</h2>"
            if isinstance(value, list): #quotes
                for listitem in value:
                    html += "<blockquote>" + str(listitem["text"]) + "</blockquote>"

            else:
                html += "<p>" + str(value) + "</p>"
        html += "<hr>"
    html += "</section>"

    return add_style(html)

def add_style(html):
    html += "<style>"
    html += "* { font-family: Arial; margin: 0; padding: 0; } "
    html += "section { margin: 15px auto; width: 1000px}"
    html += "p { margin: 15px 0 }"
    html += "hr { margin: 15px 0}"
    html += 'blockquote {  background: #f9f9f9;  border-left: 10px solid #ccc;  margin: 1.5em 10px;  padding: 0.5em 10px; font-style:italic;} '
    html += 'nav ul { list-style-type: none;  margin: 0;  padding: 0;  overflow: hidden;  background-color: #333;}'
    html += 'nav ul li {  float: left;}'
    html += 'nav ul li a {  display: block;  color: white;  text-align: center;  padding: 14px 16px;  text-decoration: none;}'
    html += 'nav ul li a:hover {  background-color: #111;}'
    html += "</style>"
    return html


if __name__ == "__main__":
    seed_philosophers()

    schema = Schema(query=Query)
    #print(schema.execute("{getAllPhilosophers {name, quotes {text}, domain}}"))
    #print(philosophers)

    app = Flask("Philosophy API")
    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

    @app.route('/')
    def welcome():
        home_page = "<section>"
        home_page += "<h1>Philosophy API</h1> <h2>Routes</h2> <h3>GraphQLi</h3>"
        home_page += "<ul><li><a href='/graphql'>/graphqli</a></li></ul>"
        home_page += "<h3>API</h3>"
        home_page += "<ul id='home'>"
        home_page += "<li><a href='/philosophers'>/philosophers</a></li>"
        home_page += "<li><a href='/philosopher/name/Marcus'>/philosopher/name/{name}</a></li>"
        home_page += "<li><a href='/whosaidthis/life'>/whosaidthis/{quote}</a></li>"
        home_page += "<li><a href='/philosopher/domain/stoicism'>/philosopher/domain/{domain}</a></li>"
        home_page += "</ul>"
        home_page += "<p><i>Select a route to proceed.</i></p>"
        home_page += "</section>"
        home_page += "<style>* { font-family: Arial;} </style>"
        return home_page
    
    @app.route('/philosophers')
    def getAllPhilosophers():
        result = schema.execute("{getAllPhilosophers {name, quotes {text}, domain}}")
        return format_query_output(result.data)

    @app.route('/philosopher/name/<name>')
    def getPhilosopherByName(name):
        result = schema.execute('{getPhilosopherByName(name: "' + str(name) + '") {name, quotes {text}, domain}}')
        return format_query_output(result.data)

    @app.route('/whosaidthis/<quote>')
    def whoSaidThis(quote):
        result = schema.execute('{whoSaidThis (quote: "' + str(quote) + '") {name, quotes {text}, domain}}')
        return format_query_output(result.data)

    @app.route('/philosopher/domain/<domain>')
    def findByDomain(domain):
        result = schema.execute('{findByDomain (domain: "' + str(domain) + '") {name, quotes {text}, domain}}')
        return format_query_output(result.data)

    app.run()
