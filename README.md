# PodcastFillers_Utils

## Introduction
Utility functions for preprocessing PodcastFillers dataset and code for reproducing Table1 and Table2 in the [FillerNet paper](https://arxiv.org/abs/2203.15135) with AVC-FillerNet sed_eval predictions.

## Requirements
tqdm==4.61.2\
sed_eval==0.2.1\
dcase_util==0.2.18\
pandas==1.1.5

## Usage

### Preprocessing
In preprocessing script, we first convert full-length MP3 podcast episodes into WAVs, then we cut 1-second event clips based on the meta csv with converted WAVs. Format conversion:
```
python preprocessing_script.py -dataset_path {dataset_path} -stage reformat
```

Event clip WAV cut:
```
python preprocessing_script.py -dataset_path {dataset_path} -stage cut
```

For customized converted sampling rate or change event clip length keep event centered in the clip, revise parameters `SAMPLE_RATE` and `DURATION_OFFSET` in the code.

### Results reproduction
To reproduce the AVCFIllerNet results from Table.1 and Table.2 from our [paper](https://arxiv.org/abs/2203.15135), run
```
python reproduce_results.py -dataset_path {dataset_path}
```

