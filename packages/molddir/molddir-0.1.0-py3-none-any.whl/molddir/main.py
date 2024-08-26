import argparse
import logging

from .decoder import Decoder
from .encoder import Encoder

logging.basicConfig(level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description="Encode or decode a codebase.")
    parser.add_argument("--encode", action="store_true", help="Encode the codebase.")
    parser.add_argument("--decode", action="store_true", help="Decode the codebase.")
    parser.add_argument(
        "--codebase_path", type=str, help="Path to the codebase to encode."
    )
    parser.add_argument(
        "--encoded_file", type=str, help="Path to the encoded file to decode."
    )
    parser.add_argument(
        "--output_dir", type=str, help="Directory to output the decoded codebase."
    )

    args = parser.parse_args()

    if args.encode and args.decode:
        parser.error("Cannot encode and decode at the same time. Choose one.")
    elif args.encode:
        if not args.codebase_path:
            parser.error("The --codebase_path must be provided for encoding.")
        _ = Encoder(codebase_path=args.codebase_path)()
    elif args.decode:
        if not args.encoded_file or not args.output_dir:
            parser.error(
                "Both --encoded_file and --output_dir must be specified for decoding."
            )
        Decoder(output_dir=args.output_dir)(encoded_file=args.encoded_file)
    else:
        parser.error("Either --encode or --decode must be specified.")


if __name__ == "__main__":
    main()
    # encode_or_decode(encode=True)
    # encode_or_decode(encode=False)
