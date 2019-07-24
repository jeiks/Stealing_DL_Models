#!/bin/bash

echo 'Be careful!! this script will remove TT100K TSRD OD* TD* PD*'

read -p 'are you sure (Y/[N])? ' RESP

case "${RESP^^}"
    in Y*)
        rm -rf TT100K TSRD OD* TD* PD*
        ;;
esac
