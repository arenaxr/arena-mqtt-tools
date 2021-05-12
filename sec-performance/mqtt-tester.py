
import argparse
from datetime import datetime, timedelta
import jwt
import string
import numpy as np
import paho.mqtt.client as mqtt
import logging
import time
import uuid
import random

# config number of topics generated (range [min, max])
min_topics=10
max_topics=100

# config number of subtopics in each topic (range [min, max])
min_subtopics=5
max_subtopics=10

# config probability of '+' in sub topics
sub_plus_probability=.1

# config number of publications and subscriptions made (range [min, max])
min_n_pub=1000
max_n_pub=2000
min_n_sub=1000
max_n_sub=2000

# config probablity that topics used for pub/sub are not in the allowed list
not_in_list_prob=0

def random_subtopic(min_str_len, max_str_len, plus_probability):
    if np.random.binomial(n=1, p=plus_probability): return '+' # insert a '+' subtopic with plus_probability
    # return a random string with min_str_len <= len <= max_str_len
    letters = string.ascii_letters
    str_len = np.random.randint(min_str_len, max_str_len)
    return ''.join(random.choice(letters) for i in range(str_len))

def random_topic_list(min_n=1, max_n=20, min_subtopics=5, max_subtopics=10, min_subtopic_len=5, max_subtopic_len=10, prefix='', suffix='/#', suffix_probability=.5, plus_probability=0):
    topic_list = []
    n = np.random.randint(min_n, max_n)
    for i in range(n):
        # generate a topic with [min_subtopics, max_subtopics]: subtopic1/subtopic2/subtopic3..;
        n_subtopics=np.random.randint(min_subtopics, max_subtopics)
        topic = '/'.join(random_subtopic(min_subtopic_len, max_subtopic_len, plus_probability) for i in range(n_subtopics))
        if np.random.binomial(n=1, p=suffix_probability): topic = topic + suffix # add suffix at the end with suffix_probability
        topic_list.append(topic)
    return topic_list

def subscribe_subtopic(st, plus_probability):
    if np.random.binomial(n=1, p=plus_probability): return '+'
    return st

def subscribe_topic(topic, plus_probability, suffix_probability=.5):
    subtopics = topic.split('/')
    subtopics_len=np.random.randint(1, len(subtopics))
    topic = '/'.join(map(lambda st: subscribe_subtopic(st, plus_probability), subtopics[:subtopics_len]))
    if np.random.binomial(n=1, p=suffix_probability): topic = topic + '/#'
    return topic

def generate_token(username, keypath, sub_topics=['#'], pub_topics=['#']):
    now = datetime.utcnow()
    claim = {
        "sub": username,
        "subs": sub_topics,
        "publ": pub_topics,
        'iat': now,
        'exp': now + timedelta(days=365)
    }
    with open(keypath, 'r') as keyfile:
        key = keyfile.read()
    token = jwt.encode(claim, key, algorithm='RS256')
    return {
        "username": username,
        "token": token
    }

def on_connect(mqttc, obj, flags, rc):
    if not rc==0:
        printf("Error Connecting")
        exit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store', dest='seed', default=None, help='PRNG seed')
    parser.add_argument('--nosec', dest='nosec', action='store_true', default=False)
    args = parser.parse_args()

    np.random.seed(int(args.seed))
    random.seed(int(args.seed))

    print('##SEED', args.seed)

    username='mqtt-test'
    pubs = random_topic_list(min_n=min_topics, max_n=max_topics, min_subtopics=min_subtopics, max_subtopics=max_subtopics, suffix_probability=0) # no suffix and no '+'

    # reinit random seed; everyone creates same pub list, but everything else is different
    np.random.seed()
    random.seed()

    #subs = random_topic_list(min_subtopics=min_subtopics, max_subtopics=max_subtopics, plus_probability=sub_plus_probability) # add suffix ('/#') to 50%; add '+' to 10%
    # generated a list of sub topics based on pub topics
    subs = list(map(lambda t: subscribe_topic(t, plus_probability=sub_plus_probability), pubs))

    #print(pubs)
    #print(subs)

    mqttc = mqtt.Client(f'mqtt-test-{str(uuid.uuid4())}', clean_session=True)
    mqttc.on_connect = on_connect
    port=21883
    if not args.nosec:
        creds = generate_token(username, './keys/jwt.priv-arena0.pem', sub_topics=subs, pub_topics=pubs)
        mqttc.username_pw_set(username=creds['username'], password=creds['token'])
        port=18883
    print()
    mqttc.connect("arena0.andrew.cmu.edu", port)

    # subscribe to some random topics; some in the subscribe list, some not
    for i in range(np.random.randint(min_n_sub, max_n_sub)):
        index=0
        if len(subs) > 1: index = np.random.randint(0, len(subs)-1)
        topic = subs[index]
        if np.random.binomial(n=1, p=not_in_list_prob): # not_in_list_prob will not be in the list
            topic = random_topic_list(min_n=1, max_n=2, min_subtopics=min_subtopics, max_subtopics=max_subtopics, plus_probability=sub_plus_probability)[0]
        print(f'subscribing: {topic}')
        mqttc.subscribe(topic)
        time.sleep(.001)

    # give some time for others to subscribe
    time.sleep(2)

    # publish some random strings to random topics; some in the publish list, some not
    string_list = random_topic_list(min_n=min_n_pub, max_n=max_n_pub, min_subtopics=1, max_subtopics=2, suffix_probability=0, plus_probability=0) # generate a random word list
    for s in string_list:
        index=0
        if len(pubs) > 1: index = np.random.randint(0, len(pubs)-1)
        topic = pubs[index]
        if np.random.binomial(n=1, p=not_in_list_prob): # not_in_list_prob will not be in the list
            topic = random_topic_list(min_n=1, max_n=2, min_subtopics=min_subtopics, max_subtopics=max_subtopics, suffix_probability=0)[0]
        print(f'publishing: {s} to {topic}')
        mqttc.publish(topic, s)
        time.sleep(.001)

if __name__ == "__main__":
    main()
