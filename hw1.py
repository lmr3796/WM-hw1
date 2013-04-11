#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import math
import subprocess
import xml.etree.ElementTree as ElementTree

MAX_NGRAM = 2
MAX_DOC = 10

config = {}

output_file = sys.stdout
idf = lambda n: config['doc_cnt_log'] - math.log10(n) 

class InvertedIndex:
    def __init__(self, inv_idx):
        self.lines = inv_idx.readlines()
        self.vocab = {'%s_%s' % (line.split()[0], line.split()[1]): {'range': (line_cnt, line_cnt + int(line.split()[2])),'idf': idf(int(line.split()[2])) }
                for line_cnt, line in enumerate(self.lines) if len(line.split()) == 3 and int(line.split()[2]) > 0}
        return

class RawQuery:
    def __init__(self, topic):
        self.title = topic.find('title').text
        self.number = topic.find('number').text[-3:]
        self.question = topic.find('question').text.strip()
        self.narrative = topic.find('narrative').text.strip()
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()
        return

class QueryVector:
    @staticmethod
    def create_ngram(raw_query_string, n=MAX_NGRAM, raw=False):
        create_ngram_cmd = '%s/create-ngram -vocab %s -tmp . -n %d' % (config['tool_dir'], config['vocab'], n)
        raw_result = subprocess.check_output('echo \'%s\' | %s' % (raw_query_string.encode('utf8'), create_ngram_cmd),
                stderr=open('/dev/null', 'w'),
                shell=True).splitlines()
        return raw_result if raw else dict(map(str.split, raw_result))

    def __init__(self, query, index):
        raw_query_string = query.question + query.narrative + ' '.join(query.concepts)
        self.vector = QueryVector.create_ngram(raw_query_string)
        return

def process_query(query, index):
    sim = {}
    qv = QueryVector(query, index)
    for bigram, query_bigram_score in qv.vector.iteritems():    # for each bigram
        gram_index = index.vocab[bigram]
        for i in gram_index['range'][1:]:   # for each file with such bigram
            try:
                (doc_id, tf) = index.lines[i].split()
            except ValueError:
                print i, index.lines[i]
                print gram_index['range']
                raise
            if not sim.has_key(doc_id):
                sim[doc_id] = 0.0
            else:
                # XXX: bigram has to be converted to tf
                sim[doc_id] += tf * idf(bigram) * query_bigram_score
        
    return map(lambda x: x[0], sorted(sim.iteritems(), key=lambda x: x[1])[:MAX_DOC])
    
def main():
    # process arguments
    (config['query_file'],
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
    output_file = open(config['file_list'])

    # read vocab
    with open(config['vocab']) as vocab_file:
        vocab = {word.strip(): line for line, word in enumerate(vocab_file.readlines())}

    # read inverted index
    with open(config['inverted_index']) as inv_idx:
        index = InvertedIndex(inv_idx)

    # parse query file
    tree = ElementTree.parse(config['query_file'])
    root = tree.getroot()
    query_list = [RawQuery(query) for query in root.findall('topic')]
    for query in query_list:
        print process_query(query, index)
        return 0

    return 0

if __name__ == '__main__':
    exit(main())
