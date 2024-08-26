"""
main.py

This script provides a command-line interface (CLI) for encoding and decoding a codebase.
It supports the following functionalities:
- Encoding a codebase using the `Encoder` class.
- Decoding an encoded file using the `Decoder` class.
- Displaying the version of the tool.

Usage:
    python main.py --encode --codebase_path <path_to_codebase>
    python main.py --decode --encoded_file <path_to_encoded_file> --output_dir <output_directory>
    python main.py -v | --version

Arguments:
    --encode            Encode the codebase.
    --decode            Decode the codebase.
    --codebase_path     Path to the codebase to encode.
    --encoded_file      Path to the encoded file to decode.
    --output_dir        Directory to save the decoded codebase.
    -v, --version       Display the version of the tool.

Examples:
    Encode a codebase:
        python main.py --encode --codebase_path /path/to/codebase

    Decode an encoded file:
        python main.py --decode --encoded_file /path/to/encoded/file --output_dir /path/to/output/dir

    Display the version:
        python main.py -v

Modules:
    - decoder: Contains the `Decoder` class for decoding the codebase.
    - encoder: Contains the `Encoder` class for encoding the codebase.
    - keys: Contains the `KeyBuilder` class for building keys.
    - walker: Contains the `FolderWalker` class for walking through folders.

Logging:
    The script uses the `logging` module to log information at the INFO level.
"""

import argparse
import logging
import importlib.metadata
import sys

from .decoder import Decoder
from .encoder import Encoder


def configure_logging(log_level):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            # logging.FileHandler("app.log", mode="a")
        ],
    )


def main():
    parser = argparse.ArgumentParser(description="Encode or decode a codebase.")
    parser.add_argument("--encode", action="store_true", help="Encode the codebase.")
    parser.add_argument("--decode", action="store_true", help="Decode the codebase.")
    parser.add_argument("--codebase_path", type=str, help="Path to the codebase to encode.")
    parser.add_argument("--encoded_file", type=str, help="Path to the encoded file to decode.")
    parser.add_argument("--output_dir", type=str, help="Directory to save the decoded codebase.")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {importlib.metadata.version('molddir')}"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

    args = parser.parse_args()

    configure_logging(args.log_level.upper())

    try:
        if args.encode and args.decode:
            parser.error("Cannot encode and decode at the same time. Choose one.")
        elif args.encode:
            if not args.codebase_path:
                parser.error("The --codebase_path must be provided for encoder.")
            _ = Encoder(codebase_path=args.codebase_path)()
        elif args.decode:
            if not args.encoded_file or not args.output_dir:
                parser.error("Both --encoded_file and --output_dir must be specified for decoder.")
            Decoder(output_dir=args.output_dir)(encoded_file=args.encoded_file)
        elif not args.encode and not args.decode:
            parser.error("Either --encode or --decode must be specified.")
    except Exception as e:
        logging.error("An error occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
