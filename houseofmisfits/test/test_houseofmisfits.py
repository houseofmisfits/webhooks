"""
This file is in place to make sure commits don't suddenly break the server bots.

"""

import os

import unittest

import yaml

from houseofmisfits import MessageScheduler

SCHEDULES_SUPPORTED = [
    'weekly',
    'hourly',
    'minutely'
]


class TestHouseOfMisfits(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestHouseOfMisfits, self).__init__(*args, **kwargs)
        self.rules = MessageScheduler.load_rules()
        self.schedules = MessageScheduler.load_schedules()

    def test_valid_rules_yaml_syntax(self):
        rules_dir = os.getenv('WORKSPACE') + '/rules'
        for file in os.listdir(rules_dir):
            with open(rules_dir + '/' + file, 'r') as yaml_file:
                try:
                    yaml.safe_load(yaml_file)
                except Exception as e:
                    self.fail("Uh oh, looks like the rules file {} has a bad syntax.\n\nException:\n{}".format(file, e))

    def test_valid_schedules_yaml_syntax(self):
        schedules_dir = os.getenv('WORKSPACE') + '/schedules'
        for file in os.listdir(schedules_dir):
            with open(schedules_dir + '/' + file, 'r') as yaml_file:
                try:
                    yaml.safe_load(yaml_file)
                except Exception as e:
                    self.fail(
                        "Uh oh, looks like the schedules file {} has a bad syntax.\n\nException:\n{}".format(file, e))

    def test_rules_root_is_dict(self):
        self.assertIsInstance(self.rules, dict)

    def test_schedules_root_is_list(self):
        self.assertIsInstance(self.schedules, list)

    def test_all_rules_are_list_of_str(self):
        for rule_name in self.rules:
            message_list = self.rules[rule_name]
            self.assertIsInstance(message_list, list)
            for message in message_list:
                self.assertIsInstance(message, str)

    def test_all_schedules_define_webhook(self):
        for schedule in self.schedules:
            self.assertIn('webhook', schedule)
            self.assertIsInstance(schedule['webhook'], str)

    def test_schedule_types_valid(self):
        for s in self.schedules:
            self.assertIn(s['schedule']['type'], SCHEDULES_SUPPORTED)

    def test_hourly_minutely_have_int_interval(self):
        for s in self.schedules:
            if s['schedule']['type'] in ['minutely', 'hourly']:
                self.assertIsInstance(s['schedule']['interval'], int)