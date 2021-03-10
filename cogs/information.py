import discord
from discord.ext import commands
import textwrap
from .utils import util
import psutil
import time
import inspect
import os


class information(commands.Cog):
    """Commands that give information about the bot or server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.process = psutil.Process()

    @commands.command()
    async def ping(self, ctx):
        """Check how the bot is doing."""
        start = time.monotonic()
        pinger = await ctx.send("Pinging...")
        diff = "%.2f" % (1000 * (time.monotonic() - start))

        embed = discord.Embed()
        embed.add_field(name="Ping", value=f"`{diff} ms`")
        embed.add_field(name="Latency", value=f"`{round(self.bot.latency*1000, 2)} ms`")

        await pinger.edit(content=None, embed=embed)

    @commands.command()
    async def usage(self, ctx):
        """Shows the bot's memory and cpu usage."""
        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()

        embed = discord.Embed(color=discord.Color.teal())
        embed.add_field(name="Memory Usage: ", value=f"**{memory_usage:.2f} MiB**")
        embed.add_field(name="CPU Usage:", value=f"**{cpu_usage}%**")
        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        """Shows the bots uptime."""
        await ctx.send(f"**{util.time_since(self.bot.uptime)}**")

    @commands.command()
    async def roles(self, ctx, member: discord.Member):
        """Sends a list of the roles a member has.

        member: discord.Member
            The member to get the roles of.
        """
        role_list = []
        for role in member.roles:
            if str(role.name) != "@everyone":
                role_list.append(f"*{role.name}*")
        await ctx.send(
            embed=discord.Embed(
                title=str(role_list)[1:-1], color=discord.Color.dark_gold()
            )
        )

    @commands.command(
        name="server",
        aliases=["guild", "info"],
    )
    async def server_info(self, ctx):
        """Sends an embed of server information."""
        created = util.time_since(ctx.guild.created_at, precision="days")
        region = ctx.guild.region
        roles = len(ctx.guild.roles)
        member_count = ctx.guild.member_count
        owner = ctx.guild.owner
        online_users = sum(
            [member.status is discord.Status.online for member in ctx.guild.members]
        )
        offline_users = sum(
            [member.status is discord.Status.offline for member in ctx.guild.members]
        )
        dnd_users = sum(
            [member.status is discord.Status.dnd for member in ctx.guild.members]
        )
        idle_users = sum(
            [member.status is discord.Status.idle for member in ctx.guild.members]
        )
        offline = util.get_matching_emote(ctx.guild, ":offline:")
        online = util.get_matching_emote(ctx.guild, ":online:")
        dnd = util.get_matching_emote(ctx.guild, ":dnd:")
        idle = util.get_matching_emote(ctx.guild, ":idle:")
        embed = discord.Embed(colour=discord.Colour.blurple())
        embed.description = textwrap.dedent(
            f"""
                **Server information**
                Created: {created}
                Region: {region}
                Owner: {owner}

                **Member counts**
                Members: {member_count:,} Roles: {roles}

                **Member statuses**
                {online} {online_users:,} {dnd} {dnd_users:,} {idle} {idle_users:,} {offline} {offline_users:,}
            """
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(name="user", aliases=["user_info", "member", "member_info"])
    async def user_info(self, ctx, member: discord.Member = None) -> None:
        """Sends info about a member.

        member: discord.Member
            The member to get info of defulting to the invoker.
        """
        if member is None:
            member = ctx.author
        embed = await self.create_user_embed(ctx, member)
        await ctx.send(embed=embed)

    async def create_user_embed(self, ctx, member: discord.Member) -> discord.Embed:
        """Creates an embed containing information on the `user`."""
        created = util.time_since(member.created_at, max_units=3)
        name = str(member)
        if member.nick:
            name = f"{member.nick} ({name})"
        joined = util.time_since(member.joined_at, max_units=3)
        roles = ", ".join(role.mention for role in member.roles[1:])
        fields = [
            (
                "User information",
                textwrap.dedent(
                    f"""
                    Created: {created}
                    Profile: {member.mention}
                    ID: {member.id}
                """
                ).strip(),
            ),
            (
                "Member information",
                textwrap.dedent(
                    f"""
                    Joined: {joined}
                    Roles: {roles or None}
                """
                ).strip(),
            ),
        ]
        embed = discord.Embed(
            title=name,
        )
        for field_name, field_content in fields:
            embed.add_field(name=field_name, value=field_content, inline=False)
        embed.set_thumbnail(url=member.avatar_url_as(static_format="png"))
        embed.colour = member.top_role.colour if roles else discord.Colour.blurple()
        return embed

    @commands.command()
    async def source(self, ctx, *, command: str = None):
        """Gets the source code of a command from github.

        command: str
            The command to find the source code of.
        """
        if command is None:
            return await ctx.send("https://github.com/Singularitat/snakebot")

        if command == "help":
            src = type(self.bot.help_command)
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command)
            if obj is None:
                return await ctx.send("Could not find command.")

            src = obj.callback.__code__
            filename = src.co_filename

        lines, lineno = inspect.getsourcelines(src)
        cog = os.path.relpath(filename).replace("\\", "/")

        final_url = f"<https://github.com/Singularitat/snakebot/blob/main/{cog}#L{lineno}-L{lineno + len(lines) - 1}>"
        if len(f'```py\n{"".join(lines)}```') <= 2000:
            await ctx.send(f'```py\n{("".join(lines)).replace("`", "")}```')
        await ctx.send(final_url)


def setup(bot: commands.Bot) -> None:
    """Starts information cog."""
    bot.add_cog(information(bot))
