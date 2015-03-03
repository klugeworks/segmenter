#!/usr/bin/env python

import argparse
import logging
import os
import time
import glob
from urllib2 import urlopen
from urlparse import urlparse

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Pull audio stream into a file')
    parser._optionals.title = "Options"

    parser.add_argument('-p', '--audio-url', help='URL from which to stream audio',
                        type=str, required=True)
    parser.add_argument('-c', '--chunk-size', help='Approximate chunk size in seconds',
                        type=int, required=True)
    parser.add_argument('-o', '--output', help='URL from which to stream audio',
                        type=str, required=True)
    return parser.parse_args()


def get_stream_chunk(stream_url, duration):
    not_ready = True
    buffer = ''
    try:
        stream = urlopen(stream_url)
        start_time = time.time()
        while not_ready:
            buffer += (stream.read(44100))
            if time.time() - start_time > duration:
                not_ready = False
    except Exception as e:
        raise e
    return buffer


def main():
    args = parse_arguments()
    stream = urlopen(args.audio_url)
    buff = get_stream_chunk(args.audio_url, args.chunk_size)
    with open(args.output, 'wb') as outfile:
        outfile.write(buff)


if __name__ == '__main__':
    main()
