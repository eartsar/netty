from flask import Flask, jsonify, render_template, request, current_app, Response
import client
import redis

app = Flask(__name__)
app.secret_key = 'asdf'
red = redis.StrictRedis()
app.debug = True
app.threaded = True
app.clients = {}
app.uid = 1

def event_stream(uid):
    pubsub = red.pubsub()
    pubsub.subscribe(str(uid))
    for message in pubsub.listen():
        data = str(message['data'])
        lines = data.split("\n")
        # this is a fix for multi-line input
        for i in range(len(lines)):
            if i == len(lines) - 1:
                yield 'data: ' + lines[i] + '\n\n'
            else:
                yield 'data: ' + lines[i] + '\n'


@app.route('/stream')
def stream():
    uid = request.args.get('uid')
    print "Event stream now serving: UID " + str(uid)
    return Response(event_stream(uid), mimetype="text/event-stream")


@app.route('/_send')
def send():
    line = request.args.get('line', '', type=str)
    uid = request.args.get('uid', '', type=str)
    if uid in current_app.clients:
        current_app.clients[uid].send_input(line)
    return Response(status=204)


def recv(text, uid):
    red.publish(str(uid), text)


@app.route('/_register')
def register():
    uid = current_app.uid
    try:
        current_app.clients[str(uid)] = client.Client(callback=recv, uid=uid)
        current_app.uid += 1
    except:
        # In the case of an exception being thrown, it means the server is now up.
        uid = 0
    return jsonify({"uid": uid})


@app.route('/')
def index():
    val = render_template('index.html')
    print "Serving: " + str(request.remote_addr)
    return val


if __name__ == '__main__':
    app.debug = True
    app.threaded = True
    app.run()
