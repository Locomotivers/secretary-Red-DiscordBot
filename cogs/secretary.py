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
        self.f_req = dataIO.load_json(fR_path)
        self.bot = bot
        self.f_hist =   {"name": "",
                        "balance": 0,
                        "comment": "",
                        "updated": ""
                        }

    def mange_fund(self, user, _op, amount, comment):
        server = user.server
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        self.f_hist["name"] = user.name
        self.f_hist["comment"] = comment
        self.f_hist["updated"] = timestamp

        if _op == "add":
            self.f_hist["balance"] += amount
        elif _op == "sub":
            self.f_hist["balance"] -= amount
        elif _op == "set":
            self.f_hist["balance"] = amount

        dataIO.save_json("data/secretary/fund.json", self.f_hist)

    def recieve_request(self, user, _op, amount, comment):
        server = user.server
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        if user.id == get_value("data/secretary/fundrequest.json", user.id):
            if _op == "add" or _op == "set":
                if self.f_req[user.id]["balance"] < 0:
                    self.f_req[user.id]["balance"]  = amount
                else:
                    self.f_req[user.id]["balance"]  += amount
                self.f_req[user.id]["type"]  = "deposit"
            else:
                if self.f_req[user.id]["balance"] > 0:
                    self.f_req[user.id]["balance"]  = amount
                else:
                    self.f_req[user.id]["balance"]  += amount
                self.f_req[user.id]["type"]  = "withdraw"
            self.f_req[user.id]["comment"]  = comment
            self.f_req[user.id]["updated"]  = timestamp

        else:
            self.f_req[user.id] =   {"name" : user.name,
                                    "amount": amount,
                                    "type": "deposit" if (_op == "add") or (_op == "set") else "withdraw",
                                    "comment": comment,
                                    "updated": timestamp
                                    }

        dataIO.save_json("data/secretary/fundrequest.json", self.f_req)

    def comment_filter(self, msg):
        msg = message.content.split(" ").slice(1);
        command = args[0];
        amount = args[1];
        comment = "";
        for x in xrange(2,len(args)):
            comment += args[x];
        return comment



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

    @commands.command(pass_context=True, no_pm=True)
    @check.mod_or_permissions(administrator=True)
    async def fund(self, ctx, amount : SetParser):
        """Sets, Adds, Substracts the fund

        Examples:
            fund 100 I Like it - sets 100
            fund +100 I Like it - adds 100
            fund -100 I dont like it - substracts 100
        """
        author = ctx.message.author
        comment = self.op.comment_filter(ctx)

        self.op.mange_fund(author, amount.operation, amount.sum, comment)

        if amount.operation == "add":
            fHLogger.info("{}({}) added {} silver because {} ".format(
                            author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) added {} silver because {} ".format(
                                author.name, author.id, amount.sum, comment))
        elif amount.operation == "sub":
            fHLogger.info("{}({}) subtracts {} silver because {} ".format(
                            author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) subtracts {} silver because {} ".format(
                                author.name, author.id, amount.sum, comment))
        elif amount.operation == "set":
            fHLogger.info("{}({}) set {} silver because {} ".format(
                            author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) set {} silver because {} ".format(
                                author.name, author.id, amount.sum, comment))

    @commands.command(pass_context=True, no_pm=True)
    async def ckbal(self):
      await self.bot.say("{} silver currently left towards to island fund.".
      format(get_value("data/secretary/fund.json", "balance")))

    @commands.command(pass_context=True, no_pm=True)
    async def freq(self, ctx, amount : SetParser)
        """Request fund toward island
        This request has to be accepted manually, so please be patient.
        Also any withdrawing request will be ignored by unapproved desposit request!

        Examples:
            freq 100 comment or
            freq +100 comment - Request to deposit the fund.
            freq -100 comment - Request to withdraw the fund.
        """
        author = ctx.message.author
        comment = self.op.comment_filter(ctx)

        if amount.operation == "add" or amount.operation == "set":
            self.op.recieve_request(author, amount.operation, amount.sum, comment)
            fRLogger.info("{}({}) has requested {} silver(s) to be deposited because {} "
            .format(author.name, author.id, amount.sum, comment))
            await self.bot.say("{}({}) has requested {} silver(s) be deposited because {} "
            .format(author.name, author.id, amount.sum, comment))
        elif amount.operation == "sub":
            self.op.recieve_request(author, amount.sum, comment)
            fRLogger.info(("{}({}) has requested {} silver(s) to be withdrawed because {} "
            .format(author.name, author.id, amount.operation, amount.sum, comment))
            await self.bot.say("{}({}) has requested {} silver(s) to be withdrawed because {} "
            .format(author.name, author.id, amount.sum, comment))


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
