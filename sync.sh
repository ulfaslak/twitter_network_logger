#!/bin/bash
cd data
git add likes.csv retweets.csv mentions.csv
git commit -m "autocommit"
git push origin master;
