import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

def ws_handler(environ, start_response):
	if environ['PATH_INFO'] == '/test':
		start_response("200 OK",[('Content-Type', 'text/plain')])
		return ["This is a test"]
	elif environ['PATH_INFO'] == '/talk':
		ws = environ['wsgi.websocket']
		message = ws.receive()
		ws.send(message)
		return "talk talk talk"

if __name__ == '__main__':
	wsserver = WSGIServer(('0.0.0.0',8000), ws_handler, handler_class=WebSocketHandler)
	wsserver.serve_forever()
