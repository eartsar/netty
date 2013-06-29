from flask import Flask, jsonify, render_template, request, current_app, Response
import client
import redis

app = Flask(__name__)
app.secret_key = 'asdf'
red = redis.StrictRedis()
app.debug = True
app.threaded = True
app.clients = {}

def event_stream(remote_addr):
    pubsub = red.pubsub()
    pubsub.subscribe(str(remote_addr))
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
    return Response(event_stream(request.remote_addr), mimetype="text/event-stream")


@app.route('/_send')
def send():
    line = request.args.get('line', '', type=str)
    current_app.clients[request.remote_addr].send_input(line)
    return Response(status=204)


def recv(text, client_ip):
    red.publish(str(client_ip), text)


@app.route('/')
def index():
    val = render_template('index.html')
    print request.remote_addr
    if request.remote_addr not in current_app.clients:
        current_app.clients[request.remote_addr] = client.Client(callback=recv, client_ip=request.remote_addr)
    return val


if __name__ == '__main__':
    app.debug = True
    app.threaded = True
    app.run()
