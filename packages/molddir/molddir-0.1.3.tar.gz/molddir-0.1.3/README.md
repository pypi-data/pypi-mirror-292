# molddir: Encoder-Decoder Module

molddir is a Python package that provides a simple way to encode and decode files and directories into a custom format. This module is particularly useful in the era of Large Language Models (LLMs), where sending a complete codebase to an LLM can be a tedious task. molddir helps by encoding the entire codebase into a single string, which can then be easily decoded back into the original files and directories.

## Features
* Encoder Class: Encodes files and directories into a custom format.
* Decoder Class: Decodes the encoded data back into files and directories.
* CLI Tool: Provides a command-line interface for easy usage.
* Supports ignoring files from repository `.gitignore` files.
* Allows you to customize the encoding pattern using keys.py module.

# Installation
You can install molddir using Poetry:
```
poetry add molddir
```

Or using pip:
```
pip install molddir
```

# Modules

* `decoder`: Contains the `Decoder` class for decoding the codebase.
* `encoder`: Contains the `Encoder` class for encoding the codebase.
* `keys`: Contains the `KeyBuilder` class for building keys.
* `walker`: Contains the `FolderWalker` class for walking through folders.

## Using the Module
### Encoder Class

The Encoder class is responsible for encoding files and directories into a custom format. It takes in a codebase path as an argument, which can be a file or a directory.
```
from molddir import Encoder

encoder = Encoder("path/to/codebase")
encoded_data = encoder()
print(encoded_data)
```
### Decoder Class

The Decoder class is responsible for decoding the encoded data back into files and directories.
```
from molddir import Decoder

decoder = Decoder("output_dir")
decoder(encoded_str="@@@@@@@file1@@@@@@@\nprint('Hello, World!')\n=======\n")
```

## Using the CLI Tool
This script `main.py` provides a command-line interface (CLI) for encoding and decoding a codebase. It supports the following functionalities:
- Encoding a codebase using the `Encoder` class.
- Decoding an encoded file using the `Decoder` class.
- Displaying the version of the tool.

### Usage

```
python main.py --encode --codebase_path <path_to_codebase>
python main.py --decode --encoded_file <path_to_encoded_file> --output_dir <output_directory>
python main.py -v | --version
```

### Arguments
* --encode: Encode the codebase.
* --decode: Decode the codebase.
* --codebase_path: Path to the codebase to encode.
* --encoded_file: Path to the encoded file to decode.
* --output_dir: Directory to save the decoded codebase.
* -v, --version: Display the version of the tool.

### Examples

#### Encode a Codebase
```
python main.py --encode --codebase_path /path/to/codebase
```

#### Decode an encoded file
```
python main.py --decode --encoded_file /path/to/encoded/file --output_dir /path/to/output/dir
```
#### Display the version
```
python main.py -v
```

# Why Use molddir?
In the era of Large Language Models (LLMs), sending a complete codebase to an LLM can be a tedious task. molddir simplifies this process by encoding the entire codebase into a single string. This encoded string can then be easily sent to an LLM, and decoded back into the original files and directories when needed.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.
