import gc
import io
import os

from flask import request, jsonify, send_file

from openmmla_audio.utils.audio_utils import resample, write_frames_to_file
from openmmla_audio.utils.logger_utils import get_logger


class AudioResampler:
    """Audio resampler receives audio signals from audio base stations, and then resample them and send it back."""

    def __init__(self, project_dir):
        """Initialize the audio resampler.

        Args:
            project_dir: the project directory.
        """
        self.server_logger_dir = os.path.join(project_dir, 'server/logger')
        self.server_file_folder = os.path.join(project_dir, 'server/temp')
        os.makedirs(self.server_logger_dir, exist_ok=True)
        os.makedirs(self.server_file_folder, exist_ok=True)

        self.logger = get_logger('resampler', os.path.join(self.server_logger_dir, 'resample_server.log'))

    def resample_audio(self):
        """Resample the audio.

        Returns:
            A tuple containing the response and status code.
        """
        if request.files:
            try:
                base_id = request.values.get('base_id')
                fr = int(request.values.get('fr'))
                target_fr = int(request.values.get('target_fr'))
                audio_file = request.files['audio']
                audio_file_path = os.path.join(self.server_file_folder, f'resample_audio_{base_id}.wav')
                write_frames_to_file(audio_file_path, audio_file.read(), 1, 2, fr)

                self.logger.info(f"starting resampling for {base_id}...")
                resample(audio_file_path, target_fr)
                self.logger.info(f"finished resampling for {base_id}...")

                with open(audio_file_path, 'rb') as f:
                    audio_data = f.read()
                return send_file(io.BytesIO(audio_data), mimetype="audio/wav"), 200
            except Exception as e:
                self.logger.error(f"during resampling, {e} happens.")
                return jsonify({"error": str(e)}), 500
            finally:
                gc.collect()
        else:
            return jsonify({"error": "No audio file provided"}), 400
