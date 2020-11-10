#!/usr/bin/python
# https://pypi.org/project/cassandra-driver/
# https://docs.datastax.com/en/developer/python-driver/3.24/getting_started/
from cassandra.cluster import Cluster
from redis import Redis, RedisError
from flask import Flask, request, Response, redirect
import time
import os
import socket

redis = Redis(host="redis", db=0, socket_connect_timeout=2, socket_timeout=2)

'''
profile = ExecutionProfile(
	load_balancing_policy=WhiteListRoundRobinPolicy(['127.0.0.1']),
	retry_policy=DowngradingConsistencyRetryPolicy(),
	consistency_level=ConsistencyLevel.LOCAL_QUORUM,
	serial_consistency_level=ConsistencyLevel.LOCAL_SERIAL,
	request_timeout=15,
	row_factory=tuple_factory
)
# Can pass in execution profile 
cluster = Cluster(execution_profiles={EXEC_PROFILE_DEFAULT: profile})
'''
# # IPS : 10.11.12.20, 10.11.12.21, 10.11.12.22, 10.11.12.233, 10.11.12,234
cluster = Cluster(['10.11.12.20', '10.11.12.21', '10.11.12.22', '10.11.12.233', '10.11.12.234'])
# # session = cluster.connect()
session = cluster.connect('a2')

# # session.set_keyspace('users')
# # or you can do this instead
# # session.execute('USE users')

# Inserts the short and the long into the cassandra database
def insert_cassandra(short_url, long_url):

	insert_statement = """
	INSERT INTO urlshorts (short, long)
	VALUES (%s, %s);
	"""
	session.execute(insert_statement, (short_url, long_url))

# Get the long associated with the given short from the cassandra
# database and also stores the short and long into the redis database
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

# Put route to store the short and longs into the cassandra database
@app.route("/", methods=['PUT'])
def put_request():

	if request.method == 'PUT':
		args = request.args

		# Checks if the url is valid
		if 'short' in args and 'long' in args:
			# Add to Cassandra
			short_url = args['short']
			long_url = args['long']
			insert_cassandra(short_url, long_url)
			return Response('Succeeded\n', status=200)
		else:
			return Response('Invalid Format\n', status=400)
	
# Get route to obtain the long associated with the given short	
@app.route("/<short>", methods=['GET'])
def get_request(short):
	
	if request.method == 'GET':
		
		# Checks to see if the short is within the cache
		try:
			if redis.exists(short):
				long_url = redis.get(short)
				return redirect(long_url, code=307)

		except RedisError:
			return Response("An error occurred related to redis", 404)
		
		# Retrieve the long if available
		long_url = get_cassandra(short)
		
		# Checks to see if the short is in the main database and if its not
		# returns a 404 error
		if long_url:
			return redirect(long_url, code=307)
		else:
			return Response('Page does not exist\n', status=404)
		
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80, threaded=True)

