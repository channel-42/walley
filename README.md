
# walley ![](https://img.shields.io/badge/Version-1.0-green.svg) ![](https://img.shields.io/badge/License-MIT-orange.svg) 

<p align="center">A reddit wallpaper/image downloader</p>

<img align="left" border="0" padding="4" src="https://github.com/channel-42/walley/blob/master/.resources/walley_logo.svg" width="30%">
<img align="right" src="https://via.placeholder.com/700x500" width="60%">

<br><br><br><br><br><br><br><br>

# installation 

#### with pip

`pip install walley`

#### manual install

```bash
git clone https://github.com/channel-42/walley.git
cd walley
cp walley.py $HOME/.local/bin/walley
chmod +x $HOME/.local/bin/walley
```

#### troubleshooting
Should you get the error `command not found: walley`, restart your terminal. Should the error persist, check that `$HOME/.local/bin` is in your `$PATH`. This can be done by adding `export PATH="$HOME/.local/bin:$PATH"` to your .bashrc/.zshrc.

# usage
Run the program by typing ’walley’ into a terminal of your choice and walley will take care of the rest. 

# configuration
When running walley for the first time, a config will automatically be created in your user's XDG config directory (i.e. .config).

The config is written in json.

#### You can configure the following parameters:

- subreddit		
- download limit			(maximum of 200)
- minimum resolution	(FHD, 2K, WQHD, 4K)
- download directory 	
- nfsw filtering

Example config:
```json
{
	"subreddit": 	"wallpapers",
	"limit":	"10",
	"resolution":	"4K",
	"directory":	"~/Pictures",
	"allow_nsfw":	False
}
```

