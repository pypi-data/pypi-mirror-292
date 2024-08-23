# flexiai/core/flexi_managers/audio_manager.py
from openai import OpenAIError


class SpeechToTextManager:
    def __init__(self, client, logger):
        """
        Initializes the SpeechToTextManager with the OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information.
        """
        self.client = client
        self.logger = logger


    def transcribe_audio(self, audio_file_path, language="en"):
        """
        Transcribes audio to text using OpenAI's Whisper model.

        Args:
            audio_file_path (str): Path to the audio file to be transcribed.
            language (str, optional): Language of the audio file. Defaults to "en".

        Returns:
            str: The transcribed text.

        Raises:
            OpenAIError: If the transcription API call fails.
            Exception: For any unexpected errors.
        """
        try:
            self.logger.info(f"Transcribing audio file: {audio_file_path} in language: {language}")
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            self.logger.info(f"Transcription successful for file: {audio_file_path}")
            return response.text
        except OpenAIError as e:
            self.logger.error(f"OpenAI error during transcription: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during transcription: {str(e)}", exc_info=True)
            raise


class TextToSpeechManager:
    def __init__(self, client, logger):
        """
        Initializes the TextToSpeechManager with the OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information.
        """
        self.client = client
        self.logger = logger


    def construct_output_file_path(self, default_path="user_flexiai_rag/data/audio/", filename="output", audio_format="mp3"):
        """
        Constructs the output file path based on the default path, filename, and audio format.

        Args:
            default_path (str): The default directory path for saving the audio file.
            filename (str): The name of the audio file without the extension.
            audio_format (str): The audio file format (e.g., 'mp3', 'opus').

        Returns:
            str: The constructed file path.
        """
        available_formats = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
        if audio_format not in available_formats:
            raise ValueError(f"Invalid audio format '{audio_format}'. Available formats are: {', '.join(available_formats)}.")

        return f"{default_path}{filename}.{audio_format}"


    def synthesize_speech(self, text, model="tts-1", voice="alloy", output_file="output.mp3"):
        """
        Synthesizes speech from text using OpenAI's text-to-speech model.

        Args:
            text (str): The text to be converted to speech.
            model (str, optional): The TTS model to use ('tts-1' or 'tts-1-hd'). Default is "tts-1".
            voice (str, optional): The voice to use for speech synthesis. Defaults to "alloy". Voices: 'alloy', 
                                'echo', 'fable', 'onyx', 'nova' and 'shimmer'.
            output_file (str, optional): The file path to save the audio. Defaults to "output.mp3". 
                                Supported audio file formats: 'mp3', 'opus', 'aac', 'flac', 'wav', and 'pcm'.

        Returns:
            None

        Raises:
            ValueError: If the model, voice, or output file format is invalid.
            OpenAIError: If the synthesis API call fails.
            Exception: For any unexpected errors.
        """
        available_models = ["tts-1", "tts-1-hd"]
        available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        # Validate model
        if model not in available_models:
            raise ValueError(f"Invalid model '{model}'. Available models are: {', '.join(available_models)}.")

        # Validate voice
        if voice not in available_voices:
            raise ValueError(f"Invalid voice '{voice}'. Available voices are: {', '.join(available_voices)}.")

        try:
            self.logger.info(f"Synthesizing speech for text: '{text[:50]}...' using model: {model} and voice: {voice}")
            response = self.client.audio.speech.create(
                model=model,
                input=text,
                voice=voice
            )
            with open(output_file, "wb") as audio_file:
                audio_file.write(response.content)
            self.logger.info(f"Speech synthesis successful and saved to {output_file}")
        except OpenAIError as e:
            self.logger.error(f"OpenAI error during speech synthesis: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during speech synthesis: {str(e)}", exc_info=True)
            raise



class AudioTranscriptionManager:
    def __init__(self, client, logger):
        """
        Initializes the AudioTranscriptionManager with the OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information.
        """
        self.client = client
        self.logger = logger


    def transcribe_and_format(self, audio_file_path, language="en"):
        """
        Transcribes and formats audio to text.

        Args:
            audio_file_path (str): Path to the audio file to be transcribed.
            language (str, optional): Language of the audio file. Defaults to "en".

        Returns:
            str: The formatted transcribed text.

        Raises:
            OpenAIError: If the transcription API call fails.
            Exception: For any unexpected errors.
        """
        try:
            self.logger.info(f"Transcribing and formatting audio file: {audio_file_path} in language: {language}")
            speech_to_text_manager = SpeechToTextManager(self.client, self.logger)
            transcribed_text = speech_to_text_manager.transcribe_audio(audio_file_path, language)
            formatted_text = self.format_transcription(transcribed_text)
            self.logger.info(f"Transcription and formatting successful for file: {audio_file_path}")
            return formatted_text
        except Exception as e:
            self.logger.error(f"Error in transcribing and formatting audio: {str(e)}", exc_info=True)
            raise


    @staticmethod
    def format_transcription(transcription):
        """
        Formats the transcription text.

        Args:
            transcription (str): The transcribed text.

        Returns:
            str: The formatted transcribed text.
        """
        return transcription.strip().replace("\n", " ")



class AudioTranslationManager:
    def __init__(self, client, logger):
        """
        Initializes the AudioTranslationManager with the OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information.
        """
        self.client = client
        self.logger = logger


    def translate_audio(self, audio_file_path, model="whisper-1"):
        """
        Translates audio to the target language using OpenAI's translation model.

        Args:
            audio_file_path (str): Path to the audio file to be translated.
            model (str, optional): The translation model to use. Defaults to "whisper-1".

        Returns:
            str: The translated text.

        Raises:
            OpenAIError: If the translation API call fails.
            Exception: For any unexpected errors.
        """
        try:
            self.logger.info(f"Translating audio file: {audio_file_path} using model: {model}")
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.translations.create(
                    model=model,
                    file=audio_file
                )
            self.logger.info(f"Translation successful for file: {audio_file_path}")
            return response.text
        except OpenAIError as e:
            self.logger.error(f"OpenAI error during translation: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during translation: {str(e)}", exc_info=True)
            raise
