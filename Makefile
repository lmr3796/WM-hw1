run30: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	./execute.sh -r -i data/query-30.xml -o ~/htdocs/ranked-list.query-30 -m data -d /tmp2
run5: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	./execute.sh -r -i data/query-5.xml -o ~/htdocs/ranked-list.query-5 -m data -d /tmp2
