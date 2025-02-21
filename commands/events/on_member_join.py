from discord import Member

async def member_join(member: Member):
    await member.create_dm()
    await member.dm_channel.send(
        f"Hola {member.name}, bienvenido al servidor {member.guild.name}."
    )