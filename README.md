<div align="center">

# Python Video Generator

Write a keyword, click a button, and we generate a completely new video.

[![Build Status](https://github.com/pedrojlazevedo/video_name_generator/workflows/build/badge.svg)](https://github.com/pedrojlazevedo/video_name_generator/actions)
[![Coverage Status](https://coveralls.io/repos/github/pedrojlazevedo/video_name_generator/badge.svg?branch=main)](https://coveralls.io/github/pedrojlazevedo/video_name_generator?branch=main)
[![PyPi](https://img.shields.io/pypi/v/video_name_generator)](https://pypi.org/project/video_name_generator)
[![Licence](https://img.shields.io/github/license/USERNAME/video_name_generator)](LICENSE)

<img src="https://raw.githubusercontent.com/justintime50/assets/main/src/python-template/showcase.png" alt="Showcase">

</div>

You can check out the first release video [clicking here](https://www.youtube.com/watch?v=mgxdDL1KbWo).

This project just started, and the code needs a severe clean-up and deep installation guide.
If you have any question about the code, just reach me out and create an issue if you have any problems.


## Install

```bash
# Create a conda environment
conda create -n video_generator python=3.8
```

```bash
# Install dependency manager 
make install
```

```bash
# Install tool
pip install python_video_generator

# Install locally
make install
```

In the package `moviepy` I changed the file `drawing.py`
```python
# line 147
# from
if vector is not None:    
# to
if vector is None:
```

Now adding the TTS package
```bash
git clone https://github.com/coqui-ai/TTS.git
cd TTS.
pip install -e .
cd ..
poetry add ./TTS
```
## Usage

Usage instructions go here.

```bash
python orchestrator.py
```

## Development

```bash
# Get a comprehensive list of development tools
make help
```
