#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import xml.etree.ElementTree as ElementTree

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
    for c in query.concepts:
        print subprocess.check_output('echo %s | tool_dir/create-ngram -vocab %s -n %d' %
                [unicode(c).encode('utf8'),''], shell=True),
        return 0
    print '\n'

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

    # parse query file
    tree = ElementTree.parse(Config.query_file)
    root = tree.getroot()
    query_list = [Query(query) for query in root.findall('topic')]
    for query in query_list:
        process_query(query)

    return 0

if __name__ == '__main__':
    exit(main())
