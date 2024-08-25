import configparser
import os

from flask import request, jsonify
from openai import OpenAI
from pupil_apriltags import Detector

from openmmla_vision.utils.apriltag_utils import detect_apriltags
from openmmla_vision.utils.logger_utils import get_logger
from openmmla_vision.utils.prompt_utils import parse_text_to_dict, generate_llm_prompt_msg, generate_vlm_prompt_msg


class VideoFrameAnalyzer:
    """Video frame analyzer receives images, processes them with VLM and LLM, and returns the results."""

    def __init__(self, project_dir, config_path=None):
        """Initialize the video frame analyzer.
        Args:
            project_dir: the project directory.
        """
        self.server_logger_dir = os.path.join(project_dir, 'server/logger')
        self.server_file_folder = os.path.join(project_dir, 'server/temp')
        os.makedirs(self.server_logger_dir, exist_ok=True)
        os.makedirs(self.server_file_folder, exist_ok=True)

        self.logger = get_logger('VideoFrameAnalyzer',
                                 os.path.join(self.server_logger_dir, 'video_frame_analyzer_server.log'))

        if config_path:
            if os.path.isabs(config_path):
                self.config_path = config_path
            else:
                self.config_path = os.path.join(project_dir, config_path)
        else:
            self.config_path = os.path.join(project_dir, 'conf/video_base.ini')

        # Check if the configuration file exists
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")

        config = configparser.ConfigParser()
        config.read(self.config_path)

        self.families = config['DEFAULT']['families']
        self.backend = config['Server']['backend']
        self.vlm_model = config['Server']['vlm_model']
        self.llm_model = config['Server']['llm_model']
        self.top_p = float(config['Server']['top_p'])
        self.temperature = float(config['Server']['temperature'])

        if self.backend == 'ollama':
            self.api_key = config['ollama']['api_key']
            self.vlm_base_url = config['ollama']['base_url']
            self.llm_base_url = config['ollama']['base_url']
        elif self.backend == 'vllm':
            self.api_key = config['vllm']['api_key']
            self.vlm_base_url = config['vllm']['vlm_base_url']
            self.llm_base_url = config['vllm']['llm_base_url']
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

        self.detector = Detector(families=self.families, nthreads=4)

        self.vlm_client = OpenAI(
            api_key=self.api_key,
            base_url=self.vlm_base_url,
        )

        self.llm_client = OpenAI(
            api_key=self.api_key,
            base_url=self.llm_base_url,
        )

        # Load action definitions from config
        self.action_definitions = '\n'.join([f"'{key}': {value}" for key, value in config['ActionDefinitions'].items()])

        # Load VLM extra body from config
        self.vlm_extra_body = {}
        if 'VLMExtraBody' in config:
            for key, value in config['VLMExtraBody'].items():
                if key == 'stop_token_ids':
                    self.vlm_extra_body[key] = [int(token) for token in value.split(',')]
                else:
                    self.vlm_extra_body[key] = value

    def process_image(self):
        """Process the image.

        Returns:
            A tuple containing the response and status code.
        """
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        try:
            image_file = request.files['image']
            image_data = image_file.read()

            # Detect AprilTags
            id_positions = detect_apriltags(image_data, self.detector, show=False)

            # Process with VLM
            vlm_messages = generate_vlm_prompt_msg(id_positions, image_data)
            vlm_response = self.vlm_client.chat.completions.create(
                model=self.vlm_model,
                messages=vlm_messages,
                top_p=self.top_p,
                temperature=self.temperature,
                extra_body=self.vlm_extra_body
            )
            image_description = vlm_response.choices[0].message.content

            # Process with LLM
            llm_messages = generate_llm_prompt_msg(image_description, self.action_definitions)
            llm_response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=llm_messages,
                top_p=self.top_p,
                temperature=self.temperature
            )
            categorization_result = llm_response.choices[0].message.content
            parsed_result = parse_text_to_dict(categorization_result)

            return jsonify({
                'image_description': image_description,
                'categorization_result': parsed_result
            }), 200

        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return jsonify({"error": str(e)}), 500
