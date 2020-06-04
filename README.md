
# Bunkbot

![bunkbot](https://github.com/fugwenna/bunkbot/blob/docs/readme/avatar.png)

<br/>  <sup>(credit [Christine Schlotter](http://christineschlotter.com))</sup>

  

## Overview

The bunkest of bots, first of his name. Bunkbot is a small sandbox discord bot meant for privately run servers who want a strange sandbox bot to run and customize for fun.

## Prerequisites:
**Required**:   
Python 3.6 or higher
<br/> PIP (v3)

_Optional_: <br />
Many of Bunkbot's features use (free) API accounts. Bunkbot will still load without these accounts, but will not support the functions that require them. Below are the APIs Bunkbot uses:
- Discord: [Developer Account](https://discord.com/developers/applications)
- Chat: [Cleverbot](https://cleverbot.io/)
- Weather: [Open Weather](https://openweathermap.org/api)
- Gif Responses: [Tenor](https://tenor.com/gifapi/documentation)
  

## Setup
Running Bunkbot's setup will provide a `config.json` at the root of the project. You may opt for defaults and come back to edit the configuration file manually later.

**Linux/OSX**
At a terminal, run: 
```bash
sh setup.sh
```
  
**Windows**
  In a command prompt or terminal, run:  
  ```
  pip install -r requirements.txt && python -m src.setup.setup
  ```
  
 ## Running the bot
Once the setup is complete, the bot is ready. Run `python3 main.py` at the root of the project to boot Bunkbot.
