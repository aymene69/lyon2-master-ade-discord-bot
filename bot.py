import discord, asyncio, pytz
from discord import app_commands
from discord.ext import tasks
from discord.ext.paginators.button_paginator import ButtonPaginator, PaginatorButton

import get_cours
from utils import download_file, translate_day_to_french

from get_cours import get_events_for_today, get_events_for_tomorrow, get_next_event, clean_description, get_events_for_next_30_days
from dotenv import dotenv_values

config = dotenv_values(".env")
CHANNEL_ID = 1282794736805216299
SERVER_ID = 1282794736805216296
paris_tz = pytz.timezone('Europe/Paris')
notified_events = set()

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

intents = discord.Intents.all()
intents.members = True
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Client connecté en tant que {client.user}')
    print(f'Version 1.0.0')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" les emplois du temps"))
    await client.tree.sync()
    print("Commandes synchronisées")
    ics_update.start()
    print("Taches lancées")

@client.tree.command()
async def status(interaction: discord.Interaction):
    """Permet de savoir si le bot répond bien."""
    await interaction.response.send_message("✅")

@client.tree.command()
@app_commands.describe(menu='Le numéro de votre menu. (exemple: "4" pour le menu 4)')
@app_commands.describe(temps="Choisissez entre 'Aujourd'hui' et 'Demain'")
@app_commands.choices(temps=[
    app_commands.Choice(name="Aujourd'hui", value="1"),
    app_commands.Choice(name="Demain", value="2")
])
@app_commands.choices(menu=[
    app_commands.Choice(name="Menu 1", value="1"),
    app_commands.Choice(name="Menu 2", value="2"),
    app_commands.Choice(name="Menu 3", value="3"),
    app_commands.Choice(name="Menu 4", value="4"),
])
async def planning(interaction: discord.Interaction, temps: str, menu: str):
    """Affiche le planning de la journée, du lendemain, de la semaine actuelle ou de la semaine prochaine en fonction du menu"""
    try:
        if temps == "1":
            events = get_events_for_today(int(menu) - 1)
            embed_title = "Planning du jour"
            embed_color = discord.Color.blue()
        elif temps == "2":
            events = get_events_for_tomorrow(int(menu) - 1)
            embed_title = "Planning de demain"
            embed_color = discord.Color.green()
        else:
            await interaction.response.send_message("Veuillez entrer '1' pour aujourd'hui ou '2' pour demain.")
            return

        if not events:
            await interaction.response.send_message(f"Aucun événement trouvé pour le jour sélectionné avec le menu {menu}.")
            return

        embed = discord.Embed(
            title=embed_title,
            description=f"Voici les cours pour {embed_title.lower()}",
            color=embed_color
        )

        for event in events:
            event_info = (
                f"**Heure**: {event['heure']} - {event['end']}\n"
                f"**Salle**: {event['location']}\n"
                f"**Description**: {clean_description(event['description']) if event.get('description') else 'Pas de description'}"
            )
            embed.add_field(name=event['name'], value=event_info, inline=False)

        embed.set_footer(text=f"Nombre total de cours : {len(events)}. Bot par @aymene")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Erreur",
            description=f"Une erreur est survenue : {e}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)




@client.tree.command()
@app_commands.describe(menu='Le numéro de votre menu.')
@app_commands.choices(menu=[
    app_commands.Choice(name="Menu 1", value="1"),
    app_commands.Choice(name="Menu 2", value="2"),
    app_commands.Choice(name="Menu 3", value="3"),
    app_commands.Choice(name="Menu 4", value="4"),
])
async def prochain(interaction: discord.Interaction, menu: str):
    """Affiche le prochain cours en fonction du menu choisi"""
    try:
        prochain = get_next_event(int(menu) - 1)

        if not prochain:
            embed = discord.Embed(
                title="Aucun cours trouvé",
                description="Il semble qu'il n'y ait pas de prochain cours disponible pour ce menu.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            title=f"Prochain Cours : {prochain['name']}",
            description=f"Le {prochain['date']}",
            color=discord.Color.red()
        )

        embed.add_field(name="Heure", value=f"{prochain['heure']} - {prochain['end']}", inline=True)
        embed.add_field(name="Salle", value=prochain['location'], inline=True)

        description = prochain.get('description', "Pas de description")
        embed.add_field(name="Description", value=clean_description(description), inline=False)

        embed.set_footer(text="Prochain cours à venir. Bot par @aymene")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Erreur",
            description=f"Une erreur est survenue : {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)


@client.tree.command()
@app_commands.describe(menu='Le numéro de votre menu.')
@app_commands.choices(menu=[
    app_commands.Choice(name="Menu 1", value="1"),
    app_commands.Choice(name="Menu 2", value="2"),
    app_commands.Choice(name="Menu 3", value="3"),
    app_commands.Choice(name="Menu 4", value="4")
])
async def edt(interaction: discord.Interaction, menu: str):
    """Affiche les cours pour les 30 prochains jours en fonction du menu choisi"""
    events_30_days = get_events_for_next_30_days(int(menu)-1)

    embeds = []
    for day in events_30_days:
        description_lines = []
        for event in day['events']:
            name = event.get('name', 'Pas de nom')
            heure = event.get('heure', 'Heure non spécifiée')
            end = event.get('end', 'Fin non spécifiée')
            description = event.get('description', 'Pas de description')
            location = event.get('location', 'Emplacement non spécifié')
            if name == "Aucun cours":
                description_lines.append(
                    f"Aucun cours ce jour"
                )
            else:
                description_lines.append(
                    f"**{name}**\n**Heure**: {heure} - {end}\n**Salle**: {location}\n**Description**: {description}\n"
                )

        description = "\n".join(description_lines) if description_lines else "Pas cours ce jour."

        embed = discord.Embed(
            title=f"{translate_day_to_french(day['day_name'])} ({day['date']})",
            color=discord.Color.green()
        )

        embed.add_field(name="Cours du jour:", value=description, inline=False)
        embeds.append(embed)

    paginator = ButtonPaginator(embeds, author_id=interaction.user.id, buttons={
        "PAGE_INDICATOR": None,
        "RIGHT": PaginatorButton(label="Jour suivant"),
        "LEFT": PaginatorButton(label="Jour précédent"),
        "FIRST": None,
        "LAST": None,
        "STOP": PaginatorButton(label="Arrêter", row=2, style=discord.ButtonStyle.danger)}, add_page_string=False)
    await paginator.send(interaction)


@tasks.loop(hours=1)
async def ics_update():
    for i, menu_url in enumerate(get_cours.menus, start=1):
        await download_file(menu_url, f"menu{i}.ics")
        await asyncio.sleep(5)

client.run(config['TOKEN'])
