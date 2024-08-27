#!/usr/bin/env bash

#
# This script installs IOCBio sparks program to python virtual environment iocbio-sparks
#

set -e
RNAME=iocbio-sparks_requirements.txt
python3 -m venv iocbio-sparks
if command -v wget &> /dev/null
then
  wget -q -O $RNAME https://gitlab.com/iocbio/sparks/-/raw/master/requirements.txt
else
  curl https://gitlab.com/iocbio/sparks/-/raw/master/requirements.txt --output $RNAME
fi
iocbio-sparks/bin/pip3 install -r $RNAME
rm $RNAME
# iocbio-sparks/bin/pip3 install git+https://gitlab.com/iocbio/sparks
iocbio-sparks/bin/pip3 install iocbio.sparks

echo Start the program by running iocbio-sparks/bin/iocbio-sparks
