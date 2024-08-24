# discord-package/discord_package/cli.py
import os
import sys

def create_project(project_name):
    # Obtener el directorio actual de trabajo
    current_directory = os.getcwd()
    
    # Crear el directorio del nuevo proyecto
    project_directory = os.path.join(current_directory, project_name)

    try:
        os.makedirs(project_directory)
        print(f"Proyecto '{project_name}' creado en {project_directory}")
        
        # Crear archivos básicos para el bot de Discord
        with open(os.path.join(project_directory, 'bot.py'), 'w') as f:
            f.write("""import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run('YOUR_TOKEN_HERE')
""")
        print("Archivo base 'bot.py' creado.")
        
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
