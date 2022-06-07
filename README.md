# PodcastFillers_Utils

## Introduction
Utility functions for preprocessing PodcastFillers dataset and code for reproducing Table1 and Table2 in the [FillerNet paper](https://arxiv.org/abs/2203.15135) with AVC-FillerNet sed_eval predictions. 

Dataset homepage: [PodcastFillers.github.io](PodcastFillers.github.io)\
Dataset zenodo page: [placeholder](zenodo.com)

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

We prepare two customized parameters to preprocessing event clips:
- `SAMPLE_RATE` : Sampling rate for the converted WAV files, default value is 16kHz;
- `DURATION`: Length of the event clips(unit: second), the filler/non-filler event will also be centered in the clip, the default value is 1.0 and it is larger than zero. 

`reformat` and `generate_clip_wav` passed [pytest](https://docs.pytest.org/en/7.1.x/index.html) using `pytest -q test.py`.

### Results reproduction
To reproduce the AVCFIllerNet results from Table.1 and Table.2 from our [paper](https://arxiv.org/abs/2203.15135), run
```
python reproduce_results.py -dataset_path {dataset_path}
```
