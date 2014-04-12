from flask import Flask
import flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import gevent

app = Flask(__name__)

@app.route('/')
def hello():
    return "<b>hello world</b>"

@app.route('/persons/<string:person>')
def get_persons(person):
    if person.lower() != 'alex':
        adj='boss'
        return flask.render_template('index.html', person=person,adj=adj)
    else:
        adj='fabulous unicorn'
        return flask.render_template('index.html', person=person,adj=adj)

@app.route('/talk')
def talk():
    ws = flask.request.environ.get('wsgi.websocket')
    if ws:
        print(dir(ws))
        print("valid websocket")
        ws.send("hello world")
        spawned_process = gevent.spawn(handle_ws, ws)
        print(ws.closed)
        gevent.joinall([spawned_process])
        return "true"
    return "true"

def handle_ws(ws):
    print("handling")
    while 1:
        msg = ws.receive()
        ws.send(msg)

if __name__ == '__main__':
    server = WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
