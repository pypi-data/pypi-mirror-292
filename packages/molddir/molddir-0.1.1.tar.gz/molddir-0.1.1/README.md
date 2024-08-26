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

# Usage
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
molddir also provides a command-line interface for easy usage.

### Encoding
To encode a codebase, run:
```
molddir --encode --codebase_path path/to/codebase
```

### Decoding
To decode the encoded data back into files and directories, run:
```
molddir --decode --encoded_file encoded_data.txt --output_dir output_dir
```

# Why Use molddir?
In the era of Large Language Models (LLMs), sending a complete codebase to an LLM can be a tedious task. molddir simplifies this process by encoding the entire codebase into a single string. This encoded string can then be easily sent to an LLM, and decoded back into the original files and directories when needed.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License. See the LICENSE file for details.