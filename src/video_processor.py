import os
import random
import logging
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop, resize
from utils.config_loader import load_config

logger = logging.getLogger(__name__)

# Load configuration
config = load_config("config/main_config.toml")


def select_background_video(audio_duration):
    """
    Select a random background video, trim it to match the audio duration,
    and crop it to the target resolution with cover object fit.

    :param audio_duration: Duration of the audio in seconds
    :return: Path to the processed video file
    """
    try:
        background_folder = config["video"]["background_folder"]
        output_folder = config["output"]["folder"]
        target_width = config["video"]["target_width"]
        target_height = config["video"]["target_height"]

        logger.info(f"Searching for video files in: {background_folder}")

        if not os.path.exists(background_folder):
            raise FileNotFoundError(
                f"Background folder does not exist: {background_folder}"
            )

        video_files = [
            f
            for f in os.listdir(background_folder)
            if f.endswith((".mp4", ".avi", ".mov", ".webm"))
        ]

        logger.info(f"Found {len(video_files)} video files: {video_files}")

        if not video_files:
            raise FileNotFoundError(
                f"No video files found in the background folder: {background_folder}"
            )

        selected_video = random.choice(video_files)
        video_path = os.path.join(background_folder, selected_video)

        logger.info(f"Selected background video: {selected_video}")

        with VideoFileClip(video_path) as video:
            logger.info(
                f"Video duration: {video.duration}, Audio duration: {audio_duration}"
            )

            if video.duration < audio_duration:
                logger.info("Video shorter than audio, looping video")
                video = video.loop(duration=audio_duration)

            start_time = 0
            if video.duration > audio_duration:
                max_start = video.duration - audio_duration
                start_time = random.uniform(0, max_start)

            logger.info(
                f"Trimming video from {start_time} to {start_time + audio_duration}"
            )

            # Trim the video
            trimmed_video = video.subclip(start_time, start_time + audio_duration)

            # Crop the video with cover object fit
            original_aspect_ratio = trimmed_video.w / trimmed_video.h
            target_aspect_ratio = target_width / target_height

            if original_aspect_ratio > target_aspect_ratio:
                # Video is wider, crop the sides
                new_width = int(trimmed_video.h * target_aspect_ratio)
                x1 = (trimmed_video.w - new_width) // 2
                y1 = 0
                x2 = x1 + new_width
                y2 = trimmed_video.h
            else:
                # Video is taller, crop the top and bottom
                new_height = int(trimmed_video.w / target_aspect_ratio)
                x1 = 0
                y1 = (trimmed_video.h - new_height) // 2
                x2 = trimmed_video.w
                y2 = y1 + new_height

            cropped_video = crop(trimmed_video, x1=x1, y1=y1, x2=x2, y2=y2)

            # Resize to target resolution using the resize video fx
            final_video = resize(cropped_video, newsize=(target_width, target_height))

            # Set the audio to None to remove any existing audio
            final_video = final_video.set_audio(None)

            # Save the processed video
            output_path = os.path.join(output_folder, "processed_background.mp4")
            logger.info(f"Saving processed video to: {output_path}")

            # Try encoding methods in order of preference
            encoding_methods = [
                (
                    "h264_qsv",
                    "Using Intel Quick Sync Video (QSV) for hardware acceleration",
                ),
                ("libx264", "Using libx264 software encoding"),
                (None, "Using default moviepy encoder"),
            ]

            for codec, message in encoding_methods:
                try:
                    logger.info(message)
                    final_video.write_videofile(
                        output_path,
                        codec=codec,
                        audio_codec=None,
                        preset="faster" if codec == "libx264" else None,
                        threads=4,
                        fps=30,
                    )
                    break  # If successful, exit the loop
                except Exception as e:
                    logger.warning(
                        f"Error with {codec if codec else 'default'} codec: {str(e)}. Trying next method."
                    )

        logger.info(f"Background video processed successfully: {output_path}")
        return output_path

    except Exception as e:
        logger.error(
            f"An error occurred while processing the background video: {str(e)}"
        )
        raise


# Example usage
if __name__ == "__main__":
    sample_audio_duration = 30

    try:
        processed_video = select_background_video(sample_audio_duration)
        print(f"Processed video: {processed_video}")
    except Exception as e:
        print(f"Error: {str(e)}")
