#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, subprocess, math
import xml.etree.ElementTree as ElementTree

from collections import defaultdict

MAX_NGRAM = 2
MAX_DOC_RETURN = 100

BASEFILE_NAME = {
        'vocab':    'vocab.all',
        'file_list':'file-list',
        'inv_index':'inverted-index'
        }

config = {} # Runtime environments
vocab = {}

idf = lambda n: config['doc_cnt_log'] - math.log10(n) 

class InvertedIndex:
    def __init__(self, inv_idx):
        # Load the lines of the inverted index files
        self.lines = inv_idx.readlines()

        # Parse it into the form: bigram => {'range': line number of the bigram
        #                                    'idf': idf of the bigram }
        self.vocab = {'%s_%s' % (line.split()[0], line.split()[1]): {'range': (line_cnt, line_cnt + int(line.split()[2])),'idf': idf(int(line.split()[2])) }
                for line_cnt, line in enumerate(self.lines) if len(line.split()) == 3 and int(line.split()[2]) > 0}
        return

class RawQuery:
    def __init__(self, topic):
        # Extract contents from the element tree
        self.title = topic.find('title').text
        self.number = topic.find('number').text[-3:]
        self.question = topic.find('question').text.strip()
        self.narrative = topic.find('narrative').text.strip()
        self.concepts = topic.find('concepts').text.strip().replace(u'、', '\n').replace(u'。', '\n').split()
        return

def create_ngram(raw_query_string, n=MAX_NGRAM, raw=False):
    # invoke the `create-ngram` to get bigram TF
    CREATE_NGRAM_BIN = 'create-ngram'
    options = '-vocab %s -tmp . -n %d' % (config['vocab_file'], n)
    create_ngram_cmd = '%s/%s %s' % (config['tool_dir'], CREATE_NGRAM_BIN, options)
    raw_result = subprocess.check_output('echo \'%s\' | %s' % (raw_query_string.encode('utf8'), create_ngram_cmd),
            stderr=open('/dev/null', 'w'),
            shell=True).splitlines()
    return raw_result if raw else dict(map(lambda x: (x.split()[0], int(x.split()[1])), raw_result))

def convert_query_to_vector(query):
    print >> sys.stderr, 'Converting query %s to vector form...' %(query.number),
    vector = defaultdict(float)
    for bigram, tf in create_ngram(query.question).iteritems():
        vector[bigram] += tf
    for bigram, tf in create_ngram(query.narrative).iteritems():
        vector[bigram] += tf
    for c in query.concepts:
        for bigram, tf in create_ngram(c).iteritems():
            vector[bigram] += tf
    print >> sys.stderr, 'done.'
    return vector

def convert_bigram_to_str(bigram):
    (a,b) = bigram.split('_')
    return '%s%s' % (vocab['line'][int(a)], vocab['line'][int(b)])

def process_query(query, index):
    sim = defaultdict(float)    # similarity to each document
    qv = convert_query_to_vector(query)
    for bigram, query_bigram_score in qv.iteritems():    # for each bigram in the query
        if not index.vocab.has_key(bigram):
            # ignore the bigram if not found
            print >> sys.stderr, 'Bigram %s("%s") not found in vocabulary' % (bigram, convert_bigram_to_str(bigram))
            continue
        for i in range(index.vocab[bigram]['range'][0]+1, index.vocab[bigram]['range'][1]):   # for each file with such bigram
            (doc_id, tf) = index.lines[i].split()
            tf = int(tf)
            sim[doc_id] += tf * index.vocab[bigram]['idf'] * query_bigram_score # Sum up as dot product

    return map(lambda x: x[0], sorted(sim.iteritems(), key=lambda x: x[1], reverse=True)[:MAX_DOC_RETURN])

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

    with open('%s/%s' % (config['model_dir'], BASEFILE_NAME['vocab'])) as f:
        vocab['line'] = map(str.strip, f.readlines())
        vocab['bigram'] = {word.strip(): line for line, word in enumerate(vocab['line'])}

    # parse query file
    tree = ElementTree.parse(config['query_file'])
    root = tree.getroot()
    query_list = [RawQuery(query) for query in root.findall('topic')]

    # process queries and output to ranked_list
    with open(config['ranked_list'], 'w') as ranked_list:
        for query in query_list:
            print >> sys.stderr, 'Processing query %s...' % (query.number)
            doc_ids = process_query(query, index)
            for doc_id in doc_ids:
                file_name = file_list[int(doc_id)]
                print >> ranked_list, query.number, file_name[file_name.rfind('/')+1:].lower()
            print >> sys.stderr, 'Query %s done, %d documents retrieved.' % (query.number, len(doc_ids))

    return 0

if __name__ == '__main__':
    exit(main())
