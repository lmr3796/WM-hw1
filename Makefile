rank-30-feedback: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	./execute.sh -r -i data/query-30.xml -o ~/htdocs/$@ -m data -d /tmp2
rank-5-feedback: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	./execute.sh -r -i data/query-5.xml -o ~/htdocs/$@ -m data -d /tmp2
rank-30: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	./execute.sh -i data/query-30.xml -o ~/htdocs/$@ -m data -d /tmp2
rank-5: $(create_ngram) $(merge_ngram) $(query_ngram) $(create_vocab)
	./execute.sh -i data/query-5.xml -o ~/htdocs/$@ -m data -d /tmp2
