#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import subprocess
import xml.etree.ElementTree as ElementTree

MAX_NGRAM = 2

config = {}

idf = lambda n: config['doc_cnt_log'] - math.log10(n) 

class InvertedIndex:
    def __init__(self, inv_idx):
        self.lines = inv_idx.readlines()
        self.vocab = {'%s_%s' % (line.split()[0], line.split()[1]): {'range': (line_cnt, line_cnt + int(line.split()[2])),'idf': idf(int(line.split()[2])) }
                for line_cnt, line in enumerate(self.lines) if len(line.split()) == 3 and int(line.split()[2]) > 0}


class Query:
    def __init__(self, topic):
        self.title = topic.find('title').text
        self.number = topic.find('number').text[-3:]
        self.question = topic.find('question').text.strip()
        self.narrative = topic.find('narrative').text.strip()
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()

def create_ngram(raw_query_string, n=MAX_NGRAM, raw=False):
    create_ngram_cmd = '%s/create-ngram -vocab %s -tmp . -n %d' % (config['tool_dir'], config['vocab'], n)
    raw_result = subprocess.check_output('echo \'%s\' | %s' % (raw_query_string.encode('utf8'), create_ngram_cmd),
            stderr=open('/dev/null', 'w'),
            shell=True).splitlines()
    return raw_result if raw else {line.split()[0]: line.split()[1] for line in raw_result}

def similarity(query, doc_id):
    return

def process_query(query, index):
    raw_query_string = query.question + query.narrative + ' '.join(query.concepts)
    query_bigram = create_ngram(raw_query_string)
    return

def create_vector():
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
            config['doc_cnt'],
            config['ntcir_dir'],
            config['relevance_feedback'],
            config['tool_dir']
            ) = sys.argv[1:]
    config['doc_cnt_log'] = math.log10(int(config['doc_cnt'])) # Preculate for speed up

    # read vocab
    with open(config['vocab']) as vocab_file:
        vocab = {word.strip(): line for line, word in enumerate(vocab_file.readlines())}

    # read inverted index
    with open(config['inverted_index']) as inv_idx:
        index = InvertedIndex(inv_idx)

    '''
    # parse query file
    tree = ElementTree.parse(config['query_file'])
    root = tree.getroot()
    query_list = [Query(query) for query in root.findall('topic')]
    for query in query_list:
        process_query(query)
    '''

    return 0

if __name__ == '__main__':
    exit(main())
