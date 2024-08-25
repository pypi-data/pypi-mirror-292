import os
import aiohttp
import base64
import cairosvg
import json

from json_repair import repair_json
from zinley.v2.code.log.logger_config import get_logger
logger = get_logger(__name__)

class ImageScanner:
    def __init__(self, project_path, api_key, endpoint, deployment_id, max_tokens):
        self.project_path = project_path
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_id = deployment_id
        self.max_tokens = max_tokens
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def scan_files_in_project(self):
        """
        Scan for all images in the project directory, including those within .xcassets.

        Returns:
            dict: Paths to all general image files and .xcassets images.
        """
        general_image_files = []
        xcassets_image_files = []

        for root, dirs, files in os.walk(self.project_path):
            if 'Pods' in root or 'AppIcon.appiconset' in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    if '.xcassets' in root:
                        xcassets_image_files.append(file_path)
                    else:
                        general_image_files.append(file_path)

        return {
            "general_images": general_image_files,
            "xcassets_images": xcassets_image_files,
        }

    def encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.info(f"Failed to encode image {image_path}: {e}")
            return None

    def convert_svg_to_png(self, svg_path):
        try:
            png_path = svg_path.replace('.svg', '_scanner.png')
            cairosvg.svg2png(url=svg_path, write_to=png_path)
            if os.path.exists(png_path):
                return png_path
            else:
                logger.info(f"Conversion failed: {png_path} not found after conversion.")
                return None
        except Exception as e:
            logger.info(f"Failed to convert SVG {svg_path} to PNG: {e}")
            return None

    async def get_image_descriptions(self, images):
        """
        Get descriptions for a list of images from Azure OpenAI.

        Args:
            images (dict): Dictionary containing lists of general and xcassets image paths.

        Returns:
            dict: Dictionary containing usable and unusable image descriptions.
        """
        usable_images = []
        unusable_images = []

        async with aiohttp.ClientSession() as session:
            for image_type, image_paths in images.items():
                is_xcassets_image = image_type == "xcassets_images"
                for image_path in image_paths:
                    try:
                        if image_path.endswith('.svg'):
                            png_path = self.convert_svg_to_png(image_path)
                            if not png_path:
                                unusable_images.append({
                                    "image_path": image_path,
                                    "reason": "Failed to convert SVG to PNG"
                                })
                                continue
                        else:
                            png_path = image_path

                        base64_image = self.encode_image(png_path)

                        if not base64_image:
                            unusable_images.append({
                                "image_path": image_path,
                                "reason": "Failed to encode image"
                            })
                            continue

                        payload = {
                            "messages": [
                                {
                                    "role": "system",
                                    "content": (
                                        f"You are a senior iOS developer. Analyze this icon/image for an Xcode project. The file name is {os.path.basename(png_path).replace('.svg', '').replace('.png', '')}. Provide a short description (under 150 characters) including its potential use with examples like back button, microphone icon, user icon, etc. Indicate if the image is unusable due to being too blurry, unclear, or any other reason and must mention unusable in your answer for unusable case."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": f"data:image/jpeg;base64,{base64_image}"
                                }
                            ],
                            "temperature": 0.2,
                            "top_p": 0.1,
                            "max_tokens": self.max_tokens
                        }

                        url = f"{self.endpoint}/openai/deployments/{self.deployment_id}/chat/completions?api-version=2024-04-01-preview"

                        async with session.post(url, headers=self.headers, json=payload) as response:
                            if response.status != 200:
                                response_json = await response.json()
                                error_message = response_json.get('error', {}).get('message', 'Unknown error')
                                unusable_images.append({
                                    "image_path": image_path,
                                    "reason": error_message
                                })
                                continue

                            description = await response.json()

                            if 'choices' in description and len(description['choices']) > 0:
                                message_content = description['choices'][0]['message']['content']
                                if "unusable" in message_content.lower():
                                    unusable_images.append({
                                        "image_path": image_path,
                                        "reason": message_content
                                    })
                                else:
                                    if is_xcassets_image:
                                        image_name = os.path.basename(os.path.dirname(image_path).replace('.imageset', ''))
                                    else:
                                        image_name = os.path.basename(image_path).replace('.svg', '').replace('.png', '')

                                    usable_images.append({
                                        "image_path": image_path,
                                        "image_name": image_name,
                                        "description": message_content,
                                        "is_xcassets_image": is_xcassets_image
                                    })

                            if image_path.endswith('.svg'):
                                os.remove(png_path)

                    except json.JSONDecodeError as e:
                        unusable_images.append({
                            "image_path": image_path,
                            "reason": "Failed to decode JSON response",
                            "raw_response": message_content  # Store raw response for reprocessing
                        })
                    except Exception as e:
                        unusable_images.append({
                            "image_path": image_path,
                            "reason": str(e)
                        })

        return {
            "usable_images": usable_images,
            "unusable_images": unusable_images
        }

    async def reprocess_image(self, session, image_path, payload, failed_image, url):
        """
        Reprocess a single failed image.

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use for the request.
            image_path (str): The path to the failed image.
            payload (dict): The payload for the reprocessing request.
            failed_image (dict): The failed image dictionary.
            url (str): The URL for the Azure OpenAI API endpoint.

        Returns:
            dict: The reprocessed image description.
        """
        try:
            async with session.post(url, headers=self.headers, json=payload) as response:
                if response.status != 200:
                    response_json = await response.json()
                    error_message = response_json.get('error', {}).get('message', 'Unknown error')
                    failed_image["reason"] = error_message
                    return failed_image

                description = await response.json()

                if 'choices' in description and len(description['choices']) > 0:
                    message_content = description['choices'][0]['message']['content']

                    try:
                        description_json = json.loads(message_content)
                        failed_image["description"] = description_json
                        failed_image.pop("reason", None)
                        failed_image.pop("raw_response", None)
                    except json.JSONDecodeError:
                        good_json_string = repair_json(message_content)
                        plan_json = json.loads(good_json_string)
                        failed_image["description"] = plan_json
                        failed_image.pop("reason", None)
                        failed_image.pop("raw_response", None)

        except Exception as e:
            failed_image["reason"] = str(e)

        return failed_image
