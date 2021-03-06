from flask import Flask
import flask
from flask.ext.socketio import SocketIO, emit
import flask.ext.socketio

#NO LONGER NEEDED. REFERENCE ONLY

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/persons/<string:person>')
def get_persons(person):
	adj='mean gangsta'
	return flask.render_template('index.html',person=person,adj=adj)

# Broadcast
@socketio.on('my broadcast event',namespace='/test')
def test_message(message):
	emit('my response',{'data': message['data']}, broadcast=True)

@socketio.on('connect',namespace='/test')
def test_connect():
	emit('my response',{'data':'Connected'})

@socketio.on('disconnect',namespace='/test')
def test_disconnect():
	emit('my response',{'data':'Disconnected'})

if __name__=='__main__':
	socketio.run(app)
