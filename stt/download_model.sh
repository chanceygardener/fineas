#!/bin/sh

DEEPSPEECH_VERSION="0.9.3"

RETURN_DIR=$PWD

cd $(dirname "$0");

# create models directory
if [[ ! -d ./models ]]; then
    mkdir models

fi
if [[ ! -d ./models/$DEEPSPEECH_VERSION ]]; then
    mkdir ./models/$DEEPSPEECH_VERSION
fi

cd ./models/$DEEPSPEECH_VERSION

model_file=deepspeech-${DEEPSPEECH_VERSION}-models.pbmm
scorer_file=deepspeech-${DEEPSPEECH_VERSION}-models.scorer

if ls $model_file 1>/dev/null 2>&1; then
    echo 'Model file found, skipping download'
else
    echo 'Model file not found, downloading'
    curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v${DEEPSPEECH_VERSION}/deepspeech-${DEEPSPEECH_VERSION}-models.pbmm
fi

if ls $scorer_file 1>/dev/null 2>&1; then
    echo 'Scorer file found, skipping download'
else
    echo 'Scorer file not found, downloading'
    curl -LO https://github.com/mozilla/DeepSpeech/releases/download/v${DEEPSPEECH_VERSION}/deepspeech-${DEEPSPEECH_VERSION}-models.scorer
fi

cd $RETURN_DIR;
