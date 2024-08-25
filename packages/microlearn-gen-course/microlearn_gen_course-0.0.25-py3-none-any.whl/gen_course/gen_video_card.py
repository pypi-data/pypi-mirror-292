import json
import logging
import os
import time
import uuid

import requests

from .utils import remove_markdown


class VideoCardGenerator:
    logger = logging.getLogger(__name__)

    SPEECH_ENDPOINT = os.getenv('SPEECH_ENDPOINT', "https://westeurope.api.cognitive.microsoft.com")
    API_VERSION = "2024-04-15-preview"


    def _create_job_id(self):
        return uuid.uuid4().__str__()


    def _authenticate(self):
        SUBSCRIPTION_KEY = os.getenv("AZURE_SUBSCRIPTION_KEY", "0833ffefa2fe47948d5cd01c93b0b20a")
        return {'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY}


    def submit_synthesis(
            self,
            job_id: str,
            content: str,
            avatar: str,
            avatar_style: str,
            voice: str,
            video_format: str,
            video_codec: str,
            background_image: str,
    ):
        url = f'{self.SPEECH_ENDPOINT}/avatar/batchsyntheses/{job_id}?api-version={self.API_VERSION}'
        header = {
            'Content-Type': 'application/json'
        }
        header.update(self._authenticate())

        payload = {
            'synthesisConfig': {
                "voice": voice,
            },
            'customVoices': {},
            "inputKind": "plainText",
            "inputs": [
                {
                    "content": content,
                },
            ],
            "avatarConfig":
                {
                    "customized": False,
                    "talkingAvatarCharacter": avatar,
                    "talkingAvatarStyle": avatar_style,
                    "videoFormat": video_format,
                    "videoCodec": video_codec,
                    "subtitleType": "soft_embedded",
                    "backgroundImage": background_image,
                }
        }

        response = requests.put(url, json.dumps(payload), headers=header)
        if response.status_code < 400:
            self.logger.info('Batch avatar synthesis job submitted successfully')
            self.logger.info(f'Job ID: {response.json()["id"]}')
            return True
        else:
            self.logger.error(f'Failed to submit batch avatar synthesis job: [{response.status_code}], {response.text}')


    def get_synthesis(self, job_id):
        url = f'{self.SPEECH_ENDPOINT}/avatar/batchsyntheses/{job_id}?api-version={self.API_VERSION}'
        header = self._authenticate()

        response = requests.get(url, headers=header)
        if response.status_code < 400:
            self.logger.debug('Get batch synthesis job successfully')
            self.logger.debug(response.json())
            if response.json()['status'] == 'Succeeded':
                self.logger.info(f'Batch synthesis job succeeded, download URL: {response.json()["outputs"]["result"]}')
            return response.json()['status'], response.json()['outputs']['result'] if response.json()['status'] == 'Succeeded' else response.text
        else:
            self.logger.error(f'Failed to get batch synthesis job: {response.text}')


    def list_synthesis_jobs(self, skip: int = 0, max_page_size: int = 100):
        url = f'{self.SPEECH_ENDPOINT}/avatar/batchsyntheses?api-version={self.API_VERSION}&skip={skip}&maxpagesize={max_page_size}'
        header = self._authenticate()

        response = requests.get(url, headers=header)
        if response.status_code < 400:
            self.logger.info(f'List batch synthesis jobs successfully, got {len(response.json()["values"])} jobs')
            self.logger.info(response.json())
        else:
            self.logger.error(f'Failed to list batch synthesis jobs: {response.text}')


    def gen_batch_avatar_synthesis(
            self,
            content: str,
            avatar: str = 'Max',
            avatar_style: str = 'casual',
            voice: str = 'it-IT-GiuseppeMultilingualNeural',
            video_format: str = 'webm',
            video_codec: str = 'vp9',
            background_image: str = 'https://aipedia-static-bucket-dev.s3.eu-central-1.amazonaws.com/media/public/static/images/1724502114_yh5xvfl2.jpg',
    ) -> str:
        start = time.time()
        job_id = self._create_job_id()
        if self.submit_synthesis(
                job_id,
                remove_markdown(content),
                avatar,
                avatar_style,
                voice,
                video_format,
                video_codec,
                background_image,
        ):
            while True:
                status, api_response = self.get_synthesis(job_id)
                if status == 'Succeeded':
                    self.logger.info('batch avatar synthesis job succeeded')
                    end = time.time()
                    self.logger.info(f'Time elapsed: {end - start} seconds')
                    return api_response
                elif status == 'Failed':
                    self.logger.error('batch avatar synthesis job failed')
                    raise Exception(f'Batch avatar synthesis job failed: {api_response}')
                else:
                    self.logger.info(f'batch avatar synthesis job is still running, status [{status}]')
                    time.sleep(5)