run: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	#./execute.sh -r -i data/query-5.xml -o ranked-list -m data -d /tmp2
	./execute.sh -r -i data/query-30.xml -o ~/htdocs/ranked-list -m data -d /tmp2
