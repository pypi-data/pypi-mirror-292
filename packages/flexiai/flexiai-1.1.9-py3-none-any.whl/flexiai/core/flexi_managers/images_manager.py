# flexiai/core/flexi_managers/images_manager.py
import requests
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAIError


class ImagesManager:
    """
    ImagesManager handles the creation of images using OpenAI's DALL-E model.

    Attributes:
        client (OpenAI or AzureOpenAI): The client for interacting with OpenAI or Azure OpenAI services.
        logger (logging.Logger): The logger for logging information and errors.
    """

    def __init__(self, client, logger):
        """
        Initializes the ImagesManager with the OpenAI client and logger.

        Args:
            client (object): The OpenAI client instance.
            logger (logging.Logger): The logger instance for logging information.
        """
        self.client = client
        self.logger = logger


    def create_image(self, prompt, n=1, size="1024x1024", model="dall-e-3", response_format="url"):
        """
        Creates images based on the given prompt using OpenAI's DALL-E model.

        Args:
            prompt (str): The text prompt to generate images.
            n (int): The number of images to generate. Default is 1.
            size (str): The size of the generated images. Default is "1024x1024".
            model (str): The model to use for image generation. Default is "dall-e-3".
            response_format (str): The format of the response. Can be "url" or "b64_json". Default is "url".

        Returns:
            list: A list of URLs or base64-encoded JSON strings of the generated images.

        Raises:
            OpenAIError: If the image generation API call fails.
            Exception: For any unexpected errors.
        """
        try:
            # self.logger.info(f"Creating image with prompt: {prompt[:50]}...")
            response = self.client.images.generate(
                prompt=prompt,
                model=model,
                n=n,
                size=size,
                response_format=response_format
            )
            self.logger.info("Image created successfully.")
            if response_format == 'url':
                return [image.url for image in response.data]
            else:
                return [image.b64_json for image in response.data]
        except OpenAIError as e:
            self.logger.error(f"OpenAI error during image creation: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during image creation: {str(e)}", exc_info=True)
            raise


    def save_image(self, image_data, file_path, response_format='url'):
        """
        Saves the generated image to a file.

        Args:
            image_data (str): The image URL or base64-encoded JSON string.
            file_path (str): The file path to save the image.
            response_format (str): The format of the image data. Can be "url" or "b64_json". Default is "url".

        Raises:
            Exception: If an error occurs while saving the image.
        """
        try:
            if response_format == 'url':
                response = requests.get(image_data)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(BytesIO(base64.b64decode(image_data)))

            image.save(file_path)
            self.logger.info(f"Image saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Error saving image: {str(e)}", exc_info=True)
            raise
