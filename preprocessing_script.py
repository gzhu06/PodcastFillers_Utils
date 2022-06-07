import glob, os
from tqdm import tqdm
import subprocess
import soundfile
import librosa
import pandas as pd
import argparse

SAMPLE_RATE = 16000
DURATION = 1.0

def ffmpeg_convert(input_audiofile, output_audiofile, sr=SAMPLE_RATE):
    """
    Convert an audio file to a resampled audio file with the desired
    sampling rate specified by `sr`.
    Parameters
    ----------
    input_audiofile : string
            Path to the video or audio file to be resampled.
    output_audiofile
            Path for saving the resampled audio file. Should have .wav extension.
    sr : int
            The sampling rate to use for resampling (e.g. 16000, 44100, 48000).
    Returns
    -------
    completed_process : subprocess.CompletedProcess
            A process completion object. If completed_process.returncode is 0 it
            means the process completed successfully. 1 means it failed.
    """

    # fmpeg command
    cmd = ["ffmpeg", "-i", input_audiofile, "-ac", "1", "-af", "aresample=resampler=soxr", "-ar", str(sr), "-y", output_audiofile]
    completed_process = subprocess.run(cmd)

    # confrim process completed successfully
    assert completed_process.returncode == 0

    # confirm new file has desired sample rate
    assert soundfile.info(output_audiofile).samplerate == sr


def reformat(ipt_folder, opt_folder, sr=SAMPLE_RATE):
    """
    convert full-length MP3 files into wav files.

    Parameters
    ----------
    ipt_folder : str
            folder path for full-length podcast episodes in the original MP3 format
    opt_folder : str
            folder path for saving full-length podcast episodes in converted WAV format
    sr : int, optional
            The target sampling rate to use for resampling
    """
    audiofiles = glob.glob(os.path.join(ipt_folder, "**/*.mp3"), recursive=True)

    for audiofile in tqdm(audiofiles):

        folderpath = os.path.join(opt_folder, audiofile.split("/")[-2])
        os.makedirs(folderpath, exist_ok=True)
        opt_audiofile = os.path.join(folderpath, audiofile.split("/")[-1].split(".mp3")[0] + ".wav")
        ffmpeg_convert(audiofile, opt_audiofile, sr)


def generate_clip_wav(master_csvfile, full_folder, clip_folder, duration=DURATION):
    """
    generate clips files from full podcast episodes for training
    filler classifier

    Args:
            master_csvfile (str): master csv filepath
            full_folder (str): folder path for full length podcast episode in converted wav format
            clip_folder (str): folder path for event wav clips 
            duration_offset (float): amount of time to increase or decrease over the original one second clip
    """

    event_df = pd.read_csv(master_csvfile)
    for i, event in event_df.iterrows():

        episode_subset = event["episode_split_subset"]
        clip_subset = event["clip_split_subset"]

        tar_folder = os.path.join(clip_folder, clip_subset)
        os.makedirs(tar_folder, exist_ok=True)

        src_filepath = os.path.join(
            full_folder, episode_subset, event["podcast_filename"] + ".wav"
        )
        start_time = event["clip_start_inepisode"]
        end_time = event["clip_end_inepisode"]
        tar_filepath = os.path.join(tar_folder, event["clip_name"])

        if os.path.exists(tar_filepath):
            continue

        # cut wav into clips based on filler metainfo
        duration_offset = (duration - 1.0)/2.0
        cut_cmd = ["ffmpeg", "-i", src_filepath, "-ss", str(start_time-duration_offset), "-to", str(end_time+duration_offset), tar_filepath]
        completed_process = subprocess.run(cut_cmd)

        actual_duration = librosa.get_duration(filename=tar_filepath)
        assert actual_duration == duration

        # confrim process completed successfully
        assert completed_process.returncode == 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-dataset_path", required=True, type=str, help="root path for PodcastFillers dataset")
    parser.add_argument("-stage", required=True, type=str, choices=["reformat", "cut"], help="preprocessing step for extracting wav clips")
    args = parser.parse_args()

    dataset_path = args.dataset_path
    master_csvfile = os.path.join(dataset_path, "metadata", "PodcastFillers.csv")
    full_mp3_folder = os.path.join(dataset_path, "audio", "episode_mp3")
    full_wav_folder = os.path.join(dataset_path, "audio", "episode_wav_regenerate")
    clip_folder = os.path.join(dataset_path, "audio", "clip_wav_regenerate")

    # convert full-length MP3 into WAV
    if args.stage == "reformat":
        reformat(full_mp3_folder, full_wav_folder, sr=SAMPLE_RATE)

    # generate clip wavs from full length WAV
    elif args.stage == "cut":
        # it's required to run "reformat" stage first
        generate_clip_wav(master_csvfile, full_wav_folder, clip_folder, duration=DURATION)

    else:
        print("Unknown operation!")
