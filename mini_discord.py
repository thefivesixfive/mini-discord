# mini discord bot
from discord.ext import commands
from discord import Embed
from dotenv import load_dotenv
from os import getenv
from mini_discord_api import MiniDiscordServerManager

# bot
bot = commands.Bot(command_prefix="=")
mdsm = MiniDiscordServerManager()
load_dotenv()
TOKEN = getenv('TOKEN')

# log
def log(text):
    logmsg = f"[/] {text}"
    print(logmsg)
    with open("botlogs.txt", "a+") as file:
        file.write(logmsg+"\n")

# init
@bot.event
async def on_start():
    log(f'Connected to Discord!')

# make server
@bot.command(name="make")
async def make_server(ctx, *args):
    # make server
    name = ' '.join(args)
    id=mdsm.__create_server__(ctx.author.id, name)
    # return id
    await ctx.send(f'Server created! The ID is {id}')

# delete server
@bot.command(name="nuke")
async def delete_server(ctx, arg):
    result = mdsm.__delete_server__(ctx.author.id, arg)
    # nuke server
    if result:
        await ctx.send('Server deleted!')
    elif result == None:
        await ctx.send('There is no server by that ID!')
    else:
        await ctx.send('You do not own that server!')

# get server info
@bot.command(name="myservers")
async def tell_servers(ctx):
    # grab info
    servers=mdsm.__server_info__(ctx.author.id)
    # if no owned
    if servers == {}:
        await ctx.send('You don\'t own any MiniDiscord servers!')
    # otherwise
    else:
        for id,server_data in servers.items():
            server_info = Embed(title=server_data['name'],description='')
            server_info.add_field(name='ID', value=id, inline=False)        
            server_info.add_field(name='Owned by', value=await bot.fetch_user(server_data['owner']))
            server_info.add_field(name='MiniDiscord Verified', value=server_data['verified'])
            # Generate Member List
            member_list = ""
            for member in server_data['members']:
                member_list+=str(await bot.fetch_user(member))+'\n'
            server_info.add_field(name='Members', value=member_list, inline=False)
            # send embed
            await ctx.send(embed=server_info)

# get all servers
@bot.command(name="browse")
async def browse_servers(ctx):
    server_list = mdsm.__servers__()
    # make embed
    browser = Embed(title="All Servers")
    for id,server in server_list.items():
        # advertisement
        ad = f"{server['name']} | {len(server['members'])} Members"
        browser.add_field(name=ad, value=id, inline=False)
    # send embed
    await ctx.send(embed=browser)

# join
@bot.command(name="join")
async def join_server(ctx, arg):
    # try to join
    if mdsm.__server_attatchment__(ctx.author.id, arg, True):
        await ctx.send(f"Joined {mdsm.__servers__()[arg]['name']}\nType `=leave <id>` to leave!")
    # error
    else:
        await ctx.send("That server doesn't exist!")

# leave
@bot.command(name="leave")
async def leave_server(ctx, arg):
    # try to join
    if mdsm.__server_attatchment__(ctx.author.id, arg, False):
        await ctx.send(f"Left {mdsm.__servers__()[arg]['name']}\nType `=join {arg}` to re-join!")
    # error
    else:
        await ctx.send("That server doesn't exist!")

# send message
@bot.command(name="send")
async def send_message(ctx, *args):
    # check for server
    if not args[0] in mdsm.__servers__().keys():
        # send message and quit
        await ctx.send(f"There's no such server with the ID {args[0]}")
        return
    # otherwise
    else:
        # generate message
        msg = ' '.join(args[1:])
        to_ping = mdsm.__send_message__(ctx.author.id, args[0], msg)
        # ping everyone in the server
        server_data = mdsm.__servers__()[args[0]]
        for member_id in to_ping:
            member = await bot.fetch_user(member_id)
            # prepare ping embed
            message = Embed(title=server_data['name'],description='New ping!')
            message.add_field(name='Author', value=member.display_name, inline=False)        
            message.add_field(name='Message', value=msg, inline=False)
            # send
            await member.send(embed=message)

# return all messages
@bot.command(name="allmsgs")
async def all_server_messages(ctx, arg):
    #  check for server
    if not arg in mdsm.__servers__().keys():
        # send message and quit
        await ctx.send(f"There's no such server with the ID {arg}")
        return
    # else
    else:
        # return all messages
        server_data = mdsm.__servers__()[arg]
        message_list = Embed(title=server_data['name'],description='All messages')
        # grab all the messages
        for message in server_data['messages']:
            # prepare ping embed
            author_name = await bot.fetch_user(message['sender'])
            description = f"{author_name} sent the message\n{message['id']} is the ID"
            message_list.add_field(name=message['text'], value=description)
        # send
        await ctx.send(embed=message_list)
# run
if __name__ == '__main__':
    bot.run(TOKEN)