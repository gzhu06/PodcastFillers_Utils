import glob, os
import sed_eval
import argparse
import dcase_util

parser = argparse.ArgumentParser()
parser.add_argument(
    "-sed_eval_path",
    required=True,
    type=str,
    help="folder path contains episode prediction",
)
parser.add_argument(
    "-table", required=True, type=int, help="table index to reproduce, 1 or 2"
)
args = parser.parse_args()


def sed_eval_reproduce(gt_folder, est_folder, t_collar=0.1):
    """
    Args:
            gt_folder (str): folder path for ground truth in sed_eval supported txt files
            est_folder (str): folder path for AVC-FillerNet predicitons with sed_eval supported txt files
            t_collar (float, optional): collar size for sed_eval evalution, in the paper, we use 0.1s
    """

    # prepare fileList dictionary for sed_eval
    filelist_dict = []
    gt_filelist = glob.glob(os.path.join(gt_folder, "*.txt"))
    for gt_file in gt_filelist:

        file_dict = {}

        _, filename = os.path.split(gt_file)
        est_file = os.path.join(est_folder, filename)

        file_dict["reference_file"] = gt_file
        file_dict["estimated_file"] = est_file

        filelist_dict.append(file_dict)

    data = []
    # Get used event labels
    all_data = dcase_util.containers.MetaDataContainer()
    for file_pair in filelist_dict:
        reference_event_list = sed_eval.io.load_event_list(
            filename=file_pair["reference_file"]
        )
        estimated_event_list = sed_eval.io.load_event_list(
            filename=file_pair["estimated_file"]
        )

        data.append(
            {
                "reference_event_list": reference_event_list,
                "estimated_event_list": estimated_event_list,
            }
        )

        all_data += reference_event_list

    event_labels = all_data.unique_event_labels

    # Start evaluating
    # Create metrics classes, define parameters
    segment_based_metrics = sed_eval.sound_event.SegmentBasedMetrics(
        event_label_list=event_labels, time_resolution=0.1
    )
    event_based_metrics = sed_eval.sound_event.EventBasedMetrics(
        event_label_list=event_labels, t_collar=t_collar
    )

    # Go through files
    for file_pair in data:
        segment_based_metrics.evaluate(
            reference_event_list=file_pair["reference_event_list"],
            estimated_event_list=file_pair["estimated_event_list"],
        )

        event_based_metrics.evaluate(
            reference_event_list=file_pair["reference_event_list"],
            estimated_event_list=file_pair["estimated_event_list"],
        )

    print(event_based_metrics)
    print(segment_based_metrics)


if __name__ == "__main__":

    gt_folder = os.path.join(
        args.sed_eval_path, "ground_truth", "Table" + str(args.table)
    )
    est_folder = os.path.join(
        args.sed_eval_path, "AVCFillerNet_predictions", "Table" + str(args.table)
    )
    sed_eval_reproduce(gt_folder, est_folder)
