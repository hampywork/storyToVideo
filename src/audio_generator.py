import os
import torch
import logging
from TTS.api import TTS
from utils.config_loader import load_config

logger = logging.getLogger(__name__)

# Load configuration
config = load_config("config/main_config.toml")


def generate_audio(text, output_path):
    """
    Generate audio from the given text using the TTS module.

    :param text: The text to convert to speech
    :param output_path: The path where the audio file will be saved
    :return: The path to the generated audio file
    """
    try:
        logger.info("Initializing TTS model")

        device = "cuda" if torch.cuda.is_available() else "cpu"

        tts = TTS(
            model_name=config["tts"]["model_name_2"],
            progress_bar=True,
        ).to(device)

        logger.info(f"Generating audio for text: {text[:50]}...")
        tts.tts_to_file(
            text=text,
            speaker="Damian Black",
            language="en",
            file_path=output_path,
            split_sentences=True,
            speed=1.5,
        )

        logger.info(f"Audio generated successfully: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"An error occurred while generating audio: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    sample_text = "Hi, I am new to Reddit. I've seen many videos related to this thread and decided to give it a try. Here's the story: Today, I, a sixteen-year-old female, was having lunch with my friend, a seventeen-year-old male whom we'll call K."
    output_file = "output/test_audio.wav"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    generated_audio = generate_audio(sample_text, output_file)
    print(f"Audio generated: {generated_audio}")
