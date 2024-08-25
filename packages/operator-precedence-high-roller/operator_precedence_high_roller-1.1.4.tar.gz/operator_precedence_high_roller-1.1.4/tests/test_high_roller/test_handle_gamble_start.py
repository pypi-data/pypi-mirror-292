import pathlib
import sys
import os
ROOT_PATH = pathlib.Path(__file__).parents[2]
sys.path.append(os.path.join(ROOT_PATH, ''))
from operator_precedence_high_roller import high_roller
from operator_precedence_high_roller.json_handling.gambling.gamble import Gamble
from operator_precedence_high_roller.computing.compute import Compute
from operator_precedence_high_roller.parsing.command_parser import CommandParser
from mock_classes.mock_message_attributes.mock_author import MockAuthor
from mock_classes.mock_message_attributes.mock_channel import MockChannel
from mock_classes.mock_message import MockMessage
from unittest import IsolatedAsyncioTestCase

class TestHandleGambleStart(IsolatedAsyncioTestCase):
    async def test_not_gambling_true(self):
        author = MockAuthor(name = 'test_1234')
        channel = MockChannel(name = 'rolls_test_1234')
        message = MockMessage(author, channel, '!gamble')
        compute = Compute()
        gamble = Gamble(message, compute)
        gamble.update_gambling_state(False)
        commandParser = CommandParser(message.content)
        commandParser.parse_init()
        await high_roller.handle_gamble_start(message, gamble)
        self.assertTrue(gamble.gambling())

    async def test_not_gambling_false(self):
        author = MockAuthor(name = 'test_1234')
        channel = MockChannel(name = 'rolls_test_1234')
        message = MockMessage(author, channel, '!gamble')
        compute = Compute()
        gamble = Gamble(message, compute)
        gamble.update_gambling_state(True)
        commandParser = CommandParser(message.content)
        commandParser.parse_init()
        await high_roller.handle_gamble_start(message, gamble)
        self.assertTrue(gamble.gambling())