#!/bin/bash


RECT='0,0,224,224'
KEY='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

FILE='NPD-links.txt'
TARGET_FILE='NPD-OL-Azure-results.txt'
FAIL_FILE='FAIL.txt'

LOCK_FILES='.k0-0 .k0-1 .k0-2 .k0-3 .k0-4 .k0-5 .k0-6 .k0-7 .k0-8 .k0-9'
LOCK='/var/lock/key-01'
lock(){
    while ! lockfile-create -r 0 -p $LOCK 2> /dev/null;do
        sleep 0.2
    done
}
unlock(){
    lockfile-remove $LOCK;
}

run_cmd2() {
    FFF=$1
    IMG=$2
    echo "$FFF - $IMG"
    sleep $((RANDOM%3+1))
    rm -vf $FFF
}

run_cmd() {
    FFF=$1
    IMG=$2

    RESP=$(curl -s -X POST "https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize?faceRectangles=$RECT" \
                -H "Content-Type: application/json" \
                -H "Ocp-Apim-Subscription-Key: $KEY" \
                --data-ascii "{'url':'$IMG'}")
    [ $? -eq 0 ] && {
        lock
        echo $IMG    >> $TARGET_FILE
        echo "$RESP" >> $TARGET_FILE
        unlock
        
    } || {
        echo $IMG >> $FAIL_FILE
    }
    rm -f $FFF
}

unlock &> /dev/null
rm -f $LOCK_FILES

date >> $TARGET_FILE

CONT=0
while read IMG CLASS;do
    while true;do
        BREAK=0
        for i in $LOCK_FILES;do
            if ! test -f $i;then
                touch $i
                run_cmd $i $IMG &
                BREAK=1
                break
            fi
        done
        if [ $BREAK -eq 1 ]; then
            break
        else
            sleep 0.2
        fi
    done
done < "$FILE"

for i in $LOCK_FILES;do 
    while test -f $i;do sleep 0.2;done
done

date >> $TARGET_FILE
echo
unlock &> /dev/null
rm -f $LOCK_FILES
