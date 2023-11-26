import socket
import subprocess

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

# accept a single connection
connection = server_socket.accept()[0].makefile('rb')
try:
    # Run gstreamer over the connection
    #cmdLine should be the directory/path of the mplayer
    cmdLine = 'mplayer -fps 31 -demuxer h264es -'
    #cmdline = ''
    player = subprocess.Popen(cmdLine.split(), stdin=subprocess.PIPE)
    while True:
        data = connection.read(1024)
        if not data:
            break
        player.stdin.write(data)
finally:      
    connection.close()
    server_socket.close()
    player.terminate()  

