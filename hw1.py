#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import xml.etree.ElementTree as ElementTree

DEFAULT_N_GRAM_CNT=2

config = {
        'query_file': None,
        'ranked_list': None,
        'model_dir': None,
        'vocab': None,
        'file_list': None,
        'inverted_index': None,
        'ntcir_dir': None,
        'relevance_feedback': None,
        'tool_dir': None
        }

class Query:
    def __init__(self, topic):
        self.title = topic.find('title').text
        self.number = topic.find('number').text[-3:]
        self.question = topic.find('question').text.strip()
        self.narrative = topic.find('narrative').text.strip()
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()

def create_ngram(raw_query_string, n=DEFAULT_N_GRAM_CNT):
    create_ngram_cmd = '%s/create-ngram -vocab %s -tmp . -n %d' % (config['tool_dir'], config['vocab'], n)
    raw_result = subprocess.check_output('echo \'%s\' | %s' % (raw_query_string.encode('utf8'), create_ngram_cmd),
            stderr=open('/dev/null', 'w'),
            shell=True).splitlines()
    return {line.split()[0]: line.split()[1] for line in raw_result}

def process_query(query):
    raw_query_string = query.question + query.narrative + ' '.join(query.concepts)
    query_bigram = create_ngram(raw_query_string)
    return

def create_vector():
    return 

def read_inv_index(inv_idx):
    return

def main():
    # process arguments
    (   
            config['query_file'],
            config['ranked_list'],
            config['model_dir'],
            config['vocab'],
            config['file_list'],
            config['inverted_index'],
            config['ntcir_dir'],
            config['relevance_feedback'],
            config['tool_dir']
            ) = sys.argv[1:]

    # read vocab
    with open(config['vocab']) as vocab_file:
        vocab = {word.strip(): line for line, word in enumerate(vocab_file.readlines())}

    # create vectors
    with open(config['inverted_index']) as inv_idx:
        read_inv_index(inv_idx)

    # parse query file
    tree = ElementTree.parse(config['query_file'])
    root = tree.getroot()
    query_list = [Query(query) for query in root.findall('topic')]
    for query in query_list:
        process_query(query)

    return 0

if __name__ == '__main__':
    exit(main())
