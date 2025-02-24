import asyncio
import datetime
import os
import re
import unittest

import aiohttp

import tests.helpers as helpers
from bot import Bot
from cogs.animals import animals
from cogs.apis import apis
from cogs.compsci import compsci
from cogs.crypto import crypto
from cogs.economy import economy
from cogs.images import images
from cogs.information import information
from cogs.misc import misc
from cogs.moderation import moderation
from cogs.stocks import stocks
from cogs.useful import useful
from run_tests import SKIP_API_TESTS, SKIP_IMAGE_TESTS

bot = Bot(helpers.MockBot())
bot.user = helpers.MockUser()
bot.uptime = 0
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


url_regex = re.compile(
    r"^(?:http)s?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}"
    r"[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))",
    re.IGNORECASE,
)


class AdminCogTests(unittest.IsolatedAsyncioTestCase):
    pass


class AnimalsCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = animals(bot=bot)

    async def run_command(self, command):
        context = helpers.MockContext()

        with self.subTest(command=command.name):
            await command._callback(self.cog, context)

            if context.send.call_args.args:
                self.assertRegex(context.send.call_args.args[0], url_regex)
            else:
                file = context.send.call_args.kwargs.get("file")
                if file:
                    self.assertIsNotNone(file)
                else:
                    self.assertNotEqual(
                        context.send.call_args.kwargs["embed"].color.value, 10038562
                    )

    @unittest.skipIf(SKIP_API_TESTS, "Really Slow.")
    async def test_animal_commands(self):
        bot.client_session = aiohttp.ClientSession()

        await asyncio.gather(
            *[self.run_command(command) for command in self.cog.walk_commands()]
        )


class ApisCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = apis(bot=bot)

    @unittest.skipIf(SKIP_API_TESTS, "Really Slow.")
    async def test_api_commands(self):
        bot.client_session = aiohttp.ClientSession()

        await asyncio.gather(
            *[getattr(self, name)() for name in dir(self) if name.endswith("command")]
        )

    async def curl_command(self):
        context = helpers.MockContext()
        code = r"""
        curl 'https://axoltlapi.herokuapp.com/' \
            -H 'Connection: keep-alive' \
            -H 'Cache-Control: max-age=0' \
            -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36' \
            -H 'Referer: https://theaxolotlapi.netlify.app/' \
            -H 'Accept-Language: en-US,en;q=0.9' \
            --compressed
        """

        with self.subTest(command="curl"):
            await self.cog.curl(self.cog, context, code=code)

    async def t0_command(self):
        context = helpers.MockContext()

        with self.subTest(command="t0"):
            await self.cog.t0(self.cog, context, prompt="What is life")

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def reddit_command(self):
        context = helpers.MockContext()

        with self.subTest(command="reddit"):
            await self.cog.reddit(self.cog, context)

            if context.send.call_args.kwargs:
                self.assertNotEqual(
                    context.send.call_args.kwargs["embed"].color.value, 10038562
                )

    async def synth_command(self):
        context = helpers.MockContext()

        with self.subTest(command="synth"):
            await self.cog.synth(self.cog, context, prompt="reverse a binary tree")

            self.assertNotEqual(
                context.reply.call_args.kwargs["embed"].color.value, 10038562
            )

    async def coffee_command(self):
        context = helpers.MockContext()

        with self.subTest(command="coffee"):
            await self.cog.coffee(self.cog, context)

            self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def inspiro_command(self):
        context = helpers.MockContext()

        with self.subTest(command="inspiro"):
            await self.cog.inspiro(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def wikipath_command(self):
        context = helpers.MockContext()

        with self.subTest(command="wikipath"):
            await self.cog.wikipath(
                self.cog, context, source="Venus flytrap", target="False memory"
            )

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def wolfram_command(self):
        context = helpers.MockContext()

        with self.subTest(command="wolfram"):
            await self.cog.wolfram(self.cog, context, query="1 plus 1")

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def fact_command(self):
        context = helpers.MockContext()

        with self.subTest(command="fact"):
            await self.cog.fact(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def country_command(self):
        context = helpers.MockContext()

        with self.subTest(command="country"):
            await self.cog.country(self.cog, context, name="New Zealand")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```Country not found```")

    async def kanye_command(self):
        context = helpers.MockContext()

        with self.subTest(command="kanye"):
            await self.cog.kanye(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def quote_command(self):
        context = helpers.MockContext()

        with self.subTest(command="quote"):
            await self.cog.quote(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def suntzu_command(self):
        context = helpers.MockContext()

        with self.subTest(command="suntzu"):
            await self.cog.suntzu(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def rhyme_command(self):
        context = helpers.MockContext()

        with self.subTest(command="rhyme"):
            await self.cog.rhyme(self.cog, context, word="forgetful")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```No results found```")

    async def spelling_command(self):
        context = helpers.MockContext()

        with self.subTest(command="spelling"):
            await self.cog.spelling(self.cog, context, word="hipopatamus")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```No results found```")

    async def apod_command(self):
        context = helpers.MockContext()

        with self.subTest(command="apod"):
            await self.cog.apod(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def cocktail_command(self):
        context = helpers.MockContext()

        with self.subTest(command="cocktail"):
            await self.cog.cocktail(self.cog, context)

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```No cocktails found.```")

    async def trivia_command(self):
        context = helpers.MockContext()

        with self.subTest(command="trivia"):
            await self.cog.trivia(self.cog, context)

    async def minecraft_command(self):
        context = helpers.MockContext()

        with self.subTest(command="minecraft"):
            await self.cog.minecraft(self.cog, context, ip="ntgc.ddns.net")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```Pinging failed.```")
            self.assertNotEqual(embed.description, "```Pinging timed out.```")

    async def define_command(self):
        context = helpers.MockContext()

        with self.subTest(command="define"):
            for word in ("cat", "pseudoscorpion"):
                await self.cog.define(self.cog, context, word=word)

                embed = context.send.call_args.kwargs["embed"]

                self.assertNotEqual(embed.color.value, 10038562)
                self.assertNotEqual(embed.description, "```No definition found```")

    async def synonyms_command(self):
        context = helpers.MockContext()

        with self.subTest(command="synonyms"):
            await self.cog.synonyms(self.cog, context, word="cat")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```Word not found```")

    async def latex_command(self):
        context = helpers.MockContext()

        with self.subTest(command="latex"):
            await self.cog.latex(self.cog, context, latex="Latex")

            self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def xkcd_command(self):
        context = helpers.MockContext()

        with self.subTest(command="xkcd"):
            await self.cog.xkcd(self.cog, context)

            self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def urban_command(self):
        context = helpers.MockContext()

        with self.subTest(command="urban"):
            await self.cog.urban(self.cog, context, search="cat")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.title, "Timed out try again later")
            self.assertNotEqual(embed.title, "No results found")

    async def wikir_command(self):
        context = helpers.MockContext()

        with self.subTest(command="wikir"):
            await self.cog.wikir(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def wikipedia_command(self):
        context = helpers.MockContext()

        with self.subTest(command="wikipedia"):
            await self.cog.wikipedia(self.cog, context, search="cat")

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(embed.description, "```Couldn't find any results```")

    async def covid_command(self):
        context = helpers.MockContext()

        with self.subTest(command="covid"):
            await self.cog.covid(self.cog, context)

            embed = context.send.call_args.kwargs["embed"]

            self.assertNotEqual(embed.color.value, 10038562)
            self.assertNotEqual(
                embed.description,
                "```Not a valid country\nExamples: NZ, New Zealand, all```",
            )

    async def github_command(self):
        context = helpers.MockContext()

        with self.subTest(command="github"):
            await self.cog.github(self.cog, context, username="Singularitat")

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )


class Background_TasksCogTests(unittest.IsolatedAsyncioTestCase):
    pass


class CompsciCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = compsci(bot=bot)

    async def test_prop_command(self):
        context = helpers.MockContext()

        await self.cog.prop(self.cog, context, "1000Mb", "800km", "200000km/s", "10000")

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_network_command(self):
        context = helpers.MockContext()

        await self.cog.network(self.cog, context, "50.74.27.18/21")

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_ip_command(self):
        context = helpers.MockContext()

        tests = (
            ("50.74.24.1", "```ahk\n00110010010010100001100000000001```"),
            ("00110010010010100001100000000001", "```ahk\n50.74.24.1```"),
        )

        for test, answer in tests:
            with self.subTest(test=test):
                await self.cog.ip(self.cog, context, test)

                self.assertEqual(context.send.call_args.args[0], answer)

    async def test_hex_command(self):
        context = helpers.MockContext()

        await self.cog._hex(self.cog, context, number="16666")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )
        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```py\nhex: 411A\nint: 91750```",
        )

    async def test_oct_command(self):
        context = helpers.MockContext()

        await self.cog._oct(self.cog, context, number="1666")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )
        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```py\noct: 3202\nint: 950```",
        )

    async def test_bin_command(self):
        context = helpers.MockContext()

        tests = (
            ("1666", "```py\nbin: 11010000010\nint: failed```"),
            (
                "11010000010",
                "```py\nbin: 1010010000001111110100010010001010\nint: 1666```",
            ),
            ("16.5", "```py\nbin: 10000.1\nint: failed```"),
            (
                "10000.1",
                "```py\nbin: 10011100010000.000110011001100110011001100110011001101\nint: 16.5```",
            ),
        )

        for test, answer in tests:
            with self.subTest(test=test):
                await self.cog._bin(self.cog, context, number=test)

                self.assertNotEqual(
                    context.send.call_args.kwargs["embed"].color.value, 10038562
                )
                self.assertEqual(
                    context.send.call_args.kwargs["embed"].description,
                    answer,
                )

    async def test_caesar_command(self):
        context = helpers.MockContext()
        context.invoked_subcommand = None

        await self.cog.caesar(self.cog, context)

        self.assertEqual(
            context.reply.call_args.kwargs["embed"].description,
            f"```Usage: {context.prefix}caesar [decode/encode]```",
        )

    async def test_caesar_encode_command(self):
        context = helpers.MockContext()

        await self.cog.caesar_encode(
            self.cog,
            context,
            shift=7,
            message="the quick brown fox jumps over the lazy dog",
        )

        context.reply.assert_called_with("aol xbpjr iyvdu mve qbtwz vcly aol shgf kvn")

    async def test_caesar_decode_command(self):
        context = helpers.MockContext()

        await self.cog.caesar_decode(
            self.cog, context, message="aol xbpjr iyvdu mve qbtwz vcly aol shgf kvn"
        )

        self.assertNotEqual(
            context.reply.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_block_command(self):
        context = helpers.MockContext()

        await self.cog.block(self.cog, context, A="1 2 3", B="3 7 15, 6 2 61, 2 5 1")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )
        self.assertEqual(
            context.send.call_args.kwargs["embed"].description, "```[21, 26, 140]\n```"
        )

    async def test_binary_command(self):
        context = helpers.MockContext()
        context.invoked_subcommand = None

        await self.cog.binary(self.cog, context)

        self.assertEqual(
            context.reply.call_args.kwargs["embed"].description,
            f"```Usage: {context.prefix}binary [decode/encode]```",
        )

    async def test_binary_encode_command(self):
        context = helpers.MockContext()

        await self.cog.binary_encode(
            self.cog,
            context,
            text="lazy",
        )

        context.reply.assert_called_with(
            "```less\n01101100 01100001 01111010 01111001```"
        )

    async def test_binary_decode_command(self):
        context = helpers.MockContext()

        await self.cog.binary_decode(
            self.cog, context, binary="01101100 01100001 01111010 01111001"
        )

        context.reply.assert_called_with("lazy")

    async def test_dashboard_command(self):
        context = helpers.MockContext()

        await self.cog.dashboard(self.cog, context)

        context.send.assert_called_with("https://web.tukib.org/uoa")

    async def test_notes_command(self):
        context = helpers.MockContext()

        await self.cog.notes(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_ones_command(self):
        context = helpers.MockContext()

        await self.cog.ones(self.cog, context, number=32, bits=7)

        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```0011111```",
        )

    async def test_twos_command(self):
        context = helpers.MockContext()

        await self.cog.twos(self.cog, context, number=32, bits=8)

        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```00100000```",
        )

    async def test_rle_command(self):
        context = helpers.MockContext()
        context.invoked_subcommand = None

        await self.cog.rle(self.cog, context)

        self.assertEqual(
            context.reply.call_args.kwargs["embed"].description,
            f"```Usage: {context.prefix}rle [de/en]```",
        )

    async def test_rle_en_command(self):
        context = helpers.MockContext()

        await self.cog.en(self.cog, context, text="aaaabbbccd")

        context.reply.assert_called_with("a4b3c2d1")

    async def test_rle_de_command(self):
        context = helpers.MockContext()

        await self.cog.de(self.cog, context, text="a4b3c2d1")

        context.reply.assert_called_with("aaaabbbccd")

    async def test_calc_command(self):
        context = helpers.MockContext()

        await self.cog.calc(self.cog, context, num_base="hex", expr="0x7d * 0x7d")

        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```py\n125 * 125\n\n>>> 0x3D09\n\nDecimal: 15625```",
        )

        await self.cog.calc(self.cog, context, "sin(10) ** 10")

        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```py\nsin(10) ** 10 \n\n>>> 0.0022706883377346374```",
        )

        await self.cog.calc(self.cog, context, "fact(10) ** pi")

        self.assertEqual(
            context.send.call_args.kwargs["embed"].description,
            "```py\nfact(10) ** pi \n\n>>> 4.056050498299384e+20```",
        )

    async def test_float_command(self):
        context = helpers.MockContext()

        await self.cog._float(self.cog, context, number=3.125)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def cheatsheet_command(self):
        with self.subTest(command="cheatsheet"):
            context = helpers.MockContext()

            await self.cog.cheatsheet(self.cog, context, "reverse a linked list")

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def test_hello_command(self):
        context = helpers.MockContext()

        await self.cog.hello(self.cog, context, language="python3")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_languages_command(self):
        context = helpers.MockContext()

        await self.cog.languages(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_tiolanguages_command(self):
        context = helpers.MockContext()

        await self.cog.tiolanguages(self.cog, context)

        # It does send an embed but it uses `embeds` rather than `embed`
        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def run_command(self):
        with self.subTest(command="run"):
            context = helpers.MockContext()

            await self.cog.run(self.cog, context, code="```py\nprint('Test')```")

            self.assertIsNone(context.reply.call_args.kwargs.get("embed"))
            self.assertEqual(context.reply.call_args.args[0], "```py\nTest\n```")

    async def tio_command(self):
        with self.subTest(command="tio"):
            context = helpers.MockContext()

            await self.cog.tio(self.cog, context, code="```python\nprint('Test')```")

            self.assertIsNone(context.send.call_args.kwargs.get("embed"))


class CryptoCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = crypto(bot=bot)

    async def test_crypto_command(self):
        context = helpers.MockContext()
        context.invoked_subcommand = None
        context.subcommand_passed = "BTC"

        await self.cog.crypto(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].description,
            "```No stock found for BTC```",
        )

    async def test_crypto_buy_command(self):
        context = helpers.MockContext()

        await self.cog.buy(self.cog, context, symbol="btc", cash=1)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_crypto_profile_command(self):
        context = helpers.MockContext()

        await self.cog.profile(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_crypto_bal_command(self):
        context = helpers.MockContext()

        await self.cog.bal(self.cog, context, symbol="btc")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_crypto_sell_command(self):
        context = helpers.MockContext()

        await self.cog.sell(self.cog, context, symbol="btc", amount="100%")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_crypto_list_command(self):
        context = helpers.MockContext()

        await self.cog.list(self.cog, context)

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_crypto_history_command(self):
        context = helpers.MockContext()

        await self.cog.history(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )


class EconomyCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = economy(bot=bot)

    async def test_coinflip_command(self):
        context = helpers.MockContext()

        await self.cog.coinflip(self.cog, context, "heads", "0")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_lottery_command(self):
        context = helpers.MockContext()

        await self.cog.lottery(self.cog, context, "1")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_baltop_command(self):
        context = helpers.MockContext()

        await self.cog.baltop(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_slot_command(self):
        context = helpers.MockContext()

        await self.cog.slot(self.cog, context, bet="1")

        self.assertNotEqual(
            context.reply.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_streak_command(self):
        context = helpers.MockContext()

        await self.cog.streak(self.cog, context)

        if hasattr(context.send.call_args, "kwargs"):
            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def test_chances_command(self):
        context = helpers.MockContext()

        await self.cog.chances(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_networth_command(self):
        context = helpers.MockContext()

        await self.cog.networth(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_pay_command(self):
        context = helpers.MockContext()

        await self.cog.pay(self.cog, context, helpers.MockMember(), "0")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_nettop_command(self):
        context = helpers.MockContext()

        await self.cog.nettop(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )


class EventsCogTests(unittest.IsolatedAsyncioTestCase):
    pass


class HelpCogTests(unittest.IsolatedAsyncioTestCase):
    pass


class ImagesCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = images(bot=bot)

    async def run_command(self, command):
        context = helpers.MockContext()

        with self.subTest(command=command.name):
            await command._callback(
                self.cog, context, url="https://i.imgur.com/oMdVph0.jpeg"
            )

            self.assertIsNotNone(context.reply.call_args.kwargs["file"])

    @unittest.skipIf(SKIP_IMAGE_TESTS, "Really Slow.")
    async def test_image_commands(self):
        bot.client_session = aiohttp.ClientSession()

        await asyncio.gather(
            *[
                self.run_command(command)
                for command in self.cog.walk_commands()
                if command.name != "images"
            ]
        )


class InformationCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = information(bot=bot)

    async def test_about_command(self):
        context = helpers.MockContext()

        await self.cog.about(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    @unittest.skipIf(SKIP_API_TESTS, "Really Slow.")
    async def test_message_top_commmand(self):
        bot.client_session = aiohttp.ClientSession()
        context = helpers.MockContext()

        await self.cog.message_top(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_permissions_command(self):
        context = helpers.MockContext()

        await self.cog.permissions(self.cog, context, member=helpers.MockMember())

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_invite_command(self):
        context = helpers.MockContext()

        await self.cog.invite(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_ping_command(self):
        context = helpers.MockContext()
        context.message.created_at = datetime.datetime.now(datetime.timezone.utc)

        await self.cog.ping(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_usage_command(self):
        context = helpers.MockContext()

        await self.cog.usage(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_source_command(self):
        context = helpers.MockContext()
        self.cog.bot.get_command = bot.get_command

        await self.cog.source(self.cog, context, command="source")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_user_command(self):
        context = helpers.MockContext()

        await self.cog.user(self.cog, context, user=helpers.MockMember())

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_server_command(self):
        context = helpers.MockContext()

        await self.cog.server(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_icon_command(self):
        context = helpers.MockContext()

        await self.cog.icon(self.cog, context, user=helpers.MockMember())

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_banner_command(self):
        context = helpers.MockContext()

        await self.cog.banner(self.cog, context, user=helpers.MockMember())

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_uptime_command(self):
        context = helpers.MockContext()

        await self.cog.uptime(self.cog, context)

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))


class MiscCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = misc(bot=bot)

    @unittest.skipIf(SKIP_API_TESTS, "Really Slow.")
    async def test_misc_commands(self):
        bot.client_session = aiohttp.ClientSession()

        await asyncio.gather(
            *[
                getattr(self, name)()
                for name in dir(self)
                if name.endswith("command") and not name.startswith("test")
            ]
        )

    async def dcommits_command(self):
        context = helpers.MockContext()

        with self.subTest(command="dcommits"):
            await self.cog.dcommits(
                self.cog,
                context,
            )
            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def color_command(self):
        context = helpers.MockContext()

        await self.cog.color(self.cog, context, color="f542e3")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def atom_command(self):
        context = helpers.MockContext()

        await self.cog.atom(self.cog, context, "O")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_char_command(self):
        context = helpers.MockContext()

        await self.cog.char(
            self.cog,
            context,
            characters="abcd",
        )
        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_code_command(self):
        context = helpers.MockContext()

        await self.cog.code(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_md_command(self):
        context = helpers.MockContext()

        await self.cog.md(self.cog, context, text="!@#$%^&*()")

        self.assertNotEqual(
            context.send.call_args.kwargs["embeds"][0].color.value, 10038562
        )

    async def test_diff_command(self):
        context = helpers.MockContext()

        await self.cog.diff(self.cog, context, "13/10/2021")

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))

    async def test_justin_command(self):
        context = helpers.MockContext()

        await self.cog.justin(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_yeah_command(self):
        context = helpers.MockContext()

        await self.cog.yeah(self.cog, context)

        context.send.assert_called_with("Oh yeah its all coming together")

    async def test_embedjson_command(self):
        context = helpers.MockContext()

        await self.cog.embedjson(self.cog, context, message=helpers.MockMessage())

        self.assertEqual(
            context.send.call_args.kwargs["embed"].description[:61],
            '```json\n<MagicMock name="mock.embeds.__getitem__().to_dict()"',
        )

    async def test_rate_command(self):
        context = helpers.MockContext()

        await self.cog.rate(self.cog, context)

        self.assertIsNone(context.reply.call_args.kwargs.get("embed"))

    async def test_match_command(self):
        context = helpers.MockContext()

        await self.cog.match(
            self.cog,
            context,
            user1=helpers.MockMember(name="Snake Bot", id=744747000293228684),
        )

        self.assertIsNone(context.reply.call_args.kwargs.get("embed"))

    async def test_snowflake_command(self):
        context = helpers.MockContext()

        await self.cog.snowflake(self.cog, context, snowflake=744747000293228684)

        embed = context.send.call_args.kwargs["embed"]

        self.assertEqual(embed.fields[0].value, "2")
        self.assertEqual(embed.fields[1].value, "0")
        self.assertEqual(embed.fields[2].value, "<t:1597631921>")
        self.assertEqual(embed.fields[3].value, "140")

    async def test_eightball_command(self):
        context = helpers.MockContext()

        await self.cog.eightball(self.cog, context)

        self.assertIsNone(context.reply.call_args.kwargs.get("embed"))

    async def test_karma_command(self):
        context = helpers.MockContext()

        await self.cog.karma(self.cog, context, user=helpers.MockMember())

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_karmaboard_command(self):
        context = helpers.MockContext()

        await self.cog.karmaboard(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_roll_command(self):
        context = helpers.MockContext()

        await self.cog.roll(self.cog, context, dice="10d10")

        self.assertNotEqual(
            context.reply.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_choose_command(self):
        context = helpers.MockContext()

        await self.cog.choose(self.cog, context, 1, 2, 3)

        self.assertIsNone(context.reply.call_args.kwargs.get("embed"))

    async def test_8ball_command(self):
        context = helpers.MockContext()

        await self.cog.eightball(self.cog, context)

        self.assertIsNone(context.reply.call_args.kwargs.get("embed"))


class ModerationCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = moderation(bot=bot)

    async def test_poll_command(self):
        context = helpers.MockContext()

        await self.cog.poll(self.cog, context, "Test Poll", "Cat", "Dog")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_timeout_command(self):
        context = helpers.MockContext()

        await self.cog.timeout(self.cog, context, helpers.MockMember())

        self.assertTrue(
            context.send.call_args.kwargs["embed"].description.endswith(
                " total infractions."
            )
        )

    async def test_warnings_command(self):
        context = helpers.MockContext()

        await self.cog.warnings(self.cog, context, helpers.MockMember())

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_history_command(self):
        context = helpers.MockContext()
        context.invoked_subcommand = None

        await self.cog.history(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )


class MusicCogTests(unittest.IsolatedAsyncioTestCase):
    pass


class OwnerCogTests(unittest.IsolatedAsyncioTestCase):
    pass


class StocksCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = stocks(bot=bot)

    async def test_stock_command(self):
        context = helpers.MockContext()
        context.invoked_subcommand = None
        context.subcommand_passed = "TSLA"

        await self.cog.stock(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].description,
            "```No stock found for TSLA```",
        )

    async def test_stock_invest_command(self):
        context = helpers.MockContext()

        await self.cog.invest(self.cog, context, symbol="tsla", cash=1)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_stock_profile_command(self):
        context = helpers.MockContext()

        await self.cog.profile(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_stock_bal_command(self):
        context = helpers.MockContext()

        await self.cog.bal(self.cog, context, symbol="tsla")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_stock_sell_command(self):
        context = helpers.MockContext()

        await self.cog.sell(self.cog, context, symbol="tsla", amount="100%")

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_stock_list_command(self):
        context = helpers.MockContext()

        await self.cog.list(self.cog, context)

        self.assertIsNone(context.send.call_args.kwargs.get("embed"))


class UsefulCogTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cog = useful(bot=bot)

    @unittest.skipIf(SKIP_API_TESTS, "Really Slow.")
    async def test_useful_cog_api_commands(self):
        bot.client_session = aiohttp.ClientSession()

        await asyncio.gather(
            *[
                getattr(self, name)()
                for name in dir(self)
                if name.endswith("command") and not name.startswith("test")
            ]
        )

    async def holidays_command(self):
        context = helpers.MockContext()

        await self.cog.holidays(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def format_command(self):
        context = helpers.MockContext()

        code = """```py
        from seven_dwwarfs import Grumpy, Happy, Sleepy, Bashful, Sneezy, Dopey, Doc
        x = {  'a':37,'b':42,

        'c':927}

        x = 123456789.123456789E123456789

        if very_long_variable_name is not None and \
         very_long_variable_name.field > 0 or \
         very_long_variable_name.is_debug:
         z = 'hello '+'world'
        else:
         world = 'world'
         a = 'hello {}'.format(world)
         f = rf'hello {world}'
        if (this
        and that): y = 'hello ''world'
        class Foo  (     object  ):
          def f    (self   ):
            return       37*-2
          def g(self, x,y=42):
              return y
        def f  (   a: List[ int ]) :
          return      37-a[42-u :  y**3]
        def very_important_function(template: str,
        *variables,file: os.PathLike,debug:bool=False,):
            '''Applies `variables` to the `template` and writes to `file`.'''
            with open(file, "w") as f:
             ...
        # fmt: off
        custom_formatting = [
            0,  1,  2,
            3,  4,  5,
            6,  7,  8,
        ]
        # fmt: on
        regular_formatting = [
            0,  1,  2,
            3,  4,  5,
            6,  7,  8,
        ]
        ```"""

        with self.subTest(command="format"):
            await self.cog.format(self.cog, context, code=code)

            self.assertIsNone(context.reply.call_args.kwargs.get("embed"))

    async def translate_command(self):
        with self.subTest(command="translate"):
            context = helpers.MockContext()

            await self.cog.translate(self.cog, context, text="안녕하십니까")

            self.assertIsNone(context.reply.call_args.kwargs.get("embed"))
            self.assertEqual(context.reply.call_args.args[0].lower(), "hello ")

    async def news_command(self):
        with self.subTest(command="news"):
            context = helpers.MockContext()

            await self.cog.news(self.cog, context)

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def google_command(self):
        with self.subTest(command="google"):
            context = helpers.MockContext()

            await self.cog.google(self.cog, context, search="cat")

            self.assertRegex(context.send.call_args.kwargs["embed"].url, url_regex)
            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def image_command(self):
        with self.subTest(command="image"):
            context = helpers.MockContext()

            await self.cog.image(self.cog, context, search="cat")

            self.assertRegex(context.send.call_args.kwargs["embed"].url, url_regex)
            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def weather_command(self):
        context = helpers.MockContext()

        await self.cog.weather(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_currency_command(self):
        context = helpers.MockContext()

        with self.subTest(command="currency"):
            await self.cog.currency(self.cog, context, "3", "usd", "to", "nzd")

            self.assertNotEqual(
                context.send.call_args.kwargs["embed"].color.value, 10038562
            )

    async def test_statuscodes_command(self):
        context = helpers.MockContext()

        await self.cog.statuscodes(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_snipe_command(self):
        context = helpers.MockContext()

        await self.cog.snipe(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )

    async def test_editsnipe_command(self):
        context = helpers.MockContext()

        await self.cog.editsnipe(self.cog, context)

        self.assertNotEqual(
            context.send.call_args.kwargs["embed"].color.value, 10038562
        )
