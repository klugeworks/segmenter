#!/usr/bin/env python

import argparse
import logging
import redis
import os
import time
import glob
from urllib2 import urlopen
from urlparse import urlparse
from pycube.io.tokenizer_job_pb2 import TokenizerJobMessage

logger = logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Enqueue chunks from audio stream to work queue')
    parser._optionals.title = "Options"

    parser.add_argument('-r', '--redis-server', help='The Redis instance to connect to for work.',
                        type=str, required=True)
    parser.add_argument('-src', '--work-queue', help='The queue to add work to',
                        type=str, required=True)
    parser.add_argument('-p', '--audio-url', help='URL from which to stream audio',
                        type=str, required=True)
    parser.add_argument('-p', '--chunk-size', help='Approximate chunk size in seconds',
                        type=int, required=True)
    return parser.parse_args()


def get_stream_chunk(stream_url, duration):
    not_ready = True
    buffer = ''
    try:
        stream = urlopen(stream_url)
        start_time = time.time()
        while not_ready:
            buffer.append(stream.read(44100))
            if time.time() - start_time > duration:
                not_ready = False
    except Exception as e:
        raise e
    return buffer


def main():
    args = parse_arguments()

    # Set up connection to Redis
    rs = urlparse(args.redis_server)
    port = 6379
    if rs.port is not None:
        port = rs.port
    r = redis.StrictRedis(host=rs.hostname, port=port, db=0)
    logger.info('Connected to redis')

    stream = urlopen(args.audio_url)
    job = TokenizerJobMessage()
    chunk_start = time.time()
    buffer = ''
    while True:
        buffer.append(stream.read(44100))
        if time.time() - chunk_start > args.chunk_size:
            job = TokenizerJobMessage()
            job.raw_audio = buffer
            logger.info('Submitting job')
            r.lpush(args.work_queue, job.SerializeToString())
            buffer = ''


if __name__ == '__main__':
    main()
