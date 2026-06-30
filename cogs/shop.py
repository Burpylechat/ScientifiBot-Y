import discord
from discord.ext import commands
import bot_package.Custom_func as Cf
import bot_package.economy as eco
import bot_package.data as data
import random
import time

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
        Permet d'acheter un item du shop
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
            



    @commands.hybrid_command(name="daily_shop")
    async def daily_shop(self, ctx):
        current_time = time.time()
        current_day = time.localtime(current_time)
        midnight = time.mktime((current_day.tm_year, current_day.tm_mon, 
                                current_day.tm_mday, 0, 0, 0, 0, 0, 0))
        midnight -= 3600 #correction cause it's fucked up
        bag = await Cf.get_bag(ctx.author.id)

        try:
            last_daily_shop_reset = bag["last_daily_shop_reset"]
        except:
            last_daily_shop_reset = 0
        
        if last_daily_shop_reset < midnight:
            bag["last_daily_shop_reset"] = midnight
            possible_daily_item_type = ["coin", "object", "yo-kai"]
            daily_item_type = random.choices(possible_daily_item_type, weights=[0.33,0.33,0.33])
            print(daily_item_type)
            if daily_item_type == ['coin']:
                coins = data.coin_list
                coins.append("bonus_roll")
                coin_type = random.choices(["normal","rare"],weights=[0.75,0.25])

                
                if coin_type == ['normal']:
                    daily_item = random.choice(data.low_cost_coin_list)
                    price = data.low_cost_coin
                elif coin_type == ['rare']:
                    daily_item = random.choice(data.high_cost_coin_list)
                    price = data.high_cost_coin
                description = "Une petite-pièce à utiliser au /bkai."
                type_daily_shop = "coin"
                data_daily_shop = [type_daily_shop, price, description, daily_item]


            elif daily_item_type == ['object']:
                daily_item = random.choice(data.item_list)
                price = data.price_daily_shop_object
                type_daily_shop = "object"
                description = "Un objet en vente."
                data_daily_shop = [type_daily_shop, price, description, daily_item]
                


            elif daily_item_type == ['yo-kai']:
                weights=data.golden_proba_list.copy() #will do a bingo-kai roll, but with better luck
                class_choice = data.yokai_data[random.choices(data.class_list, weights=weights, k=1)[0]]
                while class_choice["class_name"] in data.blacklist["rang"]:
                    class_choice = data.yokai_data[random.choices(data.class_list, weights=weights, k=1)[0]]

                #get the good name of the class and his id
                class_name = class_choice.get("class_name")
                class_id = class_choice.get("class_id")
                #choose the Yo-kai in the class
                Yokai_choice = random.choice(class_choice["yokai_list"])
        
                while Yokai_choice in data.blacklist.get("yokai") :
                    Yokai_choice = random.choice(class_choice["yokai_list"])
                Yokai_choice = Yokai_choice
                description = f"Un magnifique yo-kai de rang {class_name}✨"
                type_daily_shop = "yokai"
                price = data.classid_to_price[class_id]
                data_daily_shop = [type_daily_shop, description, price, Yokai_choice, class_id]
                
            
            bag["daily_shop_data"] = data_daily_shop
            bag["daily_shop_bought"] = False
            embed = discord.Embed(
                title="Votre item du jour dans la boutique:",
                description=""
            )
            description = bag["daily_shop_data"][2]
            price = bag["daily_shop_data"][1]
            if bag["daily_shop_data"][0] == "yokai":
                class_name = Cf.classid_to_class(bag["daily_shop_data"][4])
                embed.add_field(name = f"{daily_item}",value = f"Rang: {class_name} \nDescription: {description} \nPrix: {price} orbes")
            else:
                embed.add_field(name = f"{daily_item}",value = f"Description: {description} \nPrix: {price} orbes")
            await Cf.save_bag(bag,ctx.author.id)
            return await ctx.send(embed=embed)
        
        
        else:
            bag = await Cf.get_bag(ctx.author.id)
            daily_item = bag["daily_shop_data"][3]
            embed = discord.Embed(
                title="Votre item du jour dans la boutique:",
                description=""
            )
            description = bag["daily_shop_data"][2]
            price = bag["daily_shop_data"][1]
            if bag["daily_shop_data"][0] == "yokai":
                class_name = Cf.classid_to_class(bag["daily_shop_data"][4])
                embed.add_field(name = f"{daily_item}",value = f"Rang: {class_name} \nDescription: {description} \nPrix: {price} orbes")
            else:
                embed.add_field(name = f"{daily_item}",value = f"Description: {description} \nPrix: {price} orbes")
            return await ctx.send(embed=embed)
    


    @commands.hybrid_command(name="buy_daily")
    async def buy_daily(self, ctx):

        #vérifie si la personne à déja fait son /daily_shop, sinon réitinialise son daily_shop
        current_time = time.time()
        current_day = time.localtime(current_time)
        midnight = time.mktime((current_day.tm_year, current_day.tm_mon, 
                                current_day.tm_mday, 0, 0, 0, 0, 0, 0))
        midnight -= 3600 #correction cause it's fucked up
        bag = await Cf.get_bag(ctx.author.id)
        balance = await eco.get_balance(ctx.author.id)
        price = bag["daily_shop_data"][1]

        try:
            last_daily_shop_reset = bag["last_daily_shop_reset"]
        except:
            last_daily_shop_reset = 0
        
        if last_daily_shop_reset < midnight:
            bag["last_daily_shop_reset"] = midnight
            possible_daily_item_type = ["coin", "object", "yo-kai"]
            daily_item_type = random.choices(possible_daily_item_type, weights=[0.33,0.33,0.33])
            print(daily_item_type)
            if daily_item_type == ['coin']:
                coins = data.coin_list
                coins.append("bonus_roll")
                coin_type = random.choices(["normal","rare"],weights=[0.75,0.25])

                
                if coin_type == ['normal']:
                    daily_item = random.choice(data.low_cost_coin_list)
                    price = data.low_cost_coin
                elif coin_type == ['rare']:
                    daily_item = random.choice(data.high_cost_coin_list)
                    price = data.high_cost_coin
                description = "Une petite-pièce à utiliser au /bkai."
                type_daily_shop = "coin"
                data_daily_shop = [type_daily_shop, price, description, daily_item]


            elif daily_item_type == ['object']:
                daily_item = random.choice(data.item_list)
                price = data.price_daily_shop_object
                type_daily_shop = "object"
                description = "Un objet en vente."
                data_daily_shop = [type_daily_shop, price, description, daily_item]
                


            elif daily_item_type == ['yo-kai']:
                weights=data.golden_proba_list.copy() #will do a bingo-kai roll, but with better luck
                class_choice = data.yokai_data[random.choices(data.class_list, weights=weights, k=1)[0]]
                while class_choice["class_name"] in data.blacklist["rang"]:
                    class_choice = data.yokai_data[random.choices(data.class_list, weights=weights, k=1)[0]]

                #get the good name of the class and his id
                class_name = class_choice.get("class_name")
                class_id = class_choice.get("class_id")
                #choose the Yo-kai in the class
                Yokai_choice = random.choice(class_choice["yokai_list"])
        
                while Yokai_choice in data.blacklist.get("yokai") :
                    Yokai_choice = random.choice(class_choice["yokai_list"])
                Yokai_choice = Yokai_choice
                description = f"Un magnifique yo-kai de rang {class_name}✨"
                type_daily_shop = "yokai"
                price = data.classid_to_price[class_id]
                data_daily_shop = [type_daily_shop, description, price, Yokai_choice, class_id]
                
            
            bag["daily_shop_data"] = data_daily_shop
            bag["daily_shop_bought"] = False
            await Cf.save_bag(bag, ctx.author.id)

        elif bag["daily_shop_bought"] == True:
            embed = discord.Embed(
                title="Achat impossible",
                description="Vous avez déja acheté votre item quotidien. Réessayer demain."
                )
            return await ctx.send(embed=embed)
        

        elif balance >= price:
            if bag["daily_shop_data"][0] == "object":
                item = bag["daily_shop_data"][3]
                item_type = "obj"
                item_desc = data.item[item]["desc"]
                if bag == {}:
                    bag = data.default_bag.copy()
                    verification = False
                else:
                    verification = True

                if verification:
                    for elements in bag.keys():
                        if elements == item:
                            verification = False
                            try:
                                bag[item][1] += 1
                            except IndexError:
                                bag[item].append(2)
                                
                            #make the embed
                            item_embed = discord.Embed(
                                title="Vous avez acheté un objet 📦 ! ",
                                description=f"> **{item}**",
                                color=discord.Color.from_str("#674202")
                            )
                            #get the image

                            id = data.item[item]["id"]
                            item_embed.set_image(url=f"https://lfbn-idf3-1-5-236.w81-249.abo.wanadoo.fr/{id}.png")
                            
                            item_embed.add_field(
                                name=f"Vous l'avez déjà eu. Vous en avez donc {bag[item][1]}",
                                value="Faites `/bag` pour voir votre sacoche."
                            )
                            item_embed.add_field(name="Mhh, voici quelques informations 📜", inline=False, value=f"> {item_desc}")
                            item_embed.set_footer(text=f"Achat quotidien réalisé!")
                            await eco.add(ctx.author.id, -price)
                            bag["daily_shop_bought"] == False
                            await Cf.save_bag(bag,ctx.author.id)
                            return await ctx.send(embed=item_embed)

                if verification:
                    bag[item] = [item_type]
                    try:
                        bag[item_type] += 1
                    except KeyError:
                        bag[item_type] = 1
                    item_embed = discord.Embed(
                        title="Vous avez acheté un objet 📦 ! ",
                        description=f"> **{item}**",
                        color=discord.Color.from_str("#674202")
                    )
                    #get the image

                    id = data.item[item]["id"]
                    item_embed.set_image(url=f"https://lfbn-idf3-1-5-236.w81-249.abo.wanadoo.fr/{id}.png")
                    
                    item_embed.add_field(
                        name=f"Vous ne l'avez jamais eu !",
                        value="Faites `/bag` pour voir votre sacoche."
                    )
                    item_embed.add_field(name="Mhh, voici quelques informations 📜", inline=False, value=f"> {item_desc}")
                    
                    item_embed.set_footer(text=f"Achat quotidien réalisé!")
                    await eco.add(ctx.author.id, -price)
                    bag["daily_shop_bought"] == False
                    await Cf.save_bag(bag,ctx.author.id)
                    return await ctx.send(embed=item_embed)

            if bag["daily_shop_data"][0] == "coin":
                coin = bag["daily_shop_data"][3]
                verification = True
                coin_color = data.coin_data[coin]["color"]
                coin_id = data.coin_data[coin]["id"]
            
                coin_embed = discord.Embed(
                    title=f"Oh, vous avez eu une {coin} en bonus !",
                    description=f"Félicitations, vous pouvez l'utiliser avec `/bingo-kai {coin}`.\n-# A savoir: le /bkai avec des pièces n'a pas de cooldown, juste une limite journalière (=>vous pouvez le spam tant que vous avez des pièces)",
                    color=discord.Color.from_str(coin_color)
                )
            
                #add the image
                coin_embed.set_image(url=f"https://lfbn-idf3-1-5-236.w81-249.abo.wanadoo.fr/{coin_id}.png")

                #check if the bag is empty
                if bag == {} :
                    bag = {
                       "coin" : 1,
                       "obj" : 0,
                       "treasure" : 0,
                       coin : ["coin"]
                    }
                    verification = False
            
                if verification == True:
                    #get all the coins
                    for elements in bag.keys():
                        if elements == coin:
                            #stack the coin
                            try:
                            #stack the Yo-kai
                                bag[coin][1] += 1
                            except IndexError:
                                bag[coin].append(2)
                            verification = False

                         #Generate the rest of the embed
                            coin_embed.add_field(
                                name=f"Vous l'avez déjà eu. Vous en avez donc {bag[coin][1]}",
                                value="Faites `/bag` pour voir votre sacoche."
                            )

                    if verification == True:  
                        bag[coin] = ["coin"]
                        bag["coin"] += 1
                        coin_embed.add_field(
                            name="Vous ne l'avez jamais eu !",
                            value="Elle a été ajoutée à votre sacoche. Faites `/bag` pour la voir."
                        )
                await eco.add(ctx.author.id, -price)
                bag["daily_shop_bought"] == False
                await Cf.save_bag(bag,ctx.author.id)
                return await ctx.send(embed=coin_embed)

            elif bag["daily_shop_data"] == "yokai":
                brute_inventory = Cf.get_inv(ctx.author.id)
                
                yokai_embed = discord.Embed(
                    title=f"Vous avez eu le Yo-kai **{Yokai_choice}** ✨ ",
                    description=f"Félicitations il est de rang **{class_name}**",
                    color=discord.Color.from_str(data.yokai_data[class_id]["color"])
                )
                yokai_embed.set_thumbnail(url=data.image_link[class_id])
                id = data.yokai_list_full.get(Yokai_choice, {}).get("id", None) #I feel ashamed of what I did here
                yokai_embed.set_image(url=f"https://lfbn-idf3-1-5-236.w81-249.abo.wanadoo.fr/{id}.png")

                #is the Yo-kai in the inventory
                #try the inv
                if brute_inventory == {}:
                    brute_inventory = data.default_medallium.copy()
                    brute_inventory["last_claim"] = time.time()
                    verification = False
                else:
                    verification = True

                if verification == True:
                    #get all the yokais
                    for elements in brute_inventory.keys():
                        if elements == Yokai_choice:
                            verification = False
                            try:
                                #stack the Yo-kai
                                brute_inventory[Yokai_choice][1] += 1
                            except IndexError:
                                brute_inventory[Yokai_choice].append(2)

                            #Generate the embed
                            yokai_embed.add_field(
                                name=f"Vous l'avez déjà eu. Vous en avez donc {brute_inventory[Yokai_choice][1]}",
                                value="Faites `/medallium` pour voir votre Médallium."
                            )
                            #Set last claim
                            brute_inventory["last_claim"] = time.time()
                            #SAVE the inv
                            await Cf.save_inv(brute_inventory, ctx.author.id)                            



                    if verification == True:
                        brute_inventory[Yokai_choice] = [class_id]
                        try:
                            brute_inventory[class_id] += 1
                        except KeyError:
                            brute_inventory[class_id] = 1
                        brute_inventory["last_claim"] = time.time()
                        await Cf.save_inv(brute_inventory, ctx.author.id)
                        yokai_embed.add_field(
                            name="Vous ne l'avez jamais eu ! 🆕",
                            value="Il a été ajouté à votre Médallium. Faites `/medallium` pour le voir."
                        )

                else:
                    brute_inventory[Yokai_choice] = [class_id]
                    try:
                        brute_inventory[class_id] += 1
                    except KeyError:
                        brute_inventory[class_id] = 1
                    await Cf.save_inv(brute_inventory, ctx.author.id)
                    yokai_embed.add_field(
                        name="Vous ne l'avez jamais eu ! 🆕",
                        value="Il a été ajouté à votre Médallium. Faites `/medallium` pour le voir."
                    )


        else:
            poor_embed = discord.Embed(
                title="Tu ne peux pas acheter cela",
                description=f"Tu n'as pas assez d'argent pour acheter cela.\nIl te faut {price} orbes, mais tu n'as que {balance} orbes.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=poor_embed)


async def setup(bot) -> None:
    await bot.add_cog(shop(bot))
    
