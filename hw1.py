#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import xml.etree.ElementTree as ElementTree

N_GRAM_CNT=2

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
        self.question = topic.find('question').text
        self.narrative = topic.find('narrative').text
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()

def process_query(query):
    create_ngram_cmd = '%s/create-ngram -vocab %s -n %d' % (config['tool_dir'], config['vocab'], N_GRAM_CNT)
    raw_query_string = query.narrative #' '.join(query.concepts).encode('utf8')
    print subprocess.check_output('echo \'%s\' | %s' % (raw_query_string, create_ngram_cmd), shell=True)
    print '\n'
    return 0

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
