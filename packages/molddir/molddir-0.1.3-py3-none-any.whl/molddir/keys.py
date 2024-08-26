import logging
import re
from copy import copy
from typing import Optional

logger = logging.getLogger(__name__)

ENCODER_PATTERERN: str = """@@@@@@@{file_path}@@@@@@@\n{code_block}\n=======\n"""
DECODER_PATTERERN: str = r"""@@@@@@@(?P<file_path>.*?)@@@@@@@\n(?P<code_block>.*?)\n=======\n"""


class KeyBuilder:
    """
    KeyBuilder is a utility class for encoding and decoding code blocks with file paths.

    This class provides methods to generate encoded keys and validate them using regular expressions.
    It includes properties for encoder and decoder patterns, and a method to validate the keys.

    Methods:
    - enccoder_key: Returns the pattern for encoding a file path and code block.
    - decoder_key: Returns the pattern for decoding a file path and code block.
    - _validate_keys: Validates the encoded key by matching it against the decoder pattern.
    """

    _encoder_key: str
    _decoder_key: str

    def __init__(self, encoder_key: Optional[str] = None, decoder_key: Optional[str] = None):
        self._encoder_key = copy(ENCODER_PATTERERN) if encoder_key is None else encoder_key
        self._decoder_key = copy(DECODER_PATTERERN) if decoder_key is None else decoder_key
        self._validate_keys()

    @property
    def encoder_key(self) -> str:
        return self._encoder_key

    @property
    def decoder_key(self) -> str:
        return self._decoder_key

    def _validate_keys(self) -> bool:
        if not self._encoder_key or not self._decoder_key:
            raise ValueError("Both encoder_key and decoder_key must be provided")
        test_file = "test_filename.tsx"
        test_Content = """import React from 'react';

        const HelloWorld = () => {
          return (
            <div>
              <h1>Hello, World!</h1>
            </div>
          );
        };

        export default HelloWorld;"""
        encoded_ = self.encoder_key.format(file_path=test_file, code_block=test_Content)
        match = re.finditer(self.decoder_key, encoded_, re.DOTALL | re.VERBOSE)
        if match is None or len(list(match)) == 0:
            logger.error("Key Validation Failed")
            raise ValueError("Key Validation Failed")
        for item in match:
            file_name = item.group("file_path").strip()
            code_block = item.group("code_block").lstrip()
            if file_name != test_file or code_block != test_Content:
                logger.error("Key Validation Failed")
                raise ValueError("Key Validation Failed")
        return True
