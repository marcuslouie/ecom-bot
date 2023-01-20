import json

import discord
import discord.ui
from discord.ext import commands

from inventorymanager import Invmanager as IM


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # Change command prefix to preference
        super().__init__(command_prefix=".", intents=discord.Intents.all())

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)


bot = Bot()


def change_status(order_id, status):
    inventory = IM().order_data()
    inventory[order_id]['status'] = str(status)
    with open('orders.json', 'w') as f:
        json.dump(inventory, f)

# --------------
# BUTTON CLASSES
# --------------
# Accept buttons


class Accept(discord.ui.View):
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        change_status(order_id, 'Approved')
        await interaction.response.edit_message(view=Acceptd())
        inventory = IM().order_data()
        orderer = await bot.fetch_user(inventory[order_id]["orderer"])
        await orderer.send('Your order has been accepted')

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        change_status(order_id, 'Declined')
        await interaction.response.edit_message(view=Acceptd())
        inventory = IM().order_data()
        orderer = await bot.fetch_user(inventory[order_id]["orderer"])
        await orderer.send('Your order has been declined')

# Accept buttons (disabled)


class Acceptd(discord.ui.View):
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, disabled=True)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        disabled = True

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, disabled=True)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        disabled = True

# Delivery buttons


class Delivery(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=604800)

    @discord.ui.button(label="Yes, I have recieved my delivery", style=discord.ButtonStyle.green)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=Deliveryd())
        change_status(order_id, 'Delivered (Confirmed)')

    @discord.ui.button(label="No, I have not received my delivery", style=discord.ButtonStyle.red)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=Nevermind())
        change_status(order_id, 'Exception (Undelivered)')

    async def on_timeout(self):
        inventory = IM().order_data()
        orderer = await bot.fetch_user(inventory[order_id]["orderer"])
        await orderer.send('Since you have not replied, we’ll take it that your order has been delivered. Enjoy!')
        change_status(order_id, 'Delivered (7d no response)')

# Delivery buttons (disabled)


class Deliveryd(discord.ui.View):
    @discord.ui.button(label="✅", style=discord.ButtonStyle.green, disabled=True)
    async def menu1(self, interaction: discord.Interaction, button: discord.ui.Button):
        disabled = True

    @discord.ui.button(label="No, I have not recieved my delivery", style=discord.ButtonStyle.red, disabled=True)
    async def menu2(self, interaction: discord.Interaction, button: discord.ui.Button):
        disabled = True

# Reconfirmation button


class Nevermind(discord.ui.View):
    @discord.ui.button(label="Nevermind, I've received my delivery", style=discord.ButtonStyle.green)
    async def menu3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content='Sent!', view=Nevermindd())
        change_status(order_id, 'Delivered (Confirmed)')

# Reconfirmation button (disabled)


class Nevermindd(discord.ui.View):
    @discord.ui.button(label="✅", style=discord.ButtonStyle.green, disabled=True)
    async def menu4(self, interaction: discord.Interaction, button: discord.ui.Button):
        disabled = True

# ---------
# COMMANDS
# ---------


@bot.hybrid_command(name="stock", with_app_command=True, description="Displays all products")
async def stock(ctx: commands.Context):
    inventory = IM().stock_data()
    x = []
    for product in inventory:
        string = f'{inventory[product]["name"]} - ID: {product} | Price: ${inventory[product]["price"]}\n'
        x.append(string)
    s = ""
    for item in x:
        s += item
    emb = discord.Embed(colour=discord.Colour.blue(),
                        title=f'Stock', description=s
                        )
    await ctx.send(embed=emb)


@bot.hybrid_command(name="info", with_app_command=True, description="Displays relevent product information")
async def info(ctx: commands.Context, product_id):
    product = str(product_id).title()
    inventory = IM().stock_data()
    if product in inventory:
        emb = discord.Embed(colour=discord.Colour.blue(),
                            title=str(inventory[product]["name"]).title(),
                            url=inventory[product]["link"])
        emb.add_field(name=str(f'Stock:'), value=str(
            inventory[product]["stock"]), inline=False)
        emb.add_field(name=str(f'Price:'),
                      value=f'${inventory[product]["price"]}', inline=True)
        emb.add_field(name=str(f'MSRP:'),
                      value=f'${inventory[product]["MSRP"]}', inline=True)
        try:
            emb.set_thumbnail(url=str(inventory[product]["photo"]))
        except:
            pass
        await ctx.send(embed=emb)
    else:
        await ctx.send("This product doesn't exist, check your spelling and try again!")


@bot.hybrid_command(name="order", with_app_command=True, description="Order a product")
async def order(ctx: commands.Context, product_id: str, quantity: int):
    inventory = IM().stock_data()
    if product_id.title() in inventory:
        global order_id
        order_id = IM().create_order(product_id, quantity, int(ctx.author.id))
        # <-- Input user ID of admin user (currently TL#0001)
        admin = await bot.fetch_user(313835891669991425)
        view = Accept()
        await ctx.reply(f'Your order number is: {order_id}')
        await admin.send(f'{ctx.author} has made an order.\nOrder ID: {order_id}')
        await admin.send(view=view)
    else:
        await ctx.reply(f"This product doesn't exist, check your spelling and try again!")


@bot.hybrid_command(name="status", with_app_command=True, description="Check the status of an order")
async def status(ctx: commands.Context, order_id: str):
    inventory = IM().order_data()
    if order_id in inventory:
        emb = discord.Embed(colour=discord.Colour.blue(),
                            title=f'Order #: {order_id}',
                            )
        emb.add_field(name=str(f'Status:'), value=str(
            inventory[order_id]['status']).title(), inline=False)
        emb.add_field(name=str(f'Tracking number:'), value=str(
            inventory[order_id]['tracking_no']).title(), inline=False)
        await ctx.send(embed=emb)
    else:
        await ctx.defer(ephemeral=True)
        await ctx.reply("This order number doesn't exist, please check your spelling and try again")


@bot.hybrid_command(name="admin", with_app_command=True, description="Update status of an order")
async def admin(ctx: commands.Context, order_id: str, status: str, *, tracking_number: str = None):
    inventory = IM().order_data()
    if order_id in inventory:
        inventory[order_id]['status'] = status
        if tracking_number is not None:
            inventory[order_id]['tracking_no'] = tracking_number
        with open('orders.json', 'w') as f:
            json.dump(inventory, f)
        await ctx.defer(ephemeral=True)
        await ctx.reply("Success")
    else:
        await ctx.defer(ephemeral=True)
        await ctx.reply("This order number doesn't exist, please check your spelling and try again")


@bot.hybrid_command(name="delivered", with_app_command=True, description="Deliver an order")
async def delivered(ctx: commands.Context, id):
    global order_id
    order_id = id
    inventory = IM().order_data()
    view = Delivery()
    if order_id in inventory:
        inventory[order_id]['status'] = 'Delivered (Pending Confirmation)'
        with open('orders.json', 'w') as f:
            json.dump(inventory, f)
        orderer = await bot.fetch_user(int(inventory[order_id]['orderer']))
        await ctx.send(f'Message sent to {orderer}')
        await orderer.send('Your order was delivered, please confirm if your delivery was received')
        await orderer.send(view=view)

    else:
        await ctx.defer(ephemeral=True)
        await ctx.reply("This order number doesn't exist, please check your spelling and try again")


@bot.hybrid_command(name="add", with_app_command=True, description="Add a product")
async def add(ctx: commands.Context,
              product_id: str,
              name: str,
              *,
              stock: int = 0,
              price: int = 0,
              msrp: int = 0,
              link: str = 'https://www.google.com/',
              photo: str = ''):
    inventory = IM().stock_data()
    if product_id.title() not in inventory:
        IM().create_product(name, product_id, stock, price, msrp, link, photo)
        await ctx.defer(ephemeral=True)
        await ctx.reply('Success!')
        await info(ctx, product_id)
    else:
        await ctx.defer(ephemeral=True)
        await ctx.reply('A product already exists with this name!')


@bot.hybrid_command(name="delete", with_app_command=True, description="delete a product")
async def delete(ctx: commands.Context, product_id: str):
    inventory = IM().stock_data()
    if product_id.title() in inventory:
        IM().delete_product(product_id.title())
        await ctx.defer(ephemeral=True)
        await ctx.reply('Success!')
    else:
        await ctx.send("This product doesn't exist, check your spelling and try again!")


@bot.hybrid_command(name="edit", with_app_command=True, description="edit a product")
async def edit(ctx: commands.Context,
               product_id: str,
               *,
               name: str = None,
               stock: int = None,
               price: int = None,
               msrp: int = None,
               link: str = None,
               photo: str = None):
    inventory = IM().stock_data()
    if product_id.title() in inventory:
        IM().edit2(name, product_id, stock, price, msrp, link, photo)
        await ctx.defer(ephemeral=True)
        await ctx.reply('Success!')
        await info(ctx, product_id)
    else:
        await ctx.send("This product doesn't exist, check your spelling and try again!")


@bot.hybrid_command(name="clear", with_app_command=True, description="clear chat")
async def clear(ctx: commands.Context, ammount: int = 5):
    await ctx.channel.purge(limit=ammount+1)

bot.run('TOKEN')
