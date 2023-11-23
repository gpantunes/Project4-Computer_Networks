from socket import *
import sys 
import requests
# will use threads in a producer-consumer model 
from threading import Thread
#use a queue used by the producer and consuser thread 
from queue import Queue
# other aux.
from manifest import trackContents, parseContents, requestGetWithRange

PLAYER_PORT=8000        # Port where player is wtleg to play
DASH_SERVER_PORT=9999       #Server with the sedia contents
PROXY_PORT=1234        #Port of the proxy


def producer(arg) :
    
    #arg(e] urlBase, arg[1] novicNane, arg[21 track, arg(3] queue, arg(4] socket already connected
    urlBase = arg[0]
    movieName = arg[1]
    track = arg[2]
    segmentQueue = arg (3)
    sock = arg (4)

    print(urlBase, movieName, track, segmentQueue)
    manifestuRL = urlBase+'/'+movieName+' /nanifest. txt'
    sucess, manifestFileContents = trackContents (manifestURL)
    trackFile, noSegnents, segnents = parseContents (manifestfileContents, track)
    urlTrackFile = urlBase+'/'+movieName+'/'+trackFile



    for i in range(noSegments):
#        segment = .... TODO
#        put i, segment in the queue
#        until last segment recieved
        print("Producer: Ok all segments queued")


def consumer(arg): #arg[0] queue, arg[1] socket already connected

    segmentQueue = arg[0];
    print("Consumer: ", segmentQueue);





    #outra função maybe

while True:

    #get a segment from the queue
    #seg = ...
    #if seg = None:
    #   break
    #send seg to player

    print('Consumer: all segments sent to the player')


if __name__ == '__main__':

    #python proxyprog urlBase movieName, track

    if len(sys.argv) == 4:
        urlBase = sys.argv[1]
        movieName = sys.argv[2]
        track = int(sys.argv[3])
        #proxy socket to connect and send things to the player
        sp = socket(AF_INET, SOCK_STREAM)
        sp.connect(("localhost", PLAYER_PORT))

        #proxy socket to connect an to recieve from the dash docker server
        sd = socket(AF_INET, SOCK_STREAM)
        sd.connect(("localhost", DASH_SERVER_PORT))

        #Shared queue for proxy treads producer and consumer
        queue = Queue();
        #proxy go to start the producer
        #need to pass everything needed by the producer thread
        arg = (urlBase, movieName, track, queue, sd)
        producer = Thread(target = producer, args = (arg,))
        #and fire the producer thread
        producer.start()


        #proxy go to start the consumer
        arg = (queue, sp)
        consumer = Thread(target = consumer, args = (arg,))
        consumer.start()


        #now things are running
        #proxy only needs to wait for the producer and consumer treads to finish
        producer.join()
        consumer.join()


        #and now we can close the sockets and connections
        sd.close()
        sp.close()

    else: 
        #input arguments for proxy are incorrect
        print('Command line provided not correct')
        print('Use: myproxy.py urlBase movieName track')