#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, subprocess, math
import xml.etree.ElementTree as ElementTree

from collections import defaultdict

MAX_NGRAM = 2
MAX_DOC_RETURN = 10

BASEFILE_NAME = {
        'vocab':    'vocab.all',
        'file_list':'file-list',
        'inv_index':'inverted-index'
        }

config = {}

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
        create_ngram_cmd = '%s/create-ngram -vocab %s -tmp . -n %d' % (config['tool_dir'], config['vocab_file'], n)
        raw_result = subprocess.check_output('echo \'%s\' | %s' % (raw_query_string.encode('utf8'), create_ngram_cmd),
                stderr=open('/dev/null', 'w'),
                shell=True).splitlines()
        return raw_result if raw else dict(map(lambda x: (x.split()[0], int(x.split()[1])), raw_result))

    def __init__(self, query, index):
        raw_query_string = query.question + query.narrative + ' '.join(query.concepts)
        self.vector = QueryVector.create_ngram(raw_query_string)
        return

def process_query(query, index):
    sim = defaultdict(float)
    qv = QueryVector(query, index)
    for bigram, query_bigram_score in qv.vector.iteritems():    # for each bigram
        if not index.vocab.has_key(bigram):
            print >> sys.stderr, 'Bigram "%s" not found in vocabulary' % bigram
            continue
        gram_index = index.vocab[bigram]
        for i in gram_index['range'][1:]:   # for each file with such bigram
            (doc_id, tf) = index.lines[i].split()
            tf = int(tf)
            sim[doc_id] += tf * index.vocab[bigram]['idf'] * query_bigram_score
        
    return map(lambda x: x[0], sorted(sim.iteritems(), key=lambda x: x[1], reverse=True)[:MAX_DOC_RETURN])

def output(query, doc_ids, file_list, f):
    return
    
def main():
    # process arguments
    (config['query_file'],
            config['ranked_list'],
            config['model_dir'],
            config['doc_cnt'],
            config['ntcir_dir'],
            config['relevance_feedback'],
            config['tool_dir']
            ) = sys.argv[1:]
    config['doc_cnt_log'] = math.log10(int(config['doc_cnt'])) # Preculate for speed up
    config['vocab_file'] = config['model_dir'] + '/' +  BASEFILE_NAME['vocab']
    # Read model files
    with open('%s/%s' % (config['model_dir'], BASEFILE_NAME['file_list'])) as f:
        print >> sys.stderr, 'Reading file_list...',
        file_list = map(str.strip, f.readlines())
        print >> sys.stderr, 'done.'

    with open('%s/%s' % (config['model_dir'], BASEFILE_NAME['inv_index'])) as f:
        print >> sys.stderr, 'Processing inverted index, this should take few minutes...',
        index = InvertedIndex(f)
        print >> sys.stderr, 'done.'
    #with open(config['model_dir'] + BASEFILE_NAME['vocab']) as f:
    #    vocab = {word.strip(): line for line, word in enumerate(f.readlines())}

    # parse query file
    tree = ElementTree.parse(config['query_file'])
    root = tree.getroot()
    query_list = [RawQuery(query) for query in root.findall('topic')]
    # ranked
    with open(config['ranked_list'], 'w') as ranked_list:
        for query in query_list:
            doc_ids = process_query(query, index)
            print >> sys.stderr, 'Processing query %s...' % (query.number),
            for doc_id in doc_ids:
                file_name = file_list[int(doc_id)]
                print >> ranked_list, query.number, file_name[file_name.rfind('/')+1:].lower()
            print >> sys.stderr, 'done, %d documents retrieved.' % (len(doc_ids))

    return 0

if __name__ == '__main__':
    exit(main())
