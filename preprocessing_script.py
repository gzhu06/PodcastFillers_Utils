import glob, os
import subprocess
import soundfile
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-dataset_path",
    required=True,
    type=str,
    help="folder path contains full-length MP3 podcast episodes",
)
args = parser.parse_args()


def ffmpeg_convert(input_audiofile, output_audiofile, sr):
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
    cmd = [
        "ffmpeg",
        "-i",
        input_audiofile,
        "-ac",
        "1",
        "-af",
        "aresample=resampler=soxr",
        "-ar",
        str(sr),
        output_audiofile,
    ]
    completed_process = subprocess.run(cmd)

    # confrim process completed successfully
    assert completed_process.returncode == 0

    # confirm new file has desired sample rate
    assert soundfile.info(output_audiofile).samplerate == sr


def reformat(ipt_folder, opt_folder, sr=16000):
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
        opt_audiofile = os.path.join(
            folderpath, audiofile.split("/")[-1].split(".mp3")[0] + ".wav"
        )
        ffmpeg_convert(audiofile, opt_audiofile, sr)


def wav_cut(wavfile, start_time, end_time, output_file):
    """
    Cut wav based on filler metainfo, it cuts the original file into
    wav 5s segments which contains filler starts at the third second.

    Args:
            wavfile (str): audio wav filepath
            start_time (float): start time for the filler candidate
            end_time (float): end time for the filler candidate
            output_file (str): output wavfile saving filepath
    """

    cut_cmd = [
        "ffmpeg",
        "-i",
        wavfile,
        "-ss",
        str(start_time),
        "-to",
        str(end_time),
        output_file,
    ]
    subprocess.run(cut_cmd)


def generate_clip_wav(master_csvfile, full_folder, clip_folder):
    """
    generate clips files from full podcast episodes for training
    filler classifier

    Args:
            master_csvfile (str): master csv filepath
            full_folder (str): folder path for full length podcast episode
            clip_folder (str): folder path for event clips
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

        wav_cut(src_filepath, start_time, end_time, tar_filepath)


if __name__ == "__main__":

    dataset_path = args.dataset_path
    master_csvfile = os.path.join(dataset_path, "metadata", "PodcastFillers.csv")
    full_folder = os.path.join(dataset_path, "audio", "episodes_wav")
    clip_folder = os.path.join(dataset_path, "audio", "clips_wav")
    # generate_clip_wav(master_csvfile, full_folder, clip_folder)
