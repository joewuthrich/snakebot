import discord
from discord.ext import commands
import random
import aiohttp
import lxml.html
import orjson
import cogs.utils.database as DB
import config
import opcode
import difflib


opcodes = opcode.opmap


class misc(commands.Cog):
    """Commands that don't fit into other cogs."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def format_op(op):
        return f"{hex(opcodes[op])[2:]:<5}{opcodes[op]:<5}{op}"

    @commands.command()
    async def opcode(self, ctx, search):
        """Gets closest matches for an opcode.

        search: str
        """
        matches = difflib.get_close_matches(
            search.upper(), list(opcodes), cutoff=0, n=5
        )
        msg = "\n".join([self.format_op(match) for match in matches])
        await ctx.send(f"```py\nHex: Num: Name:\n\n{msg}```")

    @commands.group()
    async def binary(self, ctx):
        """Encoded or decodes binary as ascii text."""
        if not ctx.invoked_subcommand:
            embed = discord.Embed(
                color=discord.Color.blurple(),
                description=f"```Usage: {ctx.prefix}binary [decode/encode]```",
            )
            await ctx.send(embed=embed)

    @binary.command(name="encode")
    async def binary_encode(self, ctx, *, text):
        """Encodes ascii text as binary.

        text: str
        """
        await ctx.send(" ".join([f"{bin(ord(letter))[2:]:0>8}" for letter in text]))

    @binary.command(name="decode")
    async def binary_decode(self, ctx, *, binary):
        """Decodes binary as ascii text.

        binary: str
        """
        binary = binary.replace(" ", "")
        # fmt: off
        await ctx.send(
            "".join([chr(int(binary[i: i + 8], 2)) for i in range(0, len(binary), 8)])
        )
        # fmt: on

    @commands.command()
    async def dashboard(self, ctx):
        """Sends a link to Bryns dashboard."""
        await ctx.send("https://web.tukib.org/uoa")

    @commands.command()
    async def notes(self, ctx):
        """Sends a link to Joes notes."""
        embed = discord.Embed(color=discord.Color.blurple(), title="Joes Notes")

        embed.description = """
        [Home Page](https://notes.joewuthrich.com)

        [Compsci 101](https://notes.joewuthrich.com/compsci101)
        Introduction to programming using the python programming language.
        [Compsci 110](https://notes.joewuthrich.com/compsci110)
        This course explains how computers work and some of the things we can use them for.
        [Compsci 120](https://notes.joewuthrich.com/compsci120)
        Introduces basic mathematical tools and methods needed for computer science.
        [Compsci 130](https://notes.joewuthrich.com/compsci130)
        Entry course to Computer Science for students with prior programming knowledge.
        """
        await ctx.send(embed=embed)

    @commands.command()
    async def markdown(self, ctx):
        """Sends a link to a guide on markdown"""
        await ctx.send(
            "https://gist.github.com/matthewzring/9f7bbfd102003963f9be7dbcf7d40e51"
        )

    @staticmethod
    def starmap(iterable):
        for num1, num2 in iterable:
            yield num1 * num2

    @commands.group()
    async def cipher(self, ctx):
        """Solves or encodes a caesar cipher."""
        if not ctx.invoked_subcommand:
            embed = discord.Embed(
                color=discord.Color.blurple(),
                description=f"```Usage: {ctx.prefix}cipher [decode/encode]```",
            )
            await ctx.send(embed=embed)

    @cipher.command()
    async def encode(self, ctx, shift: int, *, message):
        """Encodes a message using the ceasar cipher.

        shift: int
            How much you want to shift the message.
        message: str
        """
        if message.isupper():
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        else:
            message = message.lower()
            chars = "abcdefghijklmnopqrstuvwxyz"

        table = str.maketrans(chars, chars[shift:] + chars[:shift])

        await ctx.send(message.translate(table))

    @cipher.command(aliases=["solve", "brute"])
    async def decode(self, ctx, *, message):
        """Solves a caesar cipher via brute force.
        Shows results sorted by the chi-square of letter frequencies

        message: str
        """
        if message.isupper():
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        else:
            message = message.lower()
            chars = "abcdefghijklmnopqrstuvwxyz"

        # fmt: off

        freq = {
            "a": 8.04, "b": 1.48, "c": 3.34,
            "d": 3.82, "e": 12.49, "f": 2.4,
            "g": 1.87, "h": 5.05, "i": 7.57,
            "j": 0.16, "k": 0.54, "l": 4.07,
            "m": 2.51, "n": 7.23, "o": 7.64,
            "p": 2.14, "q": 0.12, "r": 6.28,
            "s": 6.51, "t": 9.28, "u": 2.73,
            "v": 1.05, "w": 1.68, "x": 0.23,
            "y": 1.66, "z": 0.09,
        }

        # fmt: on

        msg_len = len(message)

        rotate1 = str.maketrans(chars, chars[1:] + chars[0])
        embed = discord.Embed(color=discord.Color.blurple())

        results = []

        for i in range(25, 0, -1):
            message = message.translate(rotate1)
            chi = sum(
                [
                    (((message.count(char) / msg_len) - freq[char]) ** 2) / freq[char]
                    for char in set(message.lower().replace(" ", ""))
                ]
            )
            results.append((chi, (i, message)))

        for chi, result in sorted(results, reverse=True):
            embed.add_field(name=result[0], value=result[1])

        embed.set_footer(text="Sorted by the chi-square of their letter frequencies")

        await ctx.send(embed=embed)

    @commands.command()
    async def block(self, ctx, A, B):
        """Solves a block cipher in the format of a python matrix.

        e.g
        "1 2 3" "3 7 15, 6 2 61, 2 5 1"

        A: str
        B: str
        """
        if "a" < A:
            A = [[ord(letter) - 97 for letter in A]]
        else:
            A = A.split(",")
            A = [[int(num) for num in block.split()] for block in A]
        B = B.split(",")
        B = [[int(num) for num in block.split()] for block in B]

        results = ""

        for block in A:
            results += f"{[sum(self.starmap(zip(block, col))) for col in zip(*B)]}\n"

        embed = discord.Embed(
            color=discord.Color.blurple(), description=f"```{results}```"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def youtube(self, ctx):
        """Starts a YouTube Together."""
        if (code := DB.db.get(b"youtube_together")) and discord.utils.get(
            await ctx.guild.invites(), code=code.decode()
        ):
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    title="There is another active Youtube Together",
                    description=f"https://discord.gg/{code.decode()}",
                )
            )

        if not ctx.author.voice:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description="```You aren't connected to a voice channel.```",
                )
            )

        headers = {"Authorization": f"Bot {config.token}"}
        json = {
            "max_age": 300,
            "target_type": 2,
            "target_application_id": 755600276941176913,
        }

        async with aiohttp.ClientSession(headers=headers) as session, session.post(
            f"https://discord.com/api/v9/channels/{ctx.author.voice.channel.id}/invites",
            json=json,
        ) as response:
            data = await response.json()

        await ctx.send(f"https://discord.gg/{data['code']}")
        DB.db.put(b"youtube_together", data["code"].encode())

    @commands.command()
    @commands.guild_only()
    async def poker(self, ctx):
        """Starts a Discord Poke Night."""
        if (code := DB.db.get(b"poker_night")) and discord.utils.get(
            await ctx.guild.invites(), code=code.decode()
        ):
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    title="There is another active Poker Night",
                    description=f"https://discord.gg/{code.decode()}",
                )
            )

        if not ctx.author.voice:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description="```You aren't connected to a voice channel.```",
                )
            )

        headers = {"Authorization": f"Bot {config.token}"}
        json = {
            "max_age": 300,
            "target_type": 2,
            "target_application_id": 755827207812677713,
        }

        async with aiohttp.ClientSession(headers=headers) as session, session.post(
            f"https://discord.com/api/v9/channels/{ctx.author.voice.channel.id}/invites",
            json=json,
        ) as response:
            data = await response.json()

        await ctx.send(f"https://discord.gg/{data['code']}")
        DB.db.put(b"poker_night", data["code"].encode())

    @commands.command()
    @commands.guild_only()
    async def betrayal(self, ctx):
        """Starts a Betrayal.io game."""
        if (code := DB.db.get(b"betrayal_io")) and discord.utils.get(
            await ctx.guild.invites(), code=code.decode()
        ):
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    title="There is another active Betrayal.io game",
                    description=f"https://discord.gg/{code.decode()}",
                )
            )

        if not ctx.author.voice:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description="```You aren't connected to a voice channel.```",
                )
            )

        headers = {"Authorization": f"Bot {config.token}"}
        json = {
            "max_age": 300,
            "target_type": 2,
            "target_application_id": 773336526917861400,
        }

        async with aiohttp.ClientSession(headers=headers) as session, session.post(
            f"https://discord.com/api/v9/channels/{ctx.author.voice.channel.id}/invites",
            json=json,
        ) as response:
            data = await response.json()

        await ctx.send(f"https://discord.gg/{data['code']}")
        DB.db.put(b"betrayal_io", data["code"].encode())

    @commands.command()
    @commands.guild_only()
    async def fishing(self, ctx):
        """Starts a Fishington.io game."""
        if (code := DB.db.get(b"fishington")) and discord.utils.get(
            await ctx.guild.invites(), code=code.decode()
        ):
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    title="There is another active Fishington.io game",
                    description=f"https://discord.gg/{code.decode()}",
                )
            )

        if not ctx.author.voice:
            return await ctx.send(
                embed=discord.Embed(
                    color=discord.Color.blurple(),
                    description="```You aren't connected to a voice channel.```",
                )
            )

        headers = {"Authorization": f"Bot {config.token}"}
        json = {
            "max_age": 300,
            "target_type": 2,
            "target_application_id": 814288819477020702,
        }

        async with aiohttp.ClientSession(headers=headers) as session, session.post(
            f"https://discord.com/api/v9/channels/{ctx.author.voice.channel.id}/invites",
            json=json,
        ) as response:
            data = await response.json()

        await ctx.send(f"https://discord.gg/{data['code']}")
        DB.db.put(b"fishington", data["code"].encode())

    @commands.command(name="8ball")
    async def eightball(self, ctx):
        """Seek advice or fortune-telling."""
        responses = [
            "It is certain.",
            "Without a doubt.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        await ctx.reply(random.choice(responses))

    @commands.command(name="hex")
    async def _hex(self, ctx, number, convert: bool = False):
        """Shows a number in hexadecimal prefixed with “0x”.

        number: str
            The number you want to convert.
        convert: bool
            If you want to convert to decimal or not
        """
        embed = discord.Embed(color=discord.Color.blurple())
        if convert:
            embed.description = f"```{int(number, 16)}```"
            return await ctx.send(embed=embed)
        embed.description = f"```{hex(int(number))}```"
        await ctx.send(embed=embed)

    @commands.command(name="oct")
    async def _oct(self, ctx, number, convert: bool = False):
        """Shows a number in octal prefixed with “0o”.

        number: str
            The number you want to convert.
        convert: bool
            If you want to convert to decimal or not
        """
        embed = discord.Embed(color=discord.Color.blurple())
        if convert:
            embed.description = f"```{int(number, 8)}```"
            return await ctx.send(embed=embed)
        embed.description = f"```{oct(int(number))}```"
        await ctx.send(embed=embed)

    @commands.command(name="bin")
    async def _bin(self, ctx, number, convert: bool = False):
        """Shows a number in binary prefixed with “0b”.

        number: str
            The number you want to convert.
        convert: bool
            If you want to convert to decimal or not
        """
        embed = discord.Embed(color=discord.Color.blurple())
        if convert:
            embed.description = f"```{int(number, 2)}```"
            return await ctx.send(embed=embed)
        embed.description = f"```{bin(int(number))}```"
        await ctx.send(embed=embed)

    @commands.command()
    async def karma(self, ctx, user: discord.User = None):
        """Gets a users karma.

        user: discord.User
            The user to get the karma of.
        """
        user = user or ctx.author
        user_id = str(user.id).encode()
        karma = DB.karma.get(user_id)

        if not karma:
            karma = 0
        else:
            karma = karma.decode()

        tenary = "+" if int(karma) > 0 else ""

        embed = discord.Embed(color=discord.Color.blurple())
        embed.description = f"```diff\n{user.display_name}'s karma:\n{tenary}{karma}```"
        await ctx.send(embed=embed)

    @commands.command(aliases=["kboard", "karmab", "karmatop"])
    async def karmaboard(self, ctx):
        """Displays the top 5 and bottom 5 members karma."""
        sorted_karma = sorted([(int(k), int(m)) for m, k in DB.karma], reverse=True)
        embed = discord.Embed(title="Karma Board", color=discord.Color.blurple())

        def parse_karma(data):
            lst = []
            for karma, member in data:
                temp = self.bot.get_user(member)
                member = temp.display_name if temp else member
                lst.append(f"{'-' if karma < 0 else '+'} {member}: {karma}")
            return lst

        embed.add_field(
            name="Top Five",
            value="```diff\n{}```".format("\n".join(parse_karma(sorted_karma[:5]))),
        )
        embed.add_field(
            name="Bottom Five",
            value="```diff\n{}```".format("\n".join(parse_karma(sorted_karma[-5:]))),
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def atom(self, ctx, element):
        """Displays information for a given atom.

        element: str
            The symbol of the element to search for.
        """
        url = f"http://www.chemicalelements.com/elements/{element.lower()}.html"
        embed = discord.Embed(colour=discord.Color.blurple())

        async with ctx.typing():
            try:
                async with aiohttp.ClientSession(
                    raise_for_status=True
                ) as session, session.get(url) as page:
                    text = lxml.html.fromstring(await page.text())
            except aiohttp.client_exceptions.ClientResponseError:
                embed.description = f"```Could not find and element with the symbol {element.upper()}```"
                return await ctx.send(embed=embed)

        image = f"http://www.chemicalelements.com{text.xpath('.//img')[1].attrib['src'][2:]}"
        text = text.xpath("//text()")[108:]

        embed.title = text[1]
        embed.set_thumbnail(url=image)
        embed.add_field(name="Name", value=text[1])
        embed.add_field(name="Symbol", value=text[3])
        embed.add_field(name="Atomic Number", value=text[5])
        embed.add_field(name="Atomic Mass", value=text[7])
        embed.add_field(name="Neutrons", value=text[15])
        embed.add_field(name="Color", value=text[text.index("Color:") + 1])
        embed.add_field(name="Uses", value=text[text.index("Uses:") + 1])
        embed.add_field(
            name="Year of Discovery", value=text[text.index("Date of Discovery:") + 1]
        )
        embed.add_field(name="Discoverer", value=text[text.index("Discoverer:") + 1])

        await ctx.send(embed=embed)

    @commands.command()
    async def icon(self, ctx, user: discord.User = None):
        """Sends a members avatar url.

        user: discord.User
            The member to show the avatar of.
        """
        user = user or ctx.author
        await ctx.send(user.avatar_url)

    @commands.command()
    async def roll(self, ctx, dice: str):
        """Rolls dice in AdX format. A is number of dice, X is number of faces.

        dice: str
            The dice to roll in AdX format.
        """
        embed = discord.Embed(color=discord.Color.blurple())

        try:
            rolls, limit = map(int, dice.split("d"))
        except ValueError:
            embed.description = "```Format has to be AdX```"
            return await ctx.send(embed=embed)

        nums = [str(random.randint(1, limit)) for r in range(rolls)]
        result = ", ".join(nums)
        total = sum([int(num) for num in nums])
        embed.description = f"```Results: {result} Total: {total}```"
        await ctx.reply(embed=embed)

    @commands.command()
    async def choose(self, ctx, *options: str):
        """Chooses between mulitple things.

        options: str
            The options to choose from.
        """
        await ctx.reply(random.choice(options))

    @commands.command()
    async def yeah(self, ctx):
        """Oh yeah its all coming together."""
        await ctx.send("Oh yeah its all coming together")

    @commands.command()
    async def slap(self, ctx, member: discord.Member, *, reason="they are evil"):
        """Slaps a member.

        member: discord.Member
            The member to slap.
        reason: str
            The reason for the slap.
        """
        await ctx.send(
            f"{ctx.author.mention} slapped {member.mention} because {reason}"
        )

    @commands.command()
    async def bar(self, ctx, graph_data: commands.Greedy[int] = None):
        """Sends a bar graph based of inputted numbers.

        e.g: bar 1 2 3

                     ____
               ____ |    |
         ____ |    ||    |
        |    ||    ||    |
        ------------------

        graph_data: commands.Greedy[int]
            A list of graph data.
        """
        max_val = max(graph_data)

        char_length = len(graph_data) * 6 * (max_val + 2) + max_val + 7
        if char_length > 2000:
            return await ctx.send(
                f"```Bar graph is greater than 2000 characters [{char_length}]```"
            )

        bar_graph = ""

        for val in range(max_val + 1, 0, -1):
            for index in range(len(graph_data)):
                if graph_data[index] - val > -1:
                    bar_graph += "|    |"
                elif graph_data[index] - val == -1:
                    bar_graph += " ____ "
                else:
                    bar_graph += "      "
            bar_graph += "\n"
        bar_graph += "------" * len(graph_data)

        await ctx.send(f"```{bar_graph}```")

    @commands.group(hidden=True)
    @commands.has_permissions(administrator=True)
    async def ledger(self, ctx):
        """The ledger command group, call without args to show ledger."""
        if not ctx.invoked_subcommand:
            ledger = DB.db.get(b"ledger")
            embed = discord.Embed(color=discord.Color.blurple())

            if not ledger:
                embed.description = "```Ledger is empty.```"
                return await ctx.send(embed=embed)

            ledger = orjson.loads(ledger)
            msg = ""
            for item in ledger["items"]:
                msg += "{} {} {} ${} {}\n".format(
                    self.bot.get_user(int(item["payer"])).display_name,
                    item["type"],
                    self.bot.get_user(int(item["payee"])).display_name,
                    item["amount"],
                    item.get("reason", "paying off their debts"),
                )

            if len(msg) == 0:
                embed.description = "```Ledger is empty.```"
                return await ctx.send(embed=embed)

            embed.description = f"```{msg}```"
            await ctx.send(embed=embed)

    @ledger.command(hidden=True)
    async def payme(self, ctx, member: discord.Member, amount: float, *, reason="idk"):
        """Adds an amount to be paid by member to the ledger.

        member: discord.Member
            The person to pay you.
        amount: float
            How much they are to pay you.
        reason: str
            The reason for the payment.
        """
        ledger = DB.db.get(b"ledger")
        embed = discord.Embed(color=discord.Color.blurple())

        if not ledger:
            ledger = {"items": [], "members": {}}
        else:
            ledger = orjson.loads(ledger)

        ledger["items"].append(
            {
                "type": "owes",
                "amount": amount,
                "reason": f"for {reason}",
                "payee": ctx.author.id,
                "payer": member.id,
            }
        )
        if str(member.id) not in ledger["members"]:
            ledger["members"][str(member.id)] = {}

        if str(ctx.author.id) not in ledger["members"][str(member.id)]:
            ledger["members"][str(member.id)][str(ctx.author.id)] = 0

        if str(member.id) in ledger["members"][str(ctx.author.id)]:
            if ledger["members"][str(ctx.author.id)][str(member.id)] >= amount:
                embed.description = (
                    "```Since {} owes {} {} their debt was canceled out```".format(
                        ctx.author.display_name,
                        member.display_name,
                        ledger["members"][str(ctx.author.id)][str(member.id)],
                    )
                )
                ledger["members"][str(ctx.author.id)][str(member.id)] -= amount
                return await ctx.send(embed=embed)

            amount -= ledger["members"][str(ctx.author.id)][str(member.id)]

        ledger["members"][str(member.id)][str(ctx.author.id)] += amount

        embed.description = "```{} is to pay {} ${:,} because {}```".format(
            member.display_name, ctx.author.display_name, amount, reason
        )
        await ctx.send(embed=embed)
        DB.db.put(b"ledger", orjson.dumps(ledger))

    @ledger.command(hidden=True)
    async def delete(self, ctx, index: int):
        """Deletes an item made by you off the ledger.

        id: str
            The id of the ledger item.
        """
        ledger = DB.db.get(b"ledger")
        embed = discord.Embed(color=discord.Color.blurple())

        if not ledger:
            embed.description = "```Ledger is empty.```"
            return await ctx.send(embed=embed)

        ledger = orjson.loads(ledger)

        try:
            item = ledger["items"][index]
        except IndexError:
            embed.description = "```Index not in ledger.```"
            return await ctx.send(embed=embed)

        if (
            item["payee"] != ctx.author.id
            and item["type"] == "owes"
            or item["payer"] != ctx.author.id
            and item["type"] == "paid"
        ):
            embed.description = "```You are not the creator of this ledger item.```"
            return await ctx.send(embed=embed)

        ledger["items"].pop(index)
        DB.db.put(b"ledger", orjson.dumps(ledger))

    @ledger.command(hidden=True)
    async def pay(self, ctx, member: discord.Member, amount: float):
        """Pay for an ledger item.

        member: discord.Member
            The person to pay.
        amount: float
            The amount to pay.
        """
        ledger = DB.db.get(b"ledger")
        embed = discord.Embed(color=discord.Color.blurple())

        if not ledger:
            ledger = {"items": [], "members": {}}
        else:
            ledger = orjson.loads(ledger)

        ledger["items"].append(
            {
                "type": "paid",
                "amount": amount,
                "payee": member.id,
                "payer": ctx.author.id,
            }
        )

        ledger["members"][str(member.id)][str(ctx.author.id)] = (
            ledger["members"][str(member.id)][str(ctx.author.id)] or 0
        ) - amount

        embed.description = "```{} paid {} ${:,}```".format(
            ctx.author.display_name, member.display_name, amount
        )
        await ctx.send(embed=embed)
        DB.db.put(b"ledger", orjson.dumps(ledger))

    @ledger.command(hidden=True)
    async def member(self, ctx, member: discord.Member):
        """Returns the ledger of the member.

        member: discord.Member
        """
        ledger = DB.db.get(b"ledger")
        embed = discord.Embed(color=discord.Color.blurple())

        if not ledger:
            embed.description = "```Ledger is empty.```"
            return await ctx.send(embed=embed)

        ledger = orjson.loads(ledger)
        msg = ""
        for item in ledger["items"]:
            if item["payer"] == str(member.id) or item["payee"] == str(member.id):
                msg += "{} {} {} ${} {}\n".format(
                    self.bot.get_user(int(item["payer"])).display_name,
                    item["type"],
                    self.bot.get_user(int(item["payee"])).display_name,
                    item["amount"],
                    item.get("reason", "paying off their debts"),
                )

        if len(msg) == 0:
            embed.description = "```Ledger is empty.```"
            return await ctx.send(embed=embed)

        embed.description = f"```{msg}```"
        await ctx.send(embed=embed)

    @ledger.command(hidden=True)
    async def split(
        self, ctx, amount: float, members: commands.Greedy[discord.Member], reason="idk"
    ):
        """Splits an amount between mutiple ledger members.

        amount: float
        members: list[discord.Member]
        reason: str
        """
        ledger = DB.db.get(b"ledger")
        embed = discord.Embed(color=discord.Color.blurple())

        if not ledger:
            ledger = {"items": [], "members": {}}
        else:
            ledger = orjson.loads(ledger)

        for member in members:
            ledger["items"].append(
                {
                    "type": "owes",
                    "amount": amount,
                    "reason": f"for {reason}",
                    "payee": ctx.author.id,
                    "payer": member.id,
                }
            )
            if str(member.id) not in ledger["members"]:
                ledger["members"][str(member.id)] = {}

            if str(ctx.author.id) not in ledger["members"][str(member.id)]:
                ledger["members"][str(member.id)][str(ctx.author.id)] = 0

            if str(member.id) in ledger["members"][str(ctx.author.id)]:
                if ledger["members"][str(ctx.author.id)][str(member.id)] >= amount:
                    ledger["members"][str(ctx.author.id)][str(member.id)] -= amount
                    continue

                amount -= ledger["members"][str(ctx.author.id)][str(member.id)]

            ledger["members"][str(member.id)][str(ctx.author.id)] += amount

            embed.description = "```{} is to pay {} ${:,} because {}```".format(
                member.display_name, ctx.author.display_name, amount, reason
            )
            await ctx.send(embed=embed)
        DB.db.put(b"ledger", orjson.dumps(ledger))


def setup(bot: commands.Bot) -> None:
    """Starts misc cog."""
    bot.add_cog(misc(bot))
