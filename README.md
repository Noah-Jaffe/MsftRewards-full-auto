# MsftRewards-full-auto
Microsoft Rewards automation

## Features:
 - PC searches
 - Mobile searches
 - Edge Exclusive Searches
 - Quests and punch cards
 - Daily Sets and other Activities
   - Simple redirect
   - Regular searches
   - Multiple choice (in page/embedded)
   - Multiple/multi choice (overlay)
   - Poll (overlay)
  - Logs daily points
  
## Requirements:
 - Python packages:
   - [selenium](https://pypi.org/project/selenium/)
   - [tqdm](https://pypi.org/project/tqdm/)
 - System:
   - Windows 10 *(Tbh idk, this might work on linux based with just changing some of the configurables, idk)*


## Installation
- Install requirements
  - `pip install selenium, tqdm`
- Update/Verify the configurable variables. They can be found at the top of the `auto.py` file after the imports.

| Variable | Comment | Default |
|---|---|---|
| `MAX_WEBDRIVER_WAIT` | Max wait time in seconds before it times out and tries to reload the page. <br>Useful for when bing gets slow. | 100 |
| `EDGE_EXE_PATH` | Full path to your edge executable file.<br>This might need to be changed before running. | "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" |
| `EDGE_PROFILE_DIR` | Directory of the profile to use. <br>**BE SURE IT HAS AUTO-LOGIN/PASSWORD SAVING ENABLED**<br>This might need to be changed before running. | "C:\\Users\\{`os.getlogin()`}\\AppData\\Local\\Microsoft\\Edge\\User Data" |
| `EDGE_PROFILE_NAME` | Edge profile name.<br>This might need to be changed before running. | "Default" |
| `MAX_SEARCH_POINTS['mobile']` | Should be universal, but if it ever needs changing ¯\\\_(ツ)\_/¯ | 100 |
| `MAX_SEARCH_POINTS['desktop']` | Should be universal, but if it ever needs changing ¯\\\_(ツ)\_/¯ | 150 |
| `POINTS_PER_SEARCH` | Should be universal, but if it ever needs changing ¯\\\_(ツ)\_/¯ | 5 |

## Instructions

1. Run `auto.py`
   - `python auto.py`
3. Wait until it prints that its done
   - You should be able to move or rezise the edge window while it is running without anything breaking.


## FAQ:
### Q: Help, I don't really understand how to use this or what I am supposed to do.
A: Try googling the terms you are not familiar with, if that does not help answer your question, just open an issue so I can update stuff to be easier to understand.

### Q: Y code so ugly?
A: Quick and dirty solution, also who knows how long this will work for so ¯\\\_(ツ)\_/¯


## Protips:
You can create a scheduled task that runs the auto.py automatically. I reccomend some form of trigger that matches your computer usage. I reccomend once daily, or on login. 
