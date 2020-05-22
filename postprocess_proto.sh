#!/bin/bash

in_filename=$1
out_filename=$2

echo "# type: ignore" > $out_filename
cat $in_filename >> $out_filename
sed --in-place= 's/^\(import.*pb2\)/from . \1/' $out_filename
