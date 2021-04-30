#!/usr/bin/python
# https://pypi.org/project/cassandra-driver/
# https://docs.datastax.com/en/developer/python-driver/3.24/getting_started/
from cassandra.cluster import Cluster
from redis import Redis, RedisError
from flask import Flask, request, Response, redirect
from datetime import datetime
import time
import os
import socket
from datetime import datetime

redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

# Replace IPs with your server IPs
cluster = Cluster(['192.168.22.131', '192.168.22.129', '192.168.22.132'])
# Connecting to tables in Cassandra
session = cluster.connect('records')
sessionLOG = cluster.connect('log')

# Inserts the short and the long into records table in the Cassandra database
def insert_cassandra(short_url, long_url):

	insert_statement = """
	INSERT INTO urlshorts (short, long)
	VALUES (%s, %s);
	"""
	session.execute(insert_statement, (short_url, long_url))

# Insert log in in logs table in the Cassandra database
def insert_cassandraLOG(datetime, log):

	insert_statement = """
	INSERT INTO logs (datetime, log)
	VALUES (%s, %s);
	"""
	sessionLOG.execute(insert_statement, (datetime, log))


# Get the long associated with the given short from Cassandra
# Also stores the short and long into the redis database
def get_cassandra(short_url):
    
	select_statement = """
	SELECT long FROM urlshorts
	WHERE short=%s;
	"""

	long_row = session.execute(select_statement, [short_url])

	try:

		long_url = long_row[0].long

		if "http://" in long_url[0:7] or "https://" in long_url[0:8]:
				long_url = long_url
		else:
				long_url = "http://" + long_url
		# Since short was not found in cache, store the short in cache
		redis.set(short_url, long_url)
		redis.expire(short_url, 180)
		return long_url

	except:
		return None


app = Flask(__name__)

# PUT route to store the short and longs into the cassandra database
@app.route("/", methods=['PUT'])
def put_request():
    if request.method == 'PUT':
	    args = request.args
	    short_url = args['short']
	    long_url = args['long']
		# Checks if the url is valid
	    if 'short' in args and 'long' in args:
			# Add to Cassandra
		    insert_cassandra(short_url, long_url)
		    now = datetime.now()
		    nowStr = now.strftime("%d/%m/%Y %H:%M:%S")
		    logString = "Successful put request made with short {} and long {} at {}\n".format(short_url, long_url, nowStr)
		    insert_cassandraLOG(nowStr, logString)
		    return Response('Succeeded\n', status=200)
	    else:
		    now = datetime.now()
		    nowStr = now.strftime("%d/%m/%Y %H:%M:%S")
		    logString = "Failed put request made with short {} and long {}\n".format(short_url, long_url)
		    insert_cassandraLOG(nowStr, logString)
		    return Response('Invalid Format\n', status=400)


# GET route to obtain the long associated with the given short
@app.route("/<short>", methods=['GET'])
def get_request(short):
    
	if request.method == 'GET':
		# Checks to see if the short is within the cache
		try:
			if redis.exists(short):
				long_url = redis.get(short)
				logString = "Successful GET request made for short {} correspinding to long {}\n".format(short,long_url)
				now = datetime.now()
				nowStr = now.strftime("%d/%m/%Y %H:%M:%S")
				insert_cassandraLOG(nowStr, logString)
				return redirect(long_url, code=307)

		except RedisError:
			logString = "Error related to Redis"
			now = datetime.now()
			nowStr = now.strftime("%d/%m/%Y %H:%M:%S")
			insert_cassandraLOG(nowStr, logString)
			return Response("An error occurred related to Redis", 404)

		# Retrieve the long if available
		long_url = get_cassandra(short)

		# Checks to see if the short is in the main database and if its not
		# returns a 404 error
		if long_url:
			logString = "Successful GET request made for short {} correspinding to long {}\n".format(short,long_url)
			now = datetime.now()
			nowStr = now.strftime("%d/%m/%Y %H:%M:%S")
			insert_cassandraLOG(nowStr, logString)
			return redirect(long_url, code=307)
		else:
			logString = "Failed GET request made for short {}\n".format(short)
			now = datetime.now()
			nowStr = now.strftime("%d/%m/%Y %H:%M:%S")
			insert_cassandraLOG(nowStr, logString)
			return Response('Page does not exist\n', status=404)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=80, threaded=True)
