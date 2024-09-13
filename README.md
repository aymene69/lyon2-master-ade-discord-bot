# Lyon 2 Master ADE Discord Bot

This Discord bot helps manage and display schedules based on different menus. It offers commands to display the events of the day, tomorrow, the next 30 days, and the next upcoming class. The bot is designed to notify users in advance of upcoming classes and uses the Discord API through the `discord.py` library.

## Features

- **/status**: Checks if the bot is responding correctly.
- **/planning**: Displays the schedule for today or tomorrow based on the selected menu.
- **/prochain**: Displays the next class based on the selected menu.
- **/edt**: Displays the classes for the next 30 days based on the selected menu.

## Configuration

### Prerequisites

Make sure to install the following dependencies:

- Python 3.8 or higher
- Python libraries listed in `requirements.txt`:

```bash
discord.py
arrow
requests
pytz
ics
aiohttp
aiofiles
discord-py-paginators
python-dotenv
```

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/discord-bot-schedule.git
cd discord-bot-schedule
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Edit the .env file with your Discord token, and the 4 menus ADE URL then rename it ".env"

```bash
mv .env.example .env
```

4. Run the bot:

```bash
python bot.py
```

## Available Commands
`/status`
  - **Description**: Verifies that the bot is operational.
  - **Usage**: /status

`/planning`
  - **Description**: Displays the schedule for today or tomorrow based on the menu.
  - **Usage**: /planning temps:[Aujourd'hui | Demain] menu:[Menu 1 | Menu 2 | Menu 3 | Menu 4]

`/prochain`
  - **Description**: Displays the next class based on the selected menu.
  - **Usage**: /prochain menu:[Menu 1 | Menu 2 | Menu 3 | Menu 4]
`/edt`
  - **Description**: Displays the classes for the next 30 days based on the selected menu.
  - **Usage**: /edt menu:[Menu 1 | Menu 2 | Menu 3 | Menu 4]

## Background Tasks
`ics_update`: 
- Automatically updates the .ics files containing the schedules every hour.

## Development
To add new features or fix bugs, modify the bot.py file. Don’t forget to sync the commands after making changes with the client.tree.sync() command.


## License
This project is licensed under the Apache 2.0. See the LICENSE file for more details.
