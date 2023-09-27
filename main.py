import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks
from db import DbStruct,BotDb
from icecream import ic
import os
from io import BytesIO

session = BotDb().session
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

def create_embed(title: str, content: str, color: discord.Color):
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name=content, value="")
    print(type(embed))
    return embed



@bot.event
async def on_ready():
    print("Ready")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command[s]")
    except Exception as e:
        print(e)


@bot.event
async def on_message(message:discord.Message):
    if isinstance(message.channel,discord.DMChannel):
        for count,resource in enumerate(message.attachments,0):
            if len(message.content) > 0:
                resource_name = os.path.splitext(resource.filename)[0]
            else:
                resource_name = message.content.strip()
            file_ext = os.path.splitext(resource.filename)[1]
            ic(message.attachments)
            file_bytes = await message.attachments[0].read()
            ic(type(file_bytes))
            file = DbStruct.Resources(member_id=message.author.id,member_name=message.author.name,resource_name=resource_name,resource_file=file_bytes,file_ext=file_ext)
            session.add(file)
            session.commit()
            embed = create_embed("Success","Resource Saved",color=discord.Color.green())
            await message.channel.send(embed=embed)

@bot.tree.command(name="save_resource_text")
@app_commands.describe(resource_name="resource name or an easy to search name",resource="Only if resource is not a file")
async def save_resource(interaction: discord.Interaction,resource_name:str,resource:str):
    resources = session.query(DbStruct.Resources).all()
    if resources:
        for saved_resource in resources:
            if saved_resource.resource_name == resource_name:
                embed = create_embed(title="resource name is already used", content="use another name or check if its the same resource",color=discord.Color.red())
                await interaction.response.defer()
                await interaction.followup.send(embed=embed, ephemeral=True)
                return 0

    print(type(resource))
    resource = DbStruct.Resources(member_id=interaction.user.id,member_name=interaction.user.name,resource_name=resource_name,resource_url=resource)
    session.add(resource)
    session.commit()
    embed = create_embed(title="Success", content="Resource Saved",color=discord.Color.green())
    await interaction.response.defer()
    await interaction.followup.send(embed=embed,ephemeral=True)


@bot.tree.command(name="save_resource_file")
async def save_resource_file(interaction:discord.Interaction):
    await interaction.response.defer()
    embed = create_embed("Not Here","DM me with the file and caption it with the resource name (resource name can be anything,you have to send the resource name in the same message as the file)",color=discord.Color.yellow())
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="search_resource")
@app_commands.describe(resource="resource name or an easy to search name")
@app_commands.choices(
   resource=[app_commands.Choice(name=x.resource_name,value=1) for x in session.query(DbStruct.Resources).all()]
)
async def search_resource(interaction:discord.Interaction,resource:app_commands.Choice[int]):
    item:DbStruct.Resources = session.query(DbStruct.Resources).filter(DbStruct.Resources.resource_name == resource.name).first()
    if item:
        try:
            binary_data =item.resource_file
            data_stream = BytesIO(binary_data)

            # Create a discord.File object from the BytesIO object
            file = discord.File(data_stream, filename=item.resource_name.strip().replace(" ","_"))
            embed = create_embed("Success",f"**Attachment**:__{item.resource_name}{item.file_ext}__\n**Submission_date**:__{item.submittion_date}__",color=discord.Color.green())
            await interaction.response.defer()
            await interaction.followup.send(embed=embed,file=file)
        except Exception as e:
            embed = create_embed("Error",str(e),discord.Color.red())
            await interaction.response.defer()
            await interaction.followup.send(embed=embed)
    else:
        embed = create_embed("Error","404 File Not Found", discord.Color.red())
        await interaction.response.defer()
        await interaction.followup.send(embed=embed)


bot.run("TOKEN")