#!/bin/bash

UCF_IMAGES='UCF-101'
UCF_ANNOTATION='ucfTrainTestlist'

echo 'Splitting videos...'
mkdir -p train
for i in $(awk '{print $1}' $UCF_ANNOTATION/trainlist01.txt);do
	ln -vs $UCF_IMAGES/${i%.avi} train/${i%.avi}
done

mkdir -p test
for i in $(awk '{print $1}' $UCF_ANNOTATION/testlist01.txt);do
	ln -vs $UCF_IMAGES/${i%.avi} test/${i%.avi}
done

echo 'Creating indexes...'
find train -type l -exec find {}/ -type f \; > train.txt
find test  -type l -exec find {}/ -type f \; > test.txt

echo 'Creating labels...'
./apply_pattern.py $UCF_ANNOTATION/classInd.txt train.txt > .train.txt
mv .train.txt train.txt
./apply_pattern.py $UCF_ANNOTATION/classInd.txt test.txt  > .test.txt
mv .test.txt test.txt

echo 'Done.'
echo 'The files "train.txt" and "test.txt" have the annotations for ODD and TDD.'
