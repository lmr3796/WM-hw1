all: create-vocab create-ngram merge-ngram query-ngram

create-vocab: create-vocab.o ustring.o arg.o
	g++ create-vocab.o ustring.o arg.o -o bin/create-vocab

create-ngram: create-ngram.o ustring.o arg.o merge.o
	g++ create-ngram.o ustring.o arg.o merge.o -o bin/create-ngram

merge-ngram: merge-ngram.o ustring.o arg.o merge.o
	g++ merge-ngram.o ustring.o arg.o merge.o -o bin/merge-ngram

query-ngram: query-ngram.o ustring.o arg.o
	g++ query-ngram.o ustring.o arg.o -o bin/query-ngram

create-vocab.o: create-vocab.cpp
	g++ -c create-vocab.cpp

create-ngram.o: create-ngram.cpp
	g++ -c create-ngram.cpp

merge-ngram.o: merge-ngram.cpp
	g++ -c merge-ngram.cpp

query-ngram.o: query-ngram.cpp
	g++ -c query-ngram.cpp

ustring.o: lib/ustring.cpp
	g++ -c lib/ustring.cpp

arg.o: lib/arg.cpp
	g++ -c lib/arg.cpp

merge.o: lib/merge.cpp
	g++ -c lib/merge.cpp


clean:
	rm -rf *.o bin/*
