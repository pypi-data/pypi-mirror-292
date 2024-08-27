import logging
import os
from datetime import datetime
from typing import Optional

from .keys import KeyBuilder
from .walker import FolderWalker

logger = logging.getLogger(__name__)


class Encoder:
    """
    Encoder class responsible for encoding the entire code base into a string format.

    This class provides a way to encode entire code base into a string format that can be
    later decoded by the Decoder class. The encoding process involves taking in
    reading files content from all directory iteratively , and generating a string
    representation of the code blocks.

    Attributes:
        _codebase_path: str: The path to the file or directory to be encoded.

    Notes:
        The encoding process is the reverse of the decoding process performed by
        the Decoder class. The encoded string format is designed to be compatible
        with the decoding pattern used by the Decoder class.

    Raises:
        ValueError: If the input code_blocks is empty or invalid.
        FileNotFoundError: If the output_file is specified but does not exist.

    """

    _codebase_path: str

    def __init__(
        self,
        codebase_path: str,
        encoder_key: Optional[str] = None,
        decoder_key: Optional[str] = None,
        escape: Optional[str] = None,
        incremental: bool = False,
    ):
        """Initializes the Encoder with the given code base path.

        Attributes:
        _codebase_path (str): The path to the file or directory to be encoded.
        """

        if not os.path.exists(codebase_path):
            raise FileNotFoundError(f"Path {codebase_path} is not exists")
        self._codebase_path = str(codebase_path)
        self._keybuilder = KeyBuilder(encoder_key, decoder_key)
        self._walker = FolderWalker(codebase_path=self._codebase_path, escape=escape, incremental=incremental)

    def __call__(self, save_encoding: bool = True) -> Optional[str]:
        """Encodes the file or directory and writes the encoded data to a file.
            This method is the entry point for encoding a file or directory.
            It calls the appropriate encoding method (_encode_file or _encode_directory)
            and writes the encoded data to a file using _write_encode_data.

        Returns:
            str: encoded_string if the encoding is successful, None otherwise.
        """
        encoded_data = None
        if os.path.isdir(self._codebase_path):
            encoded_data = self._encode_directory()
        elif os.path.isfile(self._codebase_path):
            encoded_data = self._encode_file(self._codebase_path)
        else:
            raise ValueError(f"Path {self._codebase_path} is not a valid File or Directory")
        if encoded_data is None:
            return None
        if save_encoding:
            self._write_encode_data(encoded_data)
        return encoded_data

    def _encode_file(self, path: str) -> Optional[str]:
        """
        Encodes a single file into the custom format.

        Args:
            path (str): The path to the file to be encoded.

        Returns:
            Optional[str]: The encoded content of the file, or None if the file cannot be read.
        """
        encoder_key = self._keybuilder.encoder_key
        relative_path = os.path.relpath(path, self._codebase_path)
        logger.debug(f"processing {relative_path}")
        relative_path = os.path.basename(path) if relative_path == "." else relative_path
        try:
            content = None
            with open(path, "r") as f:
                content = f.read()
        except Exception as err:
            content = None
            relative_path = None
            logger.error(f"Error While Reading file {relative_path}, Err {err}")
        finally:
            if (relative_path is None) or (content is None):
                return None
            else:
                return encoder_key.format(file_path=relative_path, code_block=content)

    def _encode_directory(self) -> Optional[str]:
        """
        Encodes a directory and its contents into the custom format.

        Args:
            path (str): The path to the directory to be encoded.

        Returns:
            str: The encoded content of the directory, including all files and subdirectories.
        """
        final_output = ""
        for item_path in self._walker:
            content = self._encode_file(item_path)
            if content is None:
                continue
            final_output = final_output + content
        return final_output if final_output else None

    def _write_encode_data(self, content: str) -> bool:
        """
        Writes the encoded data to a file.

        Args:
            encoded_data (str): The encoded data to be written.
            output_file (str): The path to the file where the encoded data will be written.

        Returns:
            None
        """
        if os.path.isfile(self._codebase_path):
            basename = os.path.basename(self._codebase_path)
            basename = os.path.basename(basename)
            outfile_name = f'{basename}_encoded_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.txt'
        else:
            basename = os.path.basename(os.path.dirname(self._codebase_path))
            outfile_name = f'{basename}_encoded_{datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.txt'
        return_status = True
        try:
            with open(outfile_name, "w", encoding="utf8") as f:
                f.write(content)
        except Exception as err:
            logger.error(f"Error While Writing Output File {outfile_name}, Error {err}")
            return_status = False
        else:
            logger.info(f"Writing Output File {outfile_name} Complete")
            return_status = True
        finally:
            return return_status
