import logging
import os
import re
from copy import copy
import shutil
from typing import List, Optional, Tuple

from .keys import KeyBuilder

logger = logging.getLogger(__name__)


class Decoder:
    """
    A class used to decode and recreate a codebase from an encoded file or string.

    The Decoder class takes an output directory as an argument in its constructor.
    It ensures the output directory is empty before proceeding.
    The class provides a callable interface that accepts either an encoded file path or an encoded string.
    It reads the content, parses it, and recreates the codebase in the specified output directory.

    Args:
        output_dir (str): The directory where the decoded codebase will be recreated.

    Raises:
        ValueError: If the output directory is not empty.
        FileNotFoundError: If the provided encoded file path does not exist.
        ValueError: If neither encoded_file nor encoded_str is provided.

    Attributes:
        _output_dir (str): The output directory where the decoded codebase will be recreated.
    """

    _output_dir: str
    _keybuilder: KeyBuilder
    _incremental: bool

    def __init__(self, output_dir: str, incremental: bool = False):
        """
        Initializes the Decoder with the given output directory.

        Attributes:
        _output_dir (str): The directory where the decoded codebase will be recreated..
        """
        os.makedirs(output_dir, exist_ok=True)
        if os.listdir(output_dir) and (not incremental):
            raise ValueError(f"Path {output_dir} is not Empty")
        self._output_dir = output_dir
        self._keybuilder = KeyBuilder()
        self._incremental = incremental

    def __call__(self, encoded_file: Optional[str] = None, encoded_str: Optional[str] = None):
        """
        Decodes the encoded file or string into a codebase.

        This method decodes the encoded file or string into a codebase and writes
        it to the output directory specified during the initialization of the
        Decoder object.

        Args:
            encoded_file: The path to the encoded file. If specified, the method
                will read the file and decode its contents.
            encoded_str: The encoded string. If specified, the method will decode
                the string.

        Returns:
            None

        Raises:
            ValueError: If neither encoded_file nor encoded_str is specified.
            FileNotFoundError: If the encoded_file is specified but does not exist.

        Notes:
            incase encoded_file and encoded_str are both not none encoded_file will be considered as
            input .
        """
        if encoded_file is not None:
            if not os.path.isfile(encoded_file):
                raise FileNotFoundError(f"Path {encoded_file} is not a valid Path")
            content = self._read_input(encoded_file)
        elif encoded_str is not None:
            content = copy.deepcopy(encoded_str)
        else:
            raise ValueError("Either provide encoded_file or encoded_str")
        if content is None:
            return
        parsed_output = self._parse_data(content)
        if not parsed_output:
            return
        self._recreate_codebase(parsed_output)
        pass

    def _parse_data(self, content: str) -> List[Tuple[str, str]]:
        """
        Parses the encoded content into a list of file paths and code blocks.

        This method takes in the encoded content, extracts the file paths and
        code blocks, and returns them as a list of tuples.

        Args:
            content: The encoded content to be parsed.

        Returns:
            A list of tuples, where each tuple contains a file path and a code block.

        Examples:
            >>> decoder = Decoder("output_dir")
            >>> encoded_content = "@@@@@@file1@@@@@@@\nprint('Hello, World!')\n=======\n"
            >>> parsed_output = decoder._parse_data(encoded_content)
            >>> parsed_output
            [("file1", "print('Hello, World!')")]
        """
        # pattern = r"""@@@@@@@(?P<filename>.*?)@@@@@@@\n(?P<code_block>.*?)\n=======\n"""
        decoder_key = self._keybuilder.decoder_key
        parsed_output = []
        for match in re.finditer(decoder_key, content, re.DOTALL | re.VERBOSE):
            file_name = match.group("file_path").strip()
            code_block = match.group("code_block").lstrip()
            logger.debug(f"File: {file_name}")
            logger.debug(f"Code Code: {code_block[:10]}")
            parsed_output.append((file_name, code_block))
        if parsed_output:
            logger.info(f"Total {len(parsed_output)} Code Blocks found")
        else:
            logger.info("NO Match Found ...")
        return parsed_output

    def _read_input(self, encoded_file: str) -> Optional[str]:
        try:
            content = None
            with open(encoded_file) as f:
                content = f.read()
        except Exception as err:
            content = None
            logger.error(f"Error While Reading file {encoded_file}, Err {err}")
        finally:
            return content

    def _recreate_codebase(self, parsed_output: List[Tuple[str, str]]):
        """
        Recreates the codebase from the parsed output.

        This method takes in the parsed output, which is a list of tuples containing
        file paths and code blocks, and recreates the codebase by writing the code
        blocks to their corresponding file paths in the output directory.

        Args:
            parsed_output: A list of tuples, where each tuple contains a file path
                and a code block.

        Examples:
            >>> decoder = Decoder("output_dir")
            >>> parsed_output = [("file1.py", "print('Hello, World!')"), ("dir1/file2.py", "def func(): pass")]
            >>> decoder._recreate_codebase(parsed_output)
            # Output files will be written to the output directory
        """
        while parsed_output:
            relative_path, code_block = parsed_output.pop()
            parent_dir, filename = os.path.split(relative_path)
            if parent_dir != "":
                os.makedirs(os.path.join(self._output_dir, parent_dir), exist_ok=True)
            self._write_file(code_block, relative_path)

    def _write_file(self, content: str, path: str):
        full_path = os.path.join(self._output_dir, path)
        if self._incremental:
            head, tail = os.path.splitext(os.path.basename(path))
            new_path = path.replace(f"{head}{tail}", f"{head}_bkp{tail}")
            new_full_path = os.path.join(self._output_dir, new_path)
            shutil.copyfile(full_path, new_full_path)
        return_status = True
        try:
            with open(full_path, "w", encoding="utf8") as f:
                f.write(content)
        except Exception as err:
            logger.error(f"Error While Writing output file {path}, Err {err}")
            return_status = False
        else:
            logger.info(f"Writing of output file {path} complete")
            return_status = True
        finally:
            return return_status
