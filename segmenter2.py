#!/usr/bin/env python

import argparse
import logging
import time
from urlparse import urlparse
import tempfile
import subprocess
import shutil
import requests

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Pull audio stream into a file')
    parser._optionals.title = "Options"

    parser.add_argument('-p', '--audio-url', help='URL from which to stream audio',
                        type=str, default="http://edge.espn.cdn.abacast.net/espn-wepnmp3-32?source=tunein")
    parser.add_argument('-k', '--kluge-web-server', help='URL to post audio',
                        type=str, default="http://kluge-web.marathon.mesos:5000")
    parser.add_argument('-c', '--chunk-size', help='Chunk size in bytes',
                        type=int, default=250000)
    parser.add_argument('-r', '--rate', help='Rate control: sleep time in seconds between pulls',
                        type=int, default=0)
    return parser.parse_args()


def gen_stream_chunk(stream_url, chunk_size):
    r = requests.get(stream_url, stream=True)
    print "Starting to read bytes from stream"
    for b in r.iter_content(chunk_size=chunk_size):
        yield b


def main():
    args = parse_arguments()

    # Audio connection
    audio_server = urlparse(args.audio_url)
    host = str(audio_server.hostname)

    directory_name = ""
    chunkid = 1
    timestamp = str(time.time()).split(".")[0]
    try:
        for buff in gen_stream_chunk(args.audio_url, args.chunk_size):
            print "Received bytes from stream"
            directory_name = tempfile.mkdtemp()
            raw_file = directory_name + "/radio.mp3"
            with open(directory_name + "/radio.mp3", 'wb') as outfile:
                outfile.write(buff)

            mulaw_file = directory_name + "/radio.ul"
            sox_command = "sox -V %s -r 8000 -b 8 -c 1 -t ul %s" % (raw_file, mulaw_file)

            print mulaw_file
            return_code = subprocess.call(sox_command, shell=True)

            if not return_code == 0:
                shutil.rmtree(directory_name)
                continue

            if return_code:
                print "Chunk of radio data converted to mulaw"

            curl_command = 'curl -F "docid={0}" -F "chunkid={1}" -F "name={2}" ' \
                           '-F "bytes=@{3}" ' \
                           '{4}/jobs/english'.format(host + "-" + timestamp, str(chunkid), host + "-" + timestamp, mulaw_file, args.kluge_web_server)

            print curl_command
            return_code = subprocess.call(curl_command, shell=True)

            if return_code:
                print "Audio posted to kluge-web"

            chunkid += 1
            time.sleep(args.rate)
    finally:
        # Clean up the directory yourself
        shutil.rmtree(directory_name)


if __name__ == '__main__':
    main()
