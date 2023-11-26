from socket import *
import sys 
import requests
# will use threads in a producer-consumer model 
from threading import Thread
#use a queue used by the producer and consuser thread 
from queue import Queue
# other aux.
#from manifest import trackContents, parseContents, requestGetWithRange

PLAYER_PORT=8000        # Port where player is wtleg to play
DASH_SERVER_PORT=9999       #Server with the sedia contents
PROXY_PORT=1234        #Port of the proxy


trackHeader = []
trackOffsets = []
manifest_file_path = 'manifest.txt'
trackRead = False




def getManifest(urlBase, movieName):

    url = f"{urlBase}{movieName}/{'manifest.txt'}"

    try:
        # Make a GET request to download the file
        print(url)
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("File download successful!")
            
            # Save the file locally
            with open("manifest.txt", "wb") as file:
                file.write(response.content)
            
            print("File saved as 'manifest.txt'")
        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



def readManifest(movieName, track):

    trackStartMarker = f"{movieName}-{track}.mp4"
    offsetStartMarker = '0'
    endMarker = f"{movieName}-{track+1}.mp4"
    headerReading = False
    offsetReading = False

    with open(manifest_file_path, 'r') as file:
        for line in file:

        # Split the line into a list of values      
            values = line.strip().split() 

            if line.strip() == trackStartMarker:
                headerReading = True
                trackHeader.append(line.strip().split())
                continue
            elif line.strip().split()[0] == offsetStartMarker and headerReading == True:
                headerReading = False
                offsetReading = True
            elif line.strip() == endMarker:
                break

            if headerReading:
                trackHeader.append(line.strip().split())

            if offsetReading:
                trackOffsets.append(line.strip().split())
            
        print(trackHeader)   
        print(trackOffsets)
        
                                                          

def producer(arg):
    
    #arg(e] urlBase, arg[1] movieName, arg[21 track, arg(3] queue, arg(4] socket already connected
    urlBase = arg[0]
    movieName = arg[1]
    track = arg[2]
    segmentQueue = arg[3]
    sock = arg[4]

    for i in range(int(trackHeader[4][0])):
#        segment = .... TODO
#        put i, segment in the queue
#        until last segment recieved

        url = f"{urlBase}{movieName}/{movieName}-{track}.mp4"

        try:
            chunkRange = 'bytes={}-{}'.format(int(trackOffsets[i][0]), int(trackOffsets[i][0])+int(trackOffsets[i][1])-1)
            #print(chunkRange)

            response = requests.get(url, headers={'Range':chunkRange})

            if response.status_code == 206:
                queue.put(response.content)
            else:
                raise Exception('Error retrieving chunk: {}'.format(response.status_code))

        # Check if the request was successful (status code 200)
            
        except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

        #print('chunk downloaded')

    trackRead = True
    print("Producer: Ok all segments queued")
    #print(queue)




def consumer(arg): #arg[0] queue, arg[1] socket already connected

    i=0

    segmentQueue = arg[0]
    socket = arg[1]
    print("Consumer: ", segmentQueue)

    #consumer send segmentQueue to player.py through socket
    while True:
        i+=1
        print(i)
        print(segmentQueue)
        segment = segmentQueue.get()
        print(segment)
        
        socket.sendall(segment)
        print("Consumer: sent segment to player")

        if not trackRead:
            continue
        else:
            break

    print("Consumer: all segments sent to the player")


#while True:

    #get a segment from the queue
    #seg = ...
    #if seg = None:
    #   break
    #send seg to player

    #print('Consumer: all segments sent to the player')




if __name__ == '__main__':

    #python proxyprog urlBase movieName, track

    if len(sys.argv) == 4:
        urlBase = sys.argv[1]
        movieName = sys.argv[2]
        track = int(sys.argv[3])
        #proxy socket to connect and send things to the player

        sp = socket(AF_INET, SOCK_STREAM)
        sp.connect(("localhost", PLAYER_PORT))

        #proxy socket to connect and to recieve from the dash docker server
        sd = socket(AF_INET, SOCK_STREAM)
        sd.connect(("localhost", DASH_SERVER_PORT))

        getManifest(urlBase, movieName)
        readManifest(movieName, track);

        #Shared queue for proxy treads producer and consumer
        queue = Queue()
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