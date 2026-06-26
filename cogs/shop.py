import discord
from discord.ext import commands
import bot_package.Custom_func as Cf
import bot_package.economy as eco
import bot_package.data as data

class shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shop")
    async def shop(self, ctx, page:str ="1"):
        '''
        permet de visualiser les items disponibles dans le shop page par page
        '''
        actual_shop = data.shop_item
        try:
            page = int(page)
        except ValueError:
            return await ctx.send(embed=discord.Embed(title="Erreur", description="Veuillez entrer un numéro de page valide.", color=discord.Color.red()))
        if page < 1 or page > len(actual_shop):
            return await ctx.send(embed=discord.Embed(title="Erreur", description=f"Veuillez entrer un numéro de page valide.", color=discord.Color.red()))
        print("Shop command executed")
        embed = discord.Embed(title="Shop",
                          description="Welcome to the shop! Here are the available items:",
                          color=discord.Color.blue())
        for item in actual_shop[f"page {page}"]:
            item_data = actual_shop[f"page {page}"][item]
            price = item_data.get("price")
            description = item_data.get("description", "")
            amount = item_data.get("quantity")
            embed.add_field(name=f"{item} X{amount}", value=f"Prix: {price} orbes\nDescription: {description}", inline=False)
            embed.set_footer(text=f"Page {page}/{len(actual_shop.keys())}")
        return await ctx.send(embed=embed)

    @commands.hybrid_command(name="buy")
    async def buy(self, ctx, item: str):
        '''
        permet d'acheter un item du shop
        '''
        actual_shop = data.shop_item
        item_found = False
        print(f"Buy command executed for item: {item}")
        for page_items in actual_shop.values():
            if item in page_items:
                item_found = True
                page = page_items
                break
        if not item_found:
            return await ctx.send(embed=discord.Embed(title="Erreur", description=f"L'item {item} n'est pas disponible dans le shop.\nMerci de rentrer un item valide.", color=discord.Color.red()))
        else:
            user_balance = await eco.get_balance(ctx.author.id)
            item_info = page[item]
            price = item_info.get("price", 0)
            rang = item_info.get("rang", "obj")
            print(rang)
            quantity = item_info.get("quantity", 1)

            if user_balance < price:
                embed_poor = discord.Embed(title="Erreur", description=f"Vous n'avez pas assez d'orbes pour acheter {item}.", color=discord.Color.red())
                embed_poor.set_footer(text=f"vous avez {user_balance}/{price} orbes") 
                return await ctx.send(embed=embed_poor)
            else:
                await eco.add(ctx.author.id, -price)
                await Cf.add(ctx.author.id, item, rang, "bag", number=quantity)
                embed = discord.Embed(title="Achat réussi", description=f"Vous avez acheté {item} pour {price} orbes.", color=discord.Color.green())
                return await ctx.send(embed=embed)



async def setup(bot) -> None:
    await bot.add_cog(shop(bot))
    