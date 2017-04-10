from discord.ext import commands
from .utils.dataIO import dataIO
from .utils.dataIO import get_value
from .utils import checks
from __main__ import user_allowed
from datetime import datetime
import time
import os
import re
import logging

class Op:

    def __init__(self, bot, fHL_path, fR_Path):
        self.f_hist = dataIO.load_json(fHL_path)
        #self.f_req = dataIO.load_json(fR_path) #TODO
        self.bot = bot
        self.f_hist =   {"name": "",
                        "balance": 0,
                        "comment": "",
                        "updated": ""
                        }

    def add_fund(self, user, amount, comment):
        server = user.server
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        self.f_hist["name"] = user.name
        self.f_hist["balance"] += amount
        self.f_hist["comment"] = comment
        self.f_hist["updated"] = timestamp

        self.save_hist()

    def sub_fund(self, user, amount, comment):
        server = user.server
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        self.f_hist["name"] = user.name
        self.f_hist["balance"] -= amount
        self.f_hist["comment"] = comment
        self.f_hist["updated"] = timestamp

        self.save_hist()

    def set_fund(self, user, amount, comment):
        server = user.server
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        self.f_hist["name"] = user.name
        self.f_hist["balance"] = amount
        self.f_hist["comment"] = comment
        self.f_hist["updated"] = timestamp

        self.save_hist()

    def save_hist(self):
        dataIO.save_json("data/secretary/fund.json", self.f_hist)

    def get_balance(self):
        return get_value("data/secretary/fund.json","balance")


class SetParser:
    def __init__(self, argument):
        allowed = ("+", "-")
        if argument and argument[0] in allowed:
            try:
                self.sum = int(argument)
            except:
                raise
            if self.sum < 0:
                self.operation = "sub"
            elif self.sum > 0:
                self.operation = "add"
            else:
                raise
            self.sum = abs(self.sum)
        elif argument.isdigit():
            self.sum = int(argument)
            self.operation = "set"
        else:
            raise


class Secretary:
    """Secretary Commands"""

    def __init__ (self, bot):
        self.bot = bot
        self.op = Op(bot, "data/secretary/fund.json",
        "data/secretary/fundrequest.json")

    # @commands.group(name="fund", pass_context=True)
    # async def _fund(self, ctx):
    #     """Fund operations"""
    #     if ctx.invoked_subcommand is None:
    #         await send_cmd_help(ctx)

    # @_fund.command(pass_context=True, no_pm=True)
    #@checks.admin_or_permissions(administrator=True)

    @commands.command(pass_context=True, no_pm=True)
    async def fund(self, ctx, amount : SetParser, comment: str):
        """Sets, Adds, Substracts the fund

        Examples:
            fund 100 "I Like it" - sets 100
            fund +100 "I Like it" - adds 100
            fund -100 "I dont like it" - substracts 100
        """
        author = ctx.message.author

        if amount.operation == "add":
            self.op.add_fund(author, amount.sum, comment)
            fHLogger.info("{}({}) added {} silver because {} ".format(
                            author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) added {} silver because {} ".format(
                                author.name, author.id, amount.sum, comment))
        elif amount.operation == "sub":
            self.op.sub_fund(author, amount.sum, comment)
            fHLogger.info("{}({}) subtracts {} silver because {} ".format(
                            author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) subtracts {} silver because {} ".format(
                                author.name, author.id, amount.sum, comment))
        elif amount.operation == "set":
            self.op.set_fund(author, amount.sum, comment)
            fHLogger.info("{}({}) set {} silver because {} ".format(
                            author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) set {} silver because {} ".format(
                                author.name, author.id, amount.sum, comment))

    @commands.command(pass_context=True, no_pm=True)
    async def ckbal(self):
      await self.bot.say("{} silver currently left towards to island fund.".format(self.op.get_balance()))

def check_folders():
    if not os.path.exists("data/secretary"):
        print("Creating data/secretary folder")
        os.makedirs("data/secretary")

def check_files(f):
    fpath = "data/secretary/{}.json".format(f)
    if not dataIO.is_valid_json(fpath):
        print("Creating empty {}.json...".format(f))
        dataIO.save_json(fpath, {})




def setup(bot):
    global fHLogger
    global fRLogger

    check_folders()
    check_files("fund")
    check_files("fundrequest")

    fHLogger = logging.getLogger("red.FundHist")
    if fHLogger.level == 0:
        fHLogger.setLevel(logging.INFO)

        fHLh = logging.FileHandler(
        filename='data/secretary/fundHistory.log', encoding='utf-8', mode='a')
        fHLh.setFormatter(logging.Formatter(
        '%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))

        fHLogger.addHandler(fHLh)

    fRLogger = logging.getLogger("red.FundReq")
    if fRLogger.level == 0:
        fRLogger.setLevel(logging.INFO)

        fRLh = logging.FileHandler(
        filename='data/secretary/fundReqHistory.log', encoding='utf-8', mode='a')
        fRLh.setFormatter(logging.Formatter(
         '%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))

        fRLogger.addHandler(fRLh)

    #bot.add_listener(n.checkCC, "on_message")
    bot.add_cog(Secretary(bot))
