import os
import json
import logging
from utils.config_loader import load_config

from groq import Groq


logger = logging.getLogger(__name__)

# Load configuration
config = load_config("config/main_config.toml")

# Determine which API to use based on environment variables

model = config["ai"]["groq_model"]
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
logger.info("Using Groq API")


def clean_story(story):
    prompt = """You are an expert in preparing text for voiceover AI. Your task is to clean up the given story without changing its content or length. 
    Focus on making it more suitable for audio narration.

    Guidelines:
    1. Do not change the story's length or content.
    2. Ensure proper punctuation for clear pausing and intonation in speech.
    3. Spell out numbers, symbols, and abbreviations for clear pronunciation.
    4. Adjust any words or phrases that might be difficult for a voiceover AI to pronounce correctly.
    5. Maintain the original structure and flow of the story.
    6. Do not add or remove any information from the original story.

    Please format your output as a JSON object with a single key 'cleaned_story'.

    # Output
    {"cleaned_story": "Here is the cleaned story ..."}
    """

    try:
        logger.info("Sending story to AI for cleaning")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": story},
            ],
        )
        content = response.choices[0].message.content
        logger.debug(f"Received response from AI: {content}")

        # Try to parse the JSON response
        try:
            cleaned_story = json.loads(content)["cleaned_story"]
        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse JSON response, attempting to extract JSON substring"
            )
            json_start_index = content.find("{")
            json_end_index = content.rfind("}")
            content = content[json_start_index : json_end_index + 1]
            cleaned_story = json.loads(content)["cleaned_story"]

        logger.info("Successfully cleaned the story")
        return cleaned_story

    except Exception as e:
        logger.error(f"An error occurred while cleaning the story: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    sample_story = """
    Hi, I am new to Reddit but have seen many videos surrounding this thread and thought I'd give it a try. To the story:  Today I, 16 (female), was having lunch with my friend 17 (male), let's call him K. We were walking down the hallway when these two boys stopped us and asked me for my number for their friend who's had a crush on me for a while apparently. I said no, I am a lesbian and therefore not into men. They responded with ""oh, don't worry, he's transgender."" I asked, ""FTM or MTF?"" They responded, ""FTM,"" but it doesn't matter because he has the lady parts I'm into. It took me a moment to respond, but he's a dude. They keep trying to convince me that it's fine. Luckily, K steps in and just pulls me away because they weren't going to let me leave that conversation without my number. K said I wasn't the asshole because I'm not into men and he identifies as a man. But my other friend L said it was transphobic for not giving him at least a chance. So now I'm very confused, am I the asshole?
    """

    cleaned_story = clean_story(sample_story)
    print(cleaned_story)
