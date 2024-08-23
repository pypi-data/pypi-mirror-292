import discord
from parsing.command_parser import CommandParser
from parsing.enums.command_type import CommandType
from computing.compute import Compute
from json_handling.gambling.gamble import Gamble
from json_handling.roll_saving.roll_save import RollSave
import message_validator as mv
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
testing_messages = True

class HighRoller:
    def __init__():
        pass

    async def handle_expr(message: discord.Message, compute: Compute, rollSave: RollSave, commandParser: CommandParser):
        result = compute.compute_expr(commandParser.stack[1])
        if compute.error:
            await message.channel.send('https://tenor.com/view/blm-gif-25815938')
        else:
            rollSave.add_rolls_to_json()
            to_send = ""
            i = 0
            for i in range(len(compute.cocked_rolls)):
                to_send += "Honor the cock. Roll " + str(compute.cocked_rolls[i][1]) + " was cocked. It would have been " + str(compute.cocked_rolls[i][0]) + "\n"
                to_send += str(result[0]) + '\nDetails: ' + str(compute.all_lists_of_rolls) + "\nAverage: " + str(result[1])
            if (len(to_send)) > 2000:
                to_send_list = [(to_send[i:i+2000]) for i in range(0, len(to_send), 2000)]
                for to_send in to_send_list:
                    await message.channel.send(to_send)
            else:
                await message.channel.send(to_send)

    async def handle_gamble_start(message: discord.Message, gamble: Gamble):
        if not gamble.gambling():
            await message.channel.send('odds or evens?')
            gamble.update_gambling_state(True)

    async def handle_gamble_bet(gamble: Gamble, commandParser: CommandParser):
        if await gamble.determine_bet(commandParser.stack[1].token_info.lexeme):
            if gamble.gambling():
                await gamble.determine_result()
                gamble.update_gambling_state(False)

    async def handle_recall_rolls(message:discord.Message, rollSave: RollSave, commandParser: CommandParser):
        if len(commandParser.stack) == 2:
            rollSave.get_rolls_from_json()
        elif len(commandParser.stack) == 7:
            rollSave.get_rolls_from_json(
                int(commandParser.stack[3].token_info.lexeme), 
                commandParser.stack[5].token_info.lexeme
            )
        await message.channel.send(file=discord.File('bar_plots/bar_plot_' + message.author.name + '.png'))

    async def handle_error(message:discord.Message):
        await message.channel.send("https://tenor.com/view/blm-gif-25815938")

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))

    @client.event
    async def on_message(self, message: discord.Message):
        if not mv.channel_valid(message) and mv.message_is_command(message):
            self.handle_error(message)
        elif mv.message_is_command(message):
            compute = Compute()
            gamble = Gamble(message, compute)
            rollSave = RollSave(message, compute)
            commandParser = CommandParser(message.content)
            commandParser.parse_init()
            match commandParser.command_type:
                case CommandType.EXPR:
                    await self.handle_expr(message, compute, rollSave, commandParser)
                case CommandType.GAMBLE_START:
                    await self.handle_gamble_start(message, gamble)
                case CommandType.GAMBLE_BET:
                    await self.handle_gamble_bet(gamble, commandParser)
                case CommandType.RECALL_ROLLS:
                    await self.handle_recall_rolls(message, rollSave, commandParser)
                case CommandType.ERROR:
                    await self.handle_error(message)
                case _:
                    pass

    with open('BOT-KEY', 'r') as file: bot_key = file.read().rstrip()
    client.run(bot_key)

    def printhehe():
        print('hehe')