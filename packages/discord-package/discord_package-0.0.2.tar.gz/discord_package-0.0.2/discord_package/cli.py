# discord-package/discord_package/cli.py
import os
import sys

def create_project(project_name):
    # Obtener el directorio actual de trabajo
    current_directory = os.getcwd()
    
    # Crear el directorio del nuevo proyecto
    project_directory = os.path.join(current_directory, project_name)

    try:
        # Crear directorios principales y archivos
        os.makedirs(project_directory)
        print(f"Proyecto '{project_name}' creado en {project_directory}")

        # Estructura de directorios y archivos
        directories = [
            'commands',
            'utils',
            'functions',
            'buttons',
            'logs',
            'config'
        ]
        
        files = [
            # Comandos
            ('commands', '__init__.py', ''),
            ('commands', 'ping.py', """
import discord
from discord.ext import commands
from buttons.buttons_help import ButtonsHelp

async def ping_layout(interaction, latency):
    try:
        await interaction.response.send_message(f"{interaction.user.mention} {latency} ms / Pong!", ephemeral=True, view=ButtonsHelp())
    except Exception as e:
        return e
"""),
            
            # Utils
            ('utils', '__init__.py', ''),
            ('utils', 'error_message.py', """
import discord
from buttons.buttons_help import ButtonsHelp
from datetime import datetime

async def error_message(e, interaction, msg):
    try: 
        embed = discord.Embed(
            title="We had a problem ⚠️",
            description=f"An error occurred while executing the 😢 command. Don't worry, it's not your fault, we are working to fix the problem as soon as possible ⚒️."
        )
        
        embed.add_field(
            name=" ",
            value="●▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬●",
            inline=False)
        
        embed.add_field(
            name="Error description: ",
            value=f"{msg}",
            inline=False)
        
        embed.add_field(
            name=" ",
            value="●▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬●",
            inline=False)
        
        embed.set_image(
                url="https://nftplazas.com/wp-content/uploads/2024/06/lumittera-gameplay.png"
            )
        
        embed.color = 0x0fffff
        await interaction.response.send_message(embed=embed, ephemeral=True, view=ButtonsHelp())
        print(f"Este es el error: {str(e)}")
        
        # Registrar el error en el archivo de log
        await log_error(interaction, e, msg)

    except Exception as e:
        print(f"Ocurrio un error al enviar el mensaje de error: {str(e)}")

async def log_error(interaction, error, custom_message):
    log_file = 'logs/errors_logs.txt'
    try:
        with open(log_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = interaction.user
            user_info = f"{user.name}#{user.discriminator} (ID: {user.id})"
            guild = interaction.guild.name if interaction.guild else "Direct Message"
            channel = interaction.channel.name if interaction.guild else "DM"
            roles = ", ".join([role.name for role in user.roles]) if interaction.guild else "No Roles"

            error_entry = (f"| {timestamp} | {user_info} | {guild} | {channel} | "
                           f"{interaction.message.id if interaction.message else 'N/A'} | "
                           f"{roles} | {str(error)} | {custom_message} |\n")
            f.write(error_entry)

    except Exception as e:
        print(f"Error al registrar el error en el log: {e}")
"""),
            
            # Funciones
            ('functions', '__init__.py', ''),
            ('functions', 'print_commands_logs.py', """
from datetime import datetime

async def log_command_usage(interaction, command_name):
    log_file = 'logs/commands_logs.txt'
    try:
        with open(log_file, 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = interaction.user
            user_info = f"{user.name}#{user.discriminator} (ID: {user.id})"
            guild = interaction.guild.name if interaction.guild else "Direct Message"
            channel = interaction.channel.name if interaction.guild else "DM"
            roles = ", ".join([role.name for role in user.roles]) if interaction.guild else "No Roles"

            log_entry = f"| {timestamp} | {user_info} | {guild} | {channel} | {command_name} |\n"
            f.write(log_entry)

    except Exception as e:
        print(f"Error al registrar el comando en el log: {e}")
"""),
            
            # Botones
            ('buttons', '__init__.py', ''),
            ('buttons', 'buttons_help.py', """
import discord

discord_url = "https://discord.com/invite/q3P5hjqsuE"
website_url = "https://lumiterra.net"
docs_url = "https://docs.lumiterra.net/docs"
oficial_guide_url = "https://lumiterra.notion.site/Ronin-LumiTerra-Game-Guide-ff7923da552242139c9e44bbec4df8e4"
unoficial_guide_url = "https://docs.lumiterra.net/docs/unofficial-guide" #no setup
download_url = "https://lumiterra.itch.io/game"
twitter_url = "https://x.com/lumiterragame"

class ButtonsHelp(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.add_item(
            discord.ui.Button(label="Oficial Discord",
                              url=discord_url,
                              style=discord.ButtonStyle.url))
        self.add_item(
            discord.ui.Button(label="Oficial Twitter",
                              url=twitter_url,
                              style=discord.ButtonStyle.url))
        self.add_item(
            discord.ui.Button(label="Oficial Web",
                              url=website_url,
                              style=discord.ButtonStyle.url))
      
"""),
            
            # Logs
            ('logs', '__init__.py', ''),
            ('logs', 'commands_logs.txt', ''),
            ('logs', 'errors_logs.txt', ''),
            
            # Config
            ('config', '__init__.py', ''),
            ('config', 'bot_config.py', """
# Configuración del bot

TOKEN = 'YOUR_TOKEN_HERE'
"""),
            
            # Gitignore
            ('', '.gitignore', """
    config
    config.py             
"""),
            
            # requirements.txt
            ('', 'requirements.txt', """
discord.py
watchdog
asyncio
datetime
requests
rich
"""),
           
           
            # dev.py     
            ('', 'dev.py', """
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.progress import Progress
from rich import print
import subprocess
import time
import os
import signal

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.last_modified = time.time()
        self.console = Console()

    def on_any_event(self, event):
        current_time = time.time()
        if current_time - self.last_modified > 5:  # Espera 5 segundos para evitar ejecuciones múltiples
            self.restart_process()
            self.last_modified = current_time

    def restart_process(self):
        if self.process:
            self.console.print("[bold red]Stopping the current process...[/bold red]")
            with Progress() as progress:
                task = progress.add_task("[cyan]Stopping...", total=100)
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.02)
            self.process.terminate()  # Terminar el proceso en Windows
            self.process.wait()  # Esperar a que termine
            self.console.print("[bold red]Process stopped.[/bold red]")

        self.console.print(f"[bold green]Running command:[/bold green] [italic yellow]{self.command}[/italic yellow]")
        with Progress() as progress:
            task = progress.add_task("[cyan]Starting...", total=100)
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.02)
        self.process = subprocess.Popen(self.command, shell=True)  # Iniciar el proceso en Windows
        self.console.print("[bold green]Process started successfully![/bold green]")

if __name__ == "__main__":
    path = "../lumiterra-bot"  # Directorio a monitorear
    command = "python bot.py"  # El comando para ejecutar tu bot

    event_handler = ChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        with Console().status("[bold green]Monitoring for changes...[/bold green]") as status:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        Console().print("[bold red]Monitoring stopped by user.[/bold red]")
    observer.join()


"""),
           
            
            # bot.py
            ('', 'bot.py', """
# Importar módulos necesarios
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from config.bot_config import TOKEN
from utils.error_message import error_message
from commands.ping import ping
from functions.print_commands_logs import log_command_usage

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Evento de inicio del bot
@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f'{bot.user} se ha conectado a Discord!')
    except Exception as e:
        print(e)

# Comando de ping
@bot.tree.command(name="ping", 
                  description="Ping the bot")
async def ping_command(interaction: discord.Interaction):
    try:
        await ping(interaction, round(bot.latency * 1000))
        await log_command_usage(interaction, "ping")  # Registrar el uso del comando
    except Exception as e:
        await error_message(e,
                            interaction,
                            f"Command ping [{e}]")

bot.run(TOKEN)
""")
        ]

        # Crear directorios
        for directory in directories:
            dir_path = os.path.join(project_directory, directory)
            os.makedirs(dir_path)
            print(f"Directorio '{dir_path}' creado.")

        # Crear archivos y añadir contenido
        for file_dir, file_name, content in files:
            file_path = os.path.join(project_directory, file_dir, file_name)
            with open(file_path, 'w') as f:
                f.write(content)  # Añade contenido al archivo
            print(f"Archivo '{file_path}' creado con contenido.")

        print("Estructura de proyecto creada con éxito.")

    except Exception as e:
        print(f"Error al crear el proyecto: {e}")

def main():
    if len(sys.argv) < 3:
        print("Uso: dcp create <nombre_del_proyecto>")
        sys.exit(1)

    command = sys.argv[1]
    if command == "create":
        project_name = sys.argv[2]
        create_project(project_name)
    else:
        print(f"Comando desconocido: {command}")

if __name__ == "__main__":
    main()
