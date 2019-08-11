import os
from datetime import date, timedelta, datetime, time

import yaml
import logging

from houseofmisfits import Message

logger = logging.getLogger(__name__)


weekdays = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


class MessageScheduler:
    def __init__(self):
        self.messages = []
        self.date = date.today()
        self.rules = MessageScheduler.load_rules()
        logger.info("Loaded rules, {} rules total".format(len(self.rules)))

    @staticmethod
    def simulate_week():
        """
        Grabs the message for the next 7 days (starting from tomorrow)
        """
        m = MessageScheduler()
        content = '<html>'
        for day in (date.today() + timedelta(days=n) for n in range(1, 8)):
            m.date = day
            m.refresh(False)
            content += "<h1>Potential messages for {}</h1>".format(day.strftime('%a %m/%d'))
            content += "<table><tr><td>Webhook</td><td>Time</td><td>Message</td></tr>"
            messages = sorted(m.messages, key=lambda x: x.scheduled_time)
            for message in messages:
                content += "<tr><td><b>{}</b></td><td><b>{}</b></td><td>{}</td></tr>".format(
                    message.webhook_name,
                    message.scheduled_time.strftime('%H:%M'),
                    message.message
                )
            content += "</table>"
        content += "</html>"

        debug_output_path = os.getenv('WORKSPACE') + '/output.html'
        with open(debug_output_path, 'w') as html_file:
            html_file.write(content)

    def run_pending(self):
        if date.today() > self.date:
            self.refresh()
            self.date = date.today()
        for message in self.messages:
            if datetime.now() >= message.scheduled_time:
                logger.info("Sending message with {}: {}".format(message.webhook_name, message.message))
                message.send()
                self.messages.remove(message)
                logger.debug("{} messages left to send".format(len(self.messages)))

    def refresh(self, set_date=True):
        logger.info("Loading new schedules for {}".format(self.date.isoformat()))
        self.messages.clear()
        for scheduled_message in MessageScheduler.load_schedules():
            schedule_type = scheduled_message['schedule']['type']
            if schedule_type == 'hourly':
                self.schedule_hourly(scheduled_message)
            elif schedule_type == 'weekly':
                self.schedule_weekly(scheduled_message)
            elif schedule_type == 'minutely':
                self.schedule_minutely(scheduled_message)
            else:
                raise KeyError(schedule_type)
        if set_date:
            self.date = date.today()
        logger.info("All messages added, {} messages in total".format(len(self.messages)))

    def schedule_hourly(self, message):
        logger.debug('Setting message {} to hourly schedule'.format(message['message']))
        start_time = datetime.combine(self.date, time(0, 0, 0))
        interval = message['schedule']['interval']
        webhook = message['webhook']
        unflat_text = message['message']
        for message_time in (start_time + timedelta(hours=n) for n in range(0, 24, interval)):
            if datetime.now() > message_time:
                logger.debug('Skipping message {}: already past {}'.format(unflat_text, message_time.isoformat()))
                continue
            new_message = Message(webhook, unflat_text, self.rules, message_time)
            self.messages.append(new_message)

    def schedule_minutely(self, message):
        logger.debug('Setting message {} to minutely schedule'.format(message['message']))
        start_time = datetime.combine(self.date, time(0, 0, 0))
        interval = message['schedule']['interval']
        webhook = message['webhook']
        unflat_text = message['message']
        for message_time in (start_time + timedelta(minutes=n) for n in range(0, 1440, interval)):
            if datetime.now() > message_time:
                logger.debug('Skipping message {}: already past {}'.format(unflat_text, message_time.isoformat()))
                continue
            new_message = Message(webhook, unflat_text, self.rules, message_time)
            self.messages.append(new_message)

    def schedule_weekly(self, message):
        day_of_week = weekdays[self.date.weekday()]
        webhook = message['webhook']
        unflat_text = message['message']
        if day_of_week in message['schedule']['days']:
            dt = self.date
            h, m = message['schedule']['time'].split(':')
            tm = time(int(h), int(m))
            message_time = datetime.combine(dt, tm)
            if datetime.now() > message_time + timedelta(minutes=15):
                logger.debug('Skipping message {}: already past {}'.format(unflat_text, message_time.isoformat()))
                return
            new_message = Message(webhook, unflat_text, self.rules, message_time)
            self.messages.append(new_message)

    @staticmethod
    def load_rules():
        rules = {}
        rules_dir = os.getenv('WORKSPACE') + '/rules'
        for file in os.listdir(rules_dir):
            with open(rules_dir + '/' + file, 'r') as yaml_file:
                rule = yaml.safe_load(yaml_file)
                rules.update(rule)
        return rules

    @staticmethod
    def load_schedules():
        schedules = []
        schedules_dir = os.getenv('WORKSPACE') + '/schedules'
        for file in os.listdir(schedules_dir):
            with open(schedules_dir + '/' + file, 'r') as yaml_file:
                schedule = yaml.safe_load(yaml_file)
                schedules += schedule
        return schedules
