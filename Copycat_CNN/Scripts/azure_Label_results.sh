#!/usr/bin/env python2

#KDEF e CK
#0=neutral
#1=anger
#X=contempt
#2=disgust
#3=fear
#4=happy
#5=sadness
#6=surprise

#Azure:
#anger     <- 1
#contempt  <- 7
#disgust   <- 2
#fear      <- 3
#happiness <- 4
#neutral   <- 0
#sadness   <- 5
#surprise  <- 6


from sys import argv, exit, stderr

if len(argv) < 2:
    print('Use: {} azure-results.txt'.format(argv[0]))
    exit(1)

import ast

azure = {'anger':1,'contempt':7,'disgust':2,'fear':3,'happiness':4,'neutral':0,'sadness':5,'surprise':6}

contents = open(argv[1]).readlines()
for i in range(0,len(contents),2):
    image  = contents[i].replace('\n','')
    resp   = ast.literal_eval( contents[i+1] )
    scores = resp[0]['scores']
    score  = max( scores, key=scores.get )
    image_azure_class = azure[score]
    print("{} {} - {}".format(image, score, image_azure_class))

