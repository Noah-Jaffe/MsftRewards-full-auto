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
   - This or That
  - Logs daily points
  - Comprehensive run logs
  - Print to log if script update is available
  
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

## Instructions

1. Run `auto.py`
   - `python auto.py`
2. Wait until it prints that its done
   - You should be able to move or rezise the edge window while it is running without anything breaking.

## ALTERNATIVE:
An alternative method is to use the [Simple.html](Simple.html) file, [can be viewed without need for download here](https://raw.githack.com/Noah-Jaffe/MsftRewards-full-auto/main/Simple.html). This is good to use if you cant run the python but perhaps want to do the tasks quickly from your phone.

 - Instructions:
   - **ENABLE POPUP WINDOWS WHEN ASKED, SO THAT IT CAN OPEN NEW SEARCHES IN NEW TABS!**
   - This is a simple html file that enables you to open all of the searches for the browsers mode (desktop/mobile) with one click.
   - Buttons:
     - `👁👅👁` --> opens all of the searches (in new tabs, all at once) (make sure popups enabled).
     - `1️⃣` --> opens a single search in a new tab.
     - `💰` --> opens rewards page in new tab [https://rewards.bing.com/](https://rewards.bing.com/)
     - `📊` --> opens points breakdown in new tab [https://rewards.bing.com/pointsbreakdown](https://rewards.bing.com/pointsbreakdown)
   - **You will have to do the tasks by hand!**
    


## FAQ:
### Q: Help, I don't really understand how to use this or what I am supposed to do.
A: Try googling the terms you are not familiar with, if that does not help answer your question, just open an issue/discussion so I can update stuff to be easier to understand.

### Q: Y code so ugly?
A: Quick and dirty solution, also who knows how long this will work for so ¯\\\_(ツ)\_/¯


## Protips:
You can create a scheduled task that runs the auto.py automatically. I reccomend some form of trigger that matches your computer usage. I reccomend once daily, or on login. 
