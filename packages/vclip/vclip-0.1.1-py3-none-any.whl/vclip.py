import argparse # for command line interface
from datetime import datetime # for default output file name
import os # for file manipulation 
import random # for selecting random files
import logging # for logging in case of errors
from moviepy.editor import VideoFileClip, concatenate_videoclips # for extracting and concatenating clips

# enable basic logging

def setup_logging(verbose):
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.disable(logging.CRITICAL)

def video_clipper(folder_path, output_file, num_clips, clip_duration):
    # list of video file extensions to look for

    supported_extensions = (".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv")

    # get a list of video files in the specified folder
    video_files = [file for file in os.listdir(folder_path) if file.lower().endswith(supported_extensions)]

    # create empty list to store video clips
    video_clips = []

    # show error if there are no video files in the specified folder
    if not video_files:
        print(f"error: no video files found in the specified folder: " + folder_path)
        return

    # check if specified number of clips exceeds videos in specified folder
    if num_clips > len(video_files):
        print(f"error: requested {num_clips} clips, but only {len(video_files)} available in specified folder: " + folder_path)
        return

    # use random.sample to select specified number of clips from video files in folder
    selected_videos = random.sample(video_files, num_clips)
    
    # select random clips from videos in folder and append to list
    for random_video in selected_videos:
        random_video_path = os.path.join(folder_path, random_video)

        try:
            video_clip = VideoFileClip(random_video_path)

            # check if specified clip duration is longer than duration of video
            if video_clip.duration <= clip_duration:
                logging.warning(f"clip duration {clip_duration}s exceeds video duration {video_clip.duration}s. using full video.")
                start_time = 0
            else:
                start_time = random.uniform(0, video_clip.duration - clip_duration)
                
            # ensure end time does not exceed video duration
            end_time = min(start_time + clip_duration, video_clip.duration)
            print(f"processing clip from {start_time}s to {end_time}s in {random_video}")
            selected_clip = video_clip.subclip(start_time, end_time)
            video_clips.append(selected_clip)

            logging.info(f"added clip from {random_video} starting at {start_time:.2f}s.")

        except Exception as e:
            logging.error(f"failed to process {random_video}: {str(e)}")

    if video_clips:
        # concatenate clips into a new video
        final_clip = concatenate_videoclips(video_clips, method="compose")

        # write video to output file with specified codec parameters
        final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)
        logging.info(f"video saved to {output_file}")
    else:
        logging.error("no clips were processed successfully.")

    
    print("clipped " + str(len(selected_videos)) + " videos randomly selected from folder of " + str(len(video_files)) + " video files.")

def main():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S.mp4")
    current_path = os.getcwd()
    parser = argparse.ArgumentParser(description="a small tool to compile randomly selected video clips from a folder of videos.")
    parser.add_argument("-i", "--input", default=current_path, help="path to input folder with videos to be clipped (default: current path)")
    parser.add_argument("-o", "--output", default=timestamp, help="name of output file name for final clipped videos (default: timestamped file in format [year month day hour second] for when script is run - e.g. 20240818085410.mp4)")
    parser.add_argument("-n", "--number", type=int, default=10, help="number of clips to include (default: 10 clips)")
    parser.add_argument("-d", "--duration", type=int, default=1, help="duration of each clip in seconds (default: 1 second)")
    parser.add_argument("--verbose", "-v", action="store_true", help="enable verbose output (logging)")
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    logging.info("starting to clip videos - - - ✂ - - -")
    
    video_clipper(args.input, args.output, args.number, args.duration)

if __name__ == "__main__":
    main()