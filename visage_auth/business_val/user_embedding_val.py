import io
import sys
import numpy as np
from ast import Bytes
from PIL import Image
from typing import List
from deepface import DeepFace
from visage_auth.logger import logging
from visage_auth.exception import AppException
from deepface.commons.functions import detect_face
from visage_auth.data_access.user_embedding_data import UserEmbeddingData
from visage_auth.constant.embedding_constants import (DETECTOR_BACKEND,
                                                    EMBEDDING_MODEL_NAME,
                                                    ENFORCE_DETECTION,
                                                    SIMILARITY_THRESHOLD)


class UserRegisterEmbeddingValidation:
    def __init__(self, uuid_:str) -> None:
        self.uuid_ = uuid_
        self.user_embedding_data = UserEmbeddingData()

    def save_embedding(self, files:bytes):
        """
            This function will generate embedding list and save it to database
            Args:
                files (dict): Bytes of images

            Returns:
                Embedding: saves the image to database
        """
        try:
            embedding_list = UserLoginEmbeddingValidation.generate_embedding_list(files)
            avg_embedding_list = UserLoginEmbeddingValidation.average_embedding(embedding_list)
            self.user_embedding_data.save_user_embedding(self.uuid_, avg_embedding_list)
        
        except Exception as e:
            raise AppException(e, sys) from e