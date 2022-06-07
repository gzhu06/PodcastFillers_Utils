import numpy as np
from preprocessing_script import reformat, generate_clip_wav
import tempfile, glob, os
import soundfile
from tqdm import tqdm

TEST_SPLIT = 'validation'

# regression test for reformat using validation files
SR = 16000
DATA_ROOTPATH = '/Users/gzhu/Documents/datasets/Filler/sc_podcast/formal_release'
EPI_MP3_PATH = os.path.join(DATA_ROOTPATH, 'audio', 'episode_mp3', TEST_SPLIT)
EPI_REG_PATH = os.path.join(DATA_ROOTPATH, 'audio', 'episode_wav', TEST_SPLIT)

# regression test for generate_clip_wav using validation files
DURATION = 1.0
CSV_NAME = 'LMScast_315 How to Create Profitable Online Courses and Membership Sites Even After Failures Along the Way.csv'
CSV_REG_PATH = os.path.join(DATA_ROOTPATH, 'metadata', 'episode_annotations', TEST_SPLIT, CSV_NAME)
CLIP_REG_PATH = os.path.join(DATA_ROOTPATH, 'audio', 'clip_wav', TEST_SPLIT)

def test_episode_conversion(test_mp3_path=EPI_MP3_PATH, reg_wav_path=EPI_REG_PATH, sr=SR, atol=1e-4, rtol=1e-8):
    # Convert MP3 files into temp folder and check
    
    with tempfile.TemporaryDirectory() as tmpdirname:

        reformat(test_mp3_path, tmpdirname, sr=SR)
        test_wav_paths = glob.glob(os.path.join(tmpdirname, TEST_SPLIT, '*.wav'), recursive=True)

        print('Testing converted WAV files')
        for test_wav_path in tqdm(test_wav_paths):

            test_wav_filename = test_wav_path.split('/')[-1]

            # validate audio
            wav, sr = soundfile.read(test_wav_path, always_2d=True)
            regwav, sr = soundfile.read(os.path.join(reg_wav_path, test_wav_filename), always_2d=True)
        
            assert np.allclose(wav, regwav, atol=atol, rtol=rtol)
            assert np.allclose(sr, SR, atol=atol, rtol=rtol)

def test_event_clip(csvfile=CSV_REG_PATH, epi_folder=os.path.join(DATA_ROOTPATH,  'audio', 'episode_wav'), 
                    clip_reg_folder=CLIP_REG_PATH, duration=DURATION, sr=SR, atol=1e-4, rtol=1e-8):
    # Cut clip WAV files from episode WAV files into temp folder and check

    with tempfile.TemporaryDirectory() as tmpdirname:

        generate_clip_wav(csvfile, epi_folder, tmpdirname, duration)
        test_clip_paths = glob.glob(os.path.join(tmpdirname, TEST_SPLIT, '*.wav'), recursive=True)

        print('Testing event clips')
        for test_wav_path in tqdm(test_clip_paths):

            test_wav_filename = test_wav_path.split('/')[-1]

            # validate audio
            wav, sr = soundfile.read(test_wav_path, always_2d=True)
            regwav, sr = soundfile.read(os.path.join(clip_reg_folder, test_wav_filename), always_2d=True)
        
            assert np.allclose(wav, regwav, atol=atol, rtol=rtol)
            assert np.allclose(sr, SR, atol=atol, rtol=rtol)
