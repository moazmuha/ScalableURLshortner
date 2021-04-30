# Scalable URL Shortner

•URL Shortner running on Docker Containers storing records in Cassandra and caching in Redis<br>
•Scalable URL shortener created using Docker containers running on multiple servers <br>
•Records stored in Cassandra and cached in Redis<br>
•Flask was used to handle web requests for PUTs and GETs<br>

## Contents
1. [Introduction](#introduction)
2. [Guide](#guide)
3. [Contributors](#Contributors)

## Introduction
This application was deployed using a docker stack which consisted of 15 replicas of the URL shortner webservice, 5 Cassandra nodes running across 5 systems, 1 visualizer running on the manager node and 1 Redis node also running on the manager node. Everything was run on Linux systems. Their are scripts to start up the all the services as well as to take them down. In the [guide](#guide) below we will be just working with 2 Linux VMs. I will walk you through getting the service up and running. This is a scalable application you can add more systems if you like. 

## Guide 
Prerequisites: Atleast 2 linux systems with docker installed. If you get any docker permission errors, take a look at [Permission Denied Issue](https://stackoverflow.com/questions/48957195/how-to-fix-docker-got-permission-denied-issue). You can download VM images [here](https://www.linuxvmimages.com/) if you need access to Linux systems. Another option is to also deploy this application on AWS using 2 or more Linux instances. In this guide I will be using a Ubuntu 20.04 VM and a Kali linux VM simply because these are the VMs I have currently available to me. 
1. Download or clone this repo onto your first Linux system. 
2. Give executable permissions to startCassandraCluster, stopCassandraCluster, docker/startDockerService, and docker/endDockerService. (chmod +x startCassandraCluster stopCassandraCluster docker/startDockerService docker/endDockerService)
3. Get the IP of both your Linux systems. (ifconfig)
4. Make sure you can SSH into the other system(s) from the first system. 
5. Run "./startCassandraCluster USER@IP1 USER@IP2". (Example: ./startCassandraCluster ubuntu@192.168.22.131 kali@192.168.22.133) Note: You will have to repeatedly enter the other Linux systems' password unless you set up paswordless SSH. Take a look at (this) for more information on setting up paswordless SSH.
6. Check that the Cassandra nodes are up using docker container ls on each Linux system. You should see somrthing like:
![Ubuntu_20 04 2_VM_LinuxVMImages_1-2021-04-30-17-01-38](https://user-images.githubusercontent.com/66569506/116753973-fba5b000-a9d5-11eb-992a-bd22d0466b98.png)
7. Now open up cassandraCommands.txt. Copy paste each command in the shell to create the necessary Keyspaces and tables for Cassandra.
8. Edit docker-compose.yml according to the comments. The data directory is where the Redis appendonly.aof file will be saved. You may also chose to chnage the number of replicas of the URL shorther web service. In this case we will be running 2 replicas on each system.
9. Now run "./startDockerService USER@IP1 USER@IP2". The manager node will be the first system provided. (Example: ./startDockerService ubuntu@192.168.22.131 kali@192.168.22.133)
10. Head over to http://localhost:8080/. You should be able to see all your systems and the containers running. There are 2 urlshortner services running on each system since we set replicas: 4 and max_replicas_per_node: 2.
![Ubuntu_20 04 2_VM_LinuxVMImages_1-2021-04-30-13-01-06](https://user-images.githubusercontent.com/66569506/116756517-40cbe100-a9da-11eb-830f-a476670f6355.png)
11. To add a record you can use an application like Postman or simple use curl to make a put command. (Example: curl -X PUT "http://localhost:4000/?short=myGithub&long=github.com/moazmuha"). In this example the short URL is myGithub and it will redirect to the longer URL is github.com/moazmuha
12. You should get a "Succeded" response. To test whaether you record was saced successfully. Open a browser and head over to http://localhost:4000/myGithub where you would replace myGithub with your short URL. You should be redirected to your long URL.![Animation](https://user-images.githubusercontent.com/66569506/116758395-e896de00-a9dd-11eb-8b5d-86b51ede6179.gif)
13. You can try to test scripts in docker/app/. You can also shutdown containers and keep making requests. Docker will automatically restart containers that shu
14. To shutdown everthing simply run "./endDockerService USER@IP1 USER@IP2" and "./stopCassandraCluster USER@IP1 USER@IP2". (Example: ./endDockerService ubuntu@192.168.22.131 kali@192.168.22.133 and ./stopCassandraCluster ubuntu@192.168.22.131 kali@192.168.22.133)

## Contributors
•[Muhammad Moaz](https://github.com/moazmuha)
•[Muhammad Huzaifa](https://github.com/waifa)
•[Hamza Khan](https://www.linkedin.com/in/hamza-khan-46882b17b/)

