# DIRP 

DirP (DIRectory Print) is a command-line utility for pretty printing directories. It generates a nice looking tree representation of its first argument, assuming a valid path. 

For example, running dirp while in the root directory of my [Akashic](https://github.com/prettytrippy/Akashic) project, we see:

```
(base) trippdow@This-Computer Akashic % dirp .
Akashic/
│   Documents/
│   __pycache__/
│   │   └── __init__.cpython-311.pyc
│   │   └── chat.cpython-310.pyc
│   │   └── chat.cpython-311.pyc
│   │   └── chatbots.cpython-310.pyc
│   │   └── chatbots.cpython-311.pyc
│   │   └── chunkers.cpython-311.pyc
│   │   └── embedders.cpython-311.pyc
│   │   └── file_io.cpython-311.pyc
│   │   └── retrieval.cpython-311.pyc
│   │   └── text_utilities.cpython-311.pyc
│   templates/
│   │   └── chat.html
│   │   └── collections.html
│   │   └── index.html
│   └── .env
│   └── .gitignore
│   └── README.md
│   └── __init__.py
│   └── app.py
│   └── architect.py
│   └── chat.py
│   └── chatbots.py
│   └── chunkers.py
│   └── collections.txt
│   └── embedders.py
│   └── file_io.py
│   └── llama_chat_format.py
│   └── playground.py
│   └── retrieval.py
│   └── text_utilities.py
│   └── webscraper.py
```

This output is useful for communicating directory structures to others over text, or prompting a chatbot assistant.

## Setup

#### From Github:

```git clone https://github.com/prettytrippy/dirp```

Edit your ```~/.bashrc```, ```~/.zshrc``` or other to say:
```alias dirp = "path/to/dir_print.py"```

#### From PyPI

```pip install dirp```

## Usage

```dirp path/to/directory/to/print```

## License

MIT License, see LICENSE.
