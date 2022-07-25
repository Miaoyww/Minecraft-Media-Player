<div align="center">

![Alt](exp.png "exp")

# Minecraft Media Player

![python-version](https://img.shields.io/badge/Python-3.6%2B-red)
![minecraft-version](https://img.shields.io/badge/Minecraft-1.13%2B-red)
![license](https://img.shields.io/github/license/Miaoywww/Minecraft-Media-Player)

A python script that can let you play the videos and show the images in Minecraft.

`Datapack Theoretical Support 1.13+`

![Alt](https://repobeats.axiom.co/api/embed/20e7170bc0d93a9fa80fe0bde4d738e56e480ee2.svg "Repobeats analytics image")

*** 

</div>

**English** | [中文](https://github.com/Fallen-Breath/MCDReforged/blob/master/README_cn.md)

## Download

Clone it to your computer by the git or download it in GitHub.

``` 
git clone https://github.com/Miaoywww/Minecraft-Media-Player.git
```

Install required libraries

```
pip install -r requirements.txt
```

**If you need process the videos, please install opencv manually, because opencv is too big, I didn't put it to
requirements.txt.**

```
pip install opencv-python
```

## Usage

> `/` is required, and I suggest put the files to be processed into `main/`

```
# Process to images
python3 images.py ./cat.jpg

# Process to videos
python3 videos.py ./video.mp4
```

After running, find your datapack in `functions/`

## License

Copyright Miaomiaoywww 2022.

Distributed under the terms of the [MIT license](https://github.com/Miaoywww/Minecraft-Media-Player/blob/main/LICENSE).
