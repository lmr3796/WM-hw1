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

class RawQuery:
    def __init__(self, topic):
        # Extract contents from the element tree
        self.title = topic.find('title').text
        self.number = topic.find('number').text[-3:]
        self.question = topic.find('question').text.strip()
        self.narrative = topic.find('narrative').text.strip()
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()
        return

class InvertedIndex:
    def __init__(self, inv_idx):
        # Load the lines of the inverted index files
        self.lines = []
        self.bigram = {}
        self.doc = defaultdict(dict)
        for line_number, line in enumerate(inv_idx.readlines()):
            self.lines.append(line)
            token = line.split()
            # index for each bigram
            if len(token) == 3:
                if int(token[2]) <= 0:
                    continue
                bigram = '%s_%s' % (token[0], token[1])
                bigram_idf = idf(int(token[2]))
                self.bigram[bigram] = {'range': (line_number, line_number + int(token[2])), 'idf': bigram_idf, 'score_in_doc':{}}
            else:
                (doc_id, tf) = line.split()
                tf = int(tf)
                self.doc[doc_id][bigram] = tf * self.bigram[bigram]['idf']
                self.bigram[bigram]['score_in_doc'][doc_id] = tf * self.bigram[bigram]['idf']

        # Caculate document length
        self.doc_len = {doc_id: reduce(lambda x, y: x + y ** 2, self.doc[doc_id].values()) ** 0.5 for doc_id in self.doc}

        return

def convert_bigram_to_str(bigram):
    (a,b) = bigram.split('_')
    return '%s%s' % (vocab['line'][int(a)], vocab['line'][int(b)])

def create_ngram(raw_query_string, index, n=MAX_NGRAM, raw=False):
    # invoke the `create-ngram` to get bigram TF
    create_ngram_cmd = '%s/create-ngram -vocab %s -tmp . -n %d' % (config['tool_dir'], config['vocab_file'], n)
    raw_result = subprocess.check_output('echo \'%s\' | %s' % (raw_query_string.encode('utf8'), create_ngram_cmd),
            stderr=open('/dev/null', 'w'),
            shell=True).splitlines()
    return raw_result if raw else dict(map(lambda x: (x.split()[0], int(x.split()[1]) * idf(int(x.split()[1])) ), raw_result))

def convert_bigram_to_str(bigram):
    (a,b) = bigram.split('_')
    return '%s%s' % (vocab['line'][int(a)], vocab['line'][int(b)])

def rocchio_feedback(qv, dr, index):
    qm = defaultdict(float)
    # linear combination
    for bigram, score in qv.iteritems():
        qm[bigram] += config['alpha'] * score
    for doc_id in dr:
        for bigram, score in index.doc[doc_id].iteritems():
            qm[bigram] += config['beta'] * score / len(dr)
    return process_query_vector(qm, index, False)

def process_query_vector(qv, index, feedback, cos=True):
    doc_square_len = defaultdict(float) # square length of each document
    sim = defaultdict(float)    # similarity of each document
    for bigram, query_bigram_score in qv.iteritems():    # for each bigram in the query
        if not index.bigram.has_key(bigram):
            # ignore the bigram if not found
            print >> sys.stderr, 'Bigram %s("%s") not found in vocabulary' % (bigram, convert_bigram_to_str(bigram))
            continue
        for doc_id, doc_bigram_score in index.bigram[bigram]['score_in_doc'].iteritems():
            sim[doc_id] += query_bigram_score * doc_bigram_score

    # cosine normalization
    if cos:
        sim = dict(map(lambda x: (x[0], x[1] / index.doc_len[x[0]]), sim.iteritems()))   # We don't need query vector length, it doesn't influence the order

    best_doc = map(lambda x: x[0], sorted(sim.iteritems(), key=lambda x: x[1], reverse=True)[:MAX_DOC_RETURN])
    
    if feedback:
        best_doc = rocchio_feedback(qv, best_doc[:config['dr']], index)

    return best_doc

def process_query(query, index, feedback=False, cos=True):
    raw_query_string = query.question + query.narrative + ' '.join(query.concepts)
    qv = create_ngram(raw_query_string, index)
    return process_query_vector(qv, index, feedback, cos)
    

def main():
    # process arguments
    (config['query_file'],
            config['ranked_list'],
            config['tool_dir'],
            config['model_dir'],
            config['doc_cnt'],
            config['ntcir_dir'],
            config['feedback'],
            config['dr'],
            config['alpha'],
            config['beta'],
            ) = sys.argv[1:]
    config['doc_cnt_log'] = math.log10(int(config['doc_cnt'])) # Preculate for speed up
    config['vocab_file'] = config['model_dir'] + '/' +  BASEFILE_NAME['vocab']
    config['feedback'] = config['feedback'] == 'true'
    config['dr'] = int(config['dr'])
    config['alpha'] = float(config['alpha'])
    config['beta'] = float(config['beta'])

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
            doc_ids = process_query(query, index, feedback=config['feedback'])
            for doc_id in doc_ids:
                file_name = file_list[int(doc_id)]
                print >> ranked_list, query.number, file_name[file_name.rfind('/')+1:].lower()
            print >> sys.stderr, 'Query %s done, %d documents retrieved.' % (query.number, len(doc_ids))

    return 0

if __name__ == '__main__':
    exit(main())
