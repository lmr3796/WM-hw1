for f in `ls /irlab/wm2008/hw1/testing/enwiki/`; do
	echo $f;
	bin/create-ngram -vocab data/vocab.enwiki -n 2 -o data/bigram.$f /irlab/wm2008/hw1/testing/enwiki/$f;
done

bin/merge-ngram -o data/bigram.enwiki data/bigram.*
