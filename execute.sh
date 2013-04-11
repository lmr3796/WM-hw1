#! /usr/bin/env bash

tool_dir=tools/bin
file_list=data/file-list
relevance_feedback=false

# Parse command line arguments
if [ "$1" == "-r" ]; then
    relevance_feedback=true
    shift
fi
para=($@)
for ((i=0; i<$#; i=i+2))
do
    case ${para[$i]} in
        "-i")
            query_file=${para[$((i+1))]}
            ;;
        "-o")
            ranked_list=${para[$((i+1))]}
            ;;
        "-m")
            model_dir=${para[$((i+1))]}
            vocab=$model_dir/vocab.all
            file_list=$model_dir/file-list
            inverted_index=$model_dir/inverted-index
            ;;
        "-d")
            ntcir_dir=${para[$((i+1))]}
            ;;
        *)
            echo "Parameter error: ${para[$i]}" >&2
            exit
            ;;

    esac
done

# Generate index of the inverted index file
if [ ! -f `basename $inverted_index`.vocindex ]; then
    echo -n 'Generating inverted index cache...'
    awk 'NF == 3{print NR " " $0}' $inverted_index > `basename $inverted_index`.vocindex
    echo 'done'
fi
doc_cnt=`wc -l $file_list | awk '{print $1}'`

# Run
./hw1.py $query_file $ranked_list $model_dir $vocab $file_list $inverted_index $doc_cnt $ntcir_dir $relevance_feedback $tool_dir




