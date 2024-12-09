#!/bin/sh
MIN="$1"
MAX="$2"
for i in $(seq $MIN $MAX)
do
    start=$(($(date +%s%N)/1000000))
    python word_design.py --solver glucose-syrup "$i" > /dev/null
    sc=$?
    end=$(($(date +%s%N)/1000000))
    echo "$i $((end - start)) $sc"
done
