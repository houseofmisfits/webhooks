import os
from datetime import date, timedelta, datetime, time

import yaml
import logging

from random import randint

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

        debug_output_path = 'output.html'
        with open(debug_output_path, 'w') as html_file:
            html_file.write(content)

    def run_pending(self):
        if date.today() > self.date:
            self.date = date.today()
            self.refresh()
        for message in self.messages:
            if datetime.now() >= message.scheduled_time:
                logger.info("Sending message with {}: \n\n```\n{}\n```".format(message.webhook_name, message.message))
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
            elif schedule_type == 'random':
                self.schedule_randomly(scheduled_message)
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

    def schedule_randomly(self, message):
        logger.debug('Setting message {} to intermittent schedule'.format(message['message']))
        webhook = message['webhook']
        unflat_text = message['message']
        schedule = message['schedule']
        if 'days' in schedule and weekdays[self.date.weekday()] not in schedule['days']:
            return
        if 'end_date' in schedule and schedule['end_date'] <= self.date:
            return
        start_time = datetime.combine(self.date, time.fromisoformat(schedule['start_time']))
        end_time = datetime.combine(self.date, time.fromisoformat(schedule['end_time']))
        min_interval, max_interval = (int(mins) * 60 for mins in schedule['minutes_apart_range'].split('-'))
        for message_time in self.get_random_times(start_time, end_time, min_interval, max_interval):
            if datetime.now() > message_time:
                logger.debug('Skipping message {}: already past {}'.format(unflat_text, message_time.isoformat()))
                continue
            new_message = Message(webhook, unflat_text, self.rules, message_time)
            self.messages.append(new_message)

    @staticmethod
    def get_random_times(start_time, end_time, min_interval_secs, max_interval_secs):
        random_times = []
        message_time = start_time + timedelta(seconds=randint(min_interval_secs, max_interval_secs) - min_interval_secs)
        while message_time <= end_time:
            random_times.append(message_time)
            message_time += timedelta(seconds=randint(min_interval_secs, max_interval_secs))
        return random_times


    @staticmethod
    def load_rules():
        rules = {}
        rules_dir = 'rules'
        for file in os.listdir(rules_dir):
            with open(rules_dir + '/' + file, 'r') as yaml_file:
                rule = yaml.safe_load(yaml_file)
                rules.update(rule)
        return rules

    @staticmethod
    def load_schedules():
        schedules = []
        schedules_dir = 'schedules'
        for file in os.listdir(schedules_dir):
            with open(schedules_dir + '/' + file, 'r') as yaml_file:
                schedule = yaml.safe_load(yaml_file)
                schedules += schedule
        return schedules
