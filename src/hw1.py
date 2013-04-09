#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
import xml.etree.ElementTree as ElementTree

class Config:
    query_file = None
    ranked_list = None
    model_dir = None
    vocab = None
    file_list = None
    inverted_index = None
    ntcir_dir = None
class Query:
    def __init__(self, topic):
        self.title = topic.find('title').text
        self.number = topic.find('number').text[-3:]
        self.question = topic.find('question').text
        self.narrative = topic.find('narrative').text
        self.concepts = topic.find('concepts').text.strip().replace(u'、', ' ').replace(u'。', ' ').split()

def process_query(query):
    for c in query.concepts:
        print subprocess.check_output('echo %s | create-ngram -vocab %s -n %d' %
                [unicode(c).encode('utf8'),''], shell=True),
        return 0
    print '\n'

    return

def main():
    # process arguments
    (   
        Config.query_file,
        Config.ranked_list,
        Config.model_dir,
        Config.vocab,
        Config.file_list,
        Config.inverted_index,
        Config.ntcir_dir
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
