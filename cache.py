# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Helen Zhao
# For 2019 Telstra Graduate Program IT&DS case study

from flask import Flask, abort, request, jsonify
import time
from threading import Timer, Thread
from time import sleep
app = Flask(__name__)

TTL=30
cache_pool = []


class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")
    
    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()
    
    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None

'''
Store a document in the cache
'''

@app.route('/messages/', methods=['POST'])
def store_document():

    if not request.json or 'id' not in request.json or 'message' not in request.json:
        return jsonify({'Result': 'Failed, Malformed document'})

    document = {
        'id': request.json['id'],
        'message': request.json['message'],
        'time':int(time.time())
    }
    cache_pool.append(document)
    return jsonify({'Result': 'Stored successfully'})


'''
Retrieve a document form the cache 
'''

@app.route('/messages/<int:doc_id>', methods=['GET'])
def retrieve_document(doc_id):

	doc_found = filter(lambda t: t['id'] == int(doc_id), cache_pool)
	if len(doc_found) ==0:
		return jsonify({'Result': 'Resource not found.'})
	document = {
		'id': doc_found[0]['id'],
		'message': doc_found[0]['message']
	}
	return jsonify(document)

'''
Clear all documents in the cache
'''	

@app.route('/messages/clear', methods=['GET'])
def clear_cache():
	for x in cache_pool: 
		cache_pool.remove(x) 
	return jsonify({'Result': 'Documents deleted'})


'''
Check if time is out, remove the document from cache when it reach TTL
'''

def time_out_check():
	now = int(time.time()) 
	for x in cache_pool:   
		if now - x['time'] > TTL:  
			print 'TTL TIMEOUT'  
			cache_pool.remove(x)


if __name__ == "__main__":
	scheduler = Scheduler(1, time_out_check)
	scheduler.start()
	app.run(host="0.0.0.0", port=8383, debug=True)
	scheduler.stop()
