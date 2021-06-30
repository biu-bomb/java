#!/bin/bash

while ((1))
do
    git push
    let r=$?
    if [[ $r == 0 ]];
    then
        break
    fi
done
