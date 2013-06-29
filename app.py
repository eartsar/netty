from flask import Flask, jsonify, render_template, request, current_app, Response
import client
import redis

app = Flask(__name__)
app.secret_key = 'asdf'
red = redis.StrictRedis()
app.debug = True
app.threaded = True
app.clients = {}
app.uid = 1337

def event_stream(uid):
    pubsub = red.pubsub()
    pubsub.subscribe(str(uid))
    for message in pubsub.listen():
        data = str(message['data'])
        lines = data.split("\n")
        for i in range(len(lines)):
            if i == len(lines) - 1:
                yield 'data: ' + lines[i] + '\n\n'
            else:
                yield 'data: ' + lines[i] + '\n'


@app.route('/stream')
def stream():
    # need to get some stuff
    uid = request.args.get('uid')
    print "IN STREAM() " + str(uid)
    return Response(event_stream(uid), mimetype="text/event-stream")


@app.route('/_send')
def send():
    line = request.args.get('line', '', type=str)
    uid = request.args.get('uid', '', type=str)
    current_app.clients[uid].send_input(line)
    return Response(status=204)


def recv(text, client_ip):
    red.publish(str(client_ip), text)


@app.route('/_register')
def register():
    uid = current_app.uid
    current_app.clients[str(uid)] = client.Client(callback=recv, client_ip=uid)
    current_app.uid += 1
    return jsonify({"uid": uid})


@app.route('/')
def index():
    val = render_template('index.html')
    print "Serving: " + str(request.remote_addr)
    #if request.remote_addr not in current_app.clients:
    #    current_app.clients[request.remote_addr] = client.Client(callback=recv, client_ip=request.remote_addr)
    return val


if __name__ == '__main__':
    app.debug = True
    app.threaded = True
    app.run()
