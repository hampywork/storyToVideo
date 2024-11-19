import argparse
from utils.config_loader import load_config
from utils.logger import setup_logger
from src.story_cleaner import clean_story
from src.audio_generator import generate_audio
from src.video_processor import select_background_video
from src.video_renderer import render_vide
from . import captacity


def main():
    # Load configuration
    config = load_config("config/main_config.toml")

    # Setup logger
    logger = setup_logger("config/logging_config.toml")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a video from a story.")
    parser.add_argument("story", type=str, help="The input story")
    args = parser.parse_args()

    try:
        # Clean the story
        logger.info("Cleaning the story...")
        cleaned_story = clean_story(args.story)

        # Generate audio
        logger.info("Generating audio...")
        audio_file = generate_audio(cleaned_story, config["audio"])

        # Select background video
        logger.info("Selecting background video...")
        bg_video = select_background_video(
            config["video"]["background_folder"], audio_file.duration
        )

        # Generate captions
        logger.info("Generating captions...")
        captions = captacity.add_captions(cleaned_story, audio_file)

        # Render final video
        logger.info("Rendering final video...")
        output_file = render_video(audio_file, bg_video, captions, config["output"])

        logger.info(f"Video generated successfully: {output_file}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
