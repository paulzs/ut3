import gevent
from gevent.queue import Queue
from gevent.event import Event
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError

class MatchMaker(object):
    def __init__(self):
        self.waiting_players = []

    def request_challenger(self, player):
        """
        If there are challengers waiting, request_challenger matches given
        player with a challenger by setting the Player.challenger_notifier
        with the matched Player. If not challengers available, places given
        player on the wait queue.
        """
        if len(self.waiting_players) != 0:
            # some players may already be disconnected (because they have been
            # waiting so long), so we must iterate through and check before
            # setting a challenger.
            while len(self.waiting_players) != 0:
                challenger = self.waiting_players.pop(0)
                if not challenger.ping():
                    challenger.exit()
                    continue
                challenger.challenge_notifier.set(player)
                player.challenge_notifier.set(challenger)
        else:
            self.waiting_players.append(player)

class Player(gevent.Greenlet):
    def __init__(self, name, websocket, match_maker):
        gevent.Greenlet.__init__(self)
        self.name = name
        self.ws = websocket
        self.match_maker = match_maker
        self.ponged = False
        self.victorious = Event()
        self.defeated = Event()

        self.received_queue = Queue()
        self.challenge_notifier = gevent.event.AsyncResult()

    def __str__(self):
        return "Player(name="+self.name+")"

    def _run(self):
        self._receiver_greenlet = gevent.spawn(self._receiver)
        self.match_maker.request_challenger(self)
        print(self.name + " waiting for challenger...")
        self.challenger = self.challenge_notifier.get()
        print(self.name + " received challenger: " + self.challenger.name)
        self.play()

    def _receiver(self):
        while True:
            try:
                message = self.ws.receive()
            except WebSocketError as e:
                print(self.name + " failed to receive message: " + str(e))
                self.exit()
            if message == "pong":
                self.ponged = True
            else:
                self.received_queue.put(message)

    def _wait_for_pong(self, timeout=5):
        """
        Waits for a pong message from websocket
        """
        if self.ponged == True:
            self.ponged = False
            return True
        else:
            gevent.sleep(timeout)
            if self.ponged == True:
                self.ponged = False
                return True
            else:
                return False

    def signal_victory(self):
        self.victorious.set()

    def signal_defeat(self):
        self.defeated.set()

    def exit(self):
        print(self.name + ": exiting")
        if hasattr(self, "challenger"):
            self.challenger.signal_victory()
        gevent.killall([self._receiver_greenlet])
        self.ws.close()
        raise gevent.GreenletExit

    def ping(self, timeout=5):
        """
        Pings websocket and returns true if ping successful. timeout specifies
        the amount of time to wait for a pong from this Player's websocket in
        seconds
        """
        try:
            self.ws.send("ping")
        except WebSocketError as e:
            print(self.name + ": failed to send ping: " + str(e))
            return False
        return self._wait_for_pong(timeout=timeout)

    def send(self, message):
        """
        Send a message to this Player
        """
        try:
            self.ws.send(message)
        except WebSocketError as e:
            print(self.name + ": failed to send message: " + str(e))
            self.exit()

    def play(self): # wait on websocket and message queue
        message = self.received_queue.get()
        self.challenger.send(message)

class Game(object):
    def __init__(self):
        self.match_maker = MatchMaker()
        self.players = {}

    def add_player(self, player):
        print(player.name + " joined the game")
        self.players[player.name] = player

    def remove_player(self, player):
        print("Removing: " + player.name + " from the game")
        del self.players[player.name]

    def connect_handler(self, environ, start_response):
        if environ['PATH_INFO'] == '/test':
            start_response("200 OK",[('Content-Type', 'text/plain')])
            return ["This is a test"]
        elif environ['PATH_INFO'] == '/talk':
            ws = environ['wsgi.websocket']
            name = ':'.join([str(x) for x in ws.stream.handler.client_address])
            player = Player(name, ws, self.match_maker)
            self.add_player(player)
            player.link(self.remove_player)
            player.start()
            player.join()
        return "true"

if __name__ == '__main__':
    game = Game()
    wsserver = WSGIServer(('0.0.0.0',8000), game.connect_handler, handler_class=WebSocketHandler)
    wsserver.serve_forever()
