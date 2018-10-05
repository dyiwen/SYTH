#!/usr/bin/env python
# encoding: utf-8

import redis

if __name__=="__main__":
    channel = "prediction"
    rcon = redis.Redis()
    rcon.publish(channel, 'kill')
