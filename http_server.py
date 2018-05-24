#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
from flask import jsonify

import rethinkdb as r

from random import randint
from time import time, sleep
from threading import Thread
from requests import get, post
from subprocess import Popen, PIPE

import json
import os

app = Flask(__name__)

ADDRESS = {
    'ftp': None,
    'rdb': None,
    'http': None
}

def run(command):
    process = Popen(command, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().strip()
        if not line:
            break
        yield line
        sleep(0.1)

def update_address(server, port):
    name = os.getenv("MUNYAL_NAME")
    while True:
        for line in run("ssh -R 0:localhost:{} serveo.net".format(port)):
            try:
                address = str(line).split("from ")[1].split("\n")[0].strip()
                address = address.strip("'")
                ADDRESS[server] = address
                response = get("http://localhost:5000/directory", params={"name": name})
                response = json.loads(response.text)
                print(response.get("status")+"\t"+response.get("message")+"\t"+str(ADDRESS))
                if response.get("status") == "ok":
                    if response.get(server+"_address") != address:
                        if ADDRESS['ftp'] and ADDRESS['rdb'] and ADDRESS['http']:
                            with open("$HOME/.munyal/config/token", "r") as f:
                                token = f.read()
                            post("http://localhost:5000/directory", data={
                                'name': name,
                                'http_address': ADDRESS['http'],
                                'ftp_address': ADDRESS['ftp'],
                                'rdb_address': ADDRESS['rdb'],
                                'token': token
                            })
                elif "servidor se ha registrado" in response.get("message"):
                    if ADDRESS['ftp'] and ADDRESS['rdb'] and ADDRESS['http']:
                        r = post("http://localhost:5000/directory", data={
                            'name': name,
                            'http_address': ADDRESS['http'],
                            'ftp_address': ADDRESS['ftp'],
                            'rdb_address': ADDRESS['rdb']
                        })
                        r = json.loads(r.text)
                        with open("$HOME/.munyal/config/token", "w") as f:
                            f.write(r.get('token'))
            except:
                sleep(1)
        sleep(1)

@app.route("/", methods=["GET"])
def index():
    return('''
    <html>
        <head>
            <title>Munyal API</title>
        </head>
        <body>
            <h1>Munyal private API</h1>
        </body>
    </html>
    ''')

@app.route("/upload", methods=["POST"])
def upload():
    try:
        r.connect( "localhost", 28015).repl()
        cursor = r.table("changes")
        
        host = request.form.get("host")
        action = request.form.get("action")
        route = request.form.get("route")
        obj = {
            'id' : str(time()).split('.')[0] + str(randint(1, 1000000)),
            'action': action,
            'route': route,
            'host': host
        }
        status = 'ok'
        try:
            cursor.insert(obj).run()
        except:
            status = 'error'
    except:
        status = 'error'
    obj['status'] = status
    return jsonify(obj)
    

if __name__ == '__main__':
    # ~ http_thread = Thread(target=update_address, args=("http", "5010"))
    # ~ http_thread.setDaemon(True)
    # ~ http_thread.start()
    
    # ~ ftp_thread = Thread(target=update_address, args=("ftp", "80"))
    # ~ ftp_thread.setDaemon(True)
    # ~ ftp_thread.start()
    
    # ~ rdb_thread = Thread(target=update_address, args=("rdb", "27017"))
    # ~ rdb_thread.setDaemon(True)
    # ~ rdb_thread.start()
    
    app.run(debug=True, port= 5000)
