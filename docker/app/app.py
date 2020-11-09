#!/usr/bin/python
# https://pypi.org/project/cassandra-driver/
# https://docs.datastax.com/en/developer/python-driver/3.24/getting_started/
from cassandra.cluster import Cluster
from redis import Redis, RedisError
from flask import Flask, request, Response
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
# IPS : 10.11.12.20, 10.11.12.21, 10.11.12.22, 10.11.12.233, 10.11.12,234
cluster = Cluster(['10.11.12.20'])
# session = cluster.connect()
#session = cluster.connect('a2')
session = cluster.connect('a2')

# session.set_keyspace('users')
# or you can do this instead
# session.execute('USE users')

def insert_cassandra(short_url, long_url):
	
	insert_statement = """
	INSERT INTO urlshorts (short, long)
	VALUES (%s, %s);
	"""
	session.execute(insert_statement, (short_url, long_url))


def get_cassandra(short_url):

	get_statement = """
	SELECT long from urlshorts
	WHERE short=(%s);
	"""
	
	return session.execute(get_statement, (short_url))

app = Flask(__name__)

@app.route("/", methods=['GET', 'PUT'])
def hello():
		
	if request.method == 'PUT':
		args = request.args
	
		if 'short' in args and 'long' in args:
			# Add to Cassandra
			short_url = args['short']
			long_url = args['long']
			
			return Response('Succeeded\n', status=200)
		else:
			return Response('Invalid Format\n', status=400)
	
	if request.method == 'GET':
		#Get from Redis
			#if successful, return 307
		
		# If not in redis, get from cassandra and add to redis
			# If successful, return 307
		
		#test = get_cassandra(request.full_path)
		#return (test, status=307)

		# If not in either, return 404
		pass
	
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=80)

