import appdaemon.plugins.hass.hassapi as hass
from queue import Queue
import threading
import random
import datetime
import time
import localvars

class NotificationEngine(hass.Hass):
    
    def initialize(self):
        # Create Queue & Create worker thread for Telegram only
        self.telegram_queue = Queue(maxsize=0)
        t1 = threading.Thread(target=self.worker_telegram)
        t1.daemon = True
        t1.start()
        # Create Queue & Create worker thread for Speech only
        self.voice_queue = Queue(maxsize=0)
        t2 = threading.Thread(target=self.worker_speech)
        t2.daemon = True
        t2.start()
        # Listen for Notification Repo
        self.listen_event(self.notification_repo, event='MQTT_MESSAGE', namespace='mqtt', topic = 'notifications/newmsg')
        self.listen_event(self.notification_repo, event='MQTT_MESSAGE', namespace='mqtt', topic = 'notifications/newmsg/alert')
        self.listen_event(self.notification_repo, event='MQTT_MESSAGE', namespace='mqtt', topic = 'notifications/newmsg/telegram')

    def notification_repo(self, event, event_data, kwargs):
        topic =  event_data['topic']
        payload = event_data['payload']
        if 'call: ' in payload:
            if payload == 'call: weekend_alarm':
                sep = '.'
                int1 = self.get_state("sensor.bom_feels_like_c")
                int1 = int1.split(sep, 1)[0]
                int2 = self.get_state("sensor.dark_sky_daytime_high_apparent_temperature_0")
                int2 = int2.split(sep, 1)[0]
                rand1 = ["The temperature today will reach a high of ", "The max temperature today is going to be ", "Today it will get to a high of "]
                current_time = self.time()
                current_time = current_time.strftime("%I:%M %p")
                high_tide = self.get_state("sensor.worldtidesinfo", attribute="high_tide_time")
                payload = "Good morning. It's " + current_time + ", the weather in Oak Park is " + int1 + " degrees and " + self.get_state("sensor.dark_sky_summary").lower() + ". " + (random.choice(rand1)) + int2 + ", and high tide in Torquay is at " + high_tide + "."
                self.announce(topic, payload)
            elif payload == 'call: weekday_alarm':
                sep = '.'
                int1 = self.get_state("sensor.bom_feels_like_c")
                int1 = int1.split(sep, 1)[0]
                int2 = self.get_state("sensor.dark_sky_daytime_high_apparent_temperature_0")
                int2 = int2.split(sep, 1)[0]
                rand1 = ["It's ", "The time is ", "The time now is ", "The time right now is "]
                rand2 = ["the weather is ", "the weather in Oak Park is "]
                rand3 = ["The max temperature today is going to be ", "Today it will get to a high of "]
                #rand4 = ["In current traffic ", "Right now ", "If you leave now, ", "If you left right now, "]
                rand5 = ["right now shows ", "currently has a status of ", "currently shows "]
                current_time = self.time()
                current_time = current_time.strftime("%-I %-M %p")
                payload = "Good morning. " + (random.choice(rand1)) + current_time + ", " + (random.choice(rand2)) + int1 + " degrees and " + self.get_state("sensor.dark_sky_summary").lower() + ". " + (random.choice(rand3)) + int2 + ", and the Craigieburn line " + (random.choice(rand5)) + self.get_state("sensor.travel_train_craigieburn").lower() + "."
                #self.announce(topic, payload)
                self.call_service("mqtt/publish", topic="alexa/tts/LivingRoom_R", payload=payload)
            elif payload == 'call: tv_waiting_wifi':
                self.announce(topic, "Waiting for the TV to connect to the network.")
            elif payload == 'call: welcome_home':
                if self.get_state('group.kyle') == 'home' and self.get_state('group.sarah') != 'home':
                    self.announce(topic, "Welcome home Kyle. I have the following notifications for you:")
                elif self.get_state('group.kyle') != 'home' and self.get_state('group.sarah') == 'home':
                    self.announce(topic, "Welcome home Sarah. I have the following notifications for you:")
                else:
                    self.announce(topic, "Welcome home. I have the following notifications for you:")
            elif payload == 'call: garage_door_open':
                self.announce(topic, "The garage door is currently open.")
            elif payload == 'call: dishwasher_ready':
                self.announce(topic, "The dishwasher has finished and is ready to be emptied.")
            elif payload == 'call: washing_ready':
                self.announce(topic, "The washing machine has finished and is ready to be emptied.")
        else:
            self.announce(topic, payload)

    def announce(self, topic, payload):
        if topic == 'notifications/newmsg/alert':
            payload = 'Alert: ' + payload
            self.voice_queue.put(payload)
        elif topic == 'notifications/newmsg/telegram' or self.get_state(entity='input_boolean.speech_notifications') == 'off':
            self.telegram_queue.put(payload)
        elif topic == 'notifications/newmsg':
            self.voice_queue.put(payload)

    def worker_telegram(self):
        while True:
            try:
                # Wait for input. Loop with a 1 second delay to ensure messages received in order
                self.log("telegram_queue empty, waiting for input.")
                while self.telegram_queue.empty() == True:
                    time.sleep(1)
                # Get text to say
                self.log("Starting telegram_queue.")
                text = self.telegram_queue.get()
                self.call_service("notify/telegram", message=text)
                time.sleep(1)
                # Rinse and repeat
                self.telegram_queue.task_done()
            except:
                self.log("Error with worker_telegram1.")

    def worker_speech(self):
        while True:
            try:
                self.log("voice_queue empty. Waiting for input.")
                while self.voice_queue.empty() == True:
                    time.sleep(1)
                voice_queue_text = self.voice_queue.get()
                while self.voice_queue.empty() == False:
                    self.log("voice_queue: Combining multiple inputs into single message.")
                    voice_queue_text = voice_queue_text + ' ' + self.voice_queue.get()
                self.log("Waiting for previous message to complete")
                loop = 0
                while localvars.Speech_InUse == 1:
                    time.sleep(0.25)
                    if loop < 1:
                        self.log("Inside waiting for previous message to complete loop")
                    loop = loop + 1
                    if loop > 60:
                        self.log("Stuck in loop for 15 seconds, exiting.")
                        self.call_service("notify/telegram", message="Stuck in loop for 15 seconds, exiting.")
                        break
                self.log("Loop completed")
                localvars.Speech_InUse = 1
                #self.log("voice_queue: Selecting output device.")
                output_device = 'media_player.livingroom_sonos'
                #self.log("Storing volume for restore")
                volume = self.get_state(entity=output_device, attribute="volume_level")
                self.log(volume)
                if 'Alert: ' in voice_queue_text:
                    self.log("Alert is on, sending via telegram")
                    telegram_text = voice_queue_text.replace('<break strength="x-strong"/>', ' ')
                    voice_queue_text = voice_queue_text.replace('Alert: ', '')
                    self.log("voice_queue: Sending to telegram: " + telegram_text )
                    self.call_service("notify/telegram", message=telegram_text)
                    alert=1
                else:
                    alert=0
                if self.get_state(entity=output_device, attribute="media_artist") != 'Joanna':
                    self.call_service('media_player/sonos_snapshot', entity_id=output_device)
                self.worker_speech_start_handle = self.listen_state(self.speech_start, entity=output_device, attribute='media_artist', new='Joanna', output_device=output_device, volume=volume, alert=alert)
                self.log("voice_queue: Calling TTS service with message: " + voice_queue_text)
                self.call_service("tts/amazon_polly_say", entity_id=output_device, message='<speak><break time="0.5s" />' + voice_queue_text + '<break time="0.5s" /></speak>')
                # Rinse and repeat
                self.log("Worker3 task complete. Speech notification sent.")
                self.voice_queue.task_done()
            except:
                self.log("Error with worker_speech.")                

    def speech_start(self, entity, attribute, old, new, kwargs):
        self.log("Reached speech_start")
        self.speech_end_handle = self.listen_state(self.speech_end, entity=kwargs['output_device'], old='playing', new='paused', output_device=kwargs['output_device'], volume=kwargs['volume'])
        if kwargs['alert'] == 1:
            self.log("Alert is on, setting volume to 0.5")
            self.call_service('media_player/volume_set', entity_id=kwargs['output_device'], volume_level='0.5')
        else:
            self.call_service('media_player/volume_set', entity_id=kwargs['output_device'], volume_level='0.35')
        try:
            self.cancel_listen_state(self.worker_speech_start_handle)
        except:
            self.log("self.worker_speech_start_handle did not exist to be cancelled.")       

    def speech_end(self, entity, attribute, old, new, kwargs):
        self.log("Reached speech_end")
        try:
            self.cancel_listen_state(self.speech_end_handle)
        except:
            self.log("self.speech_end_handle did not exist to be cancelled.")
        self.log("Restoring volume to: " + str(kwargs['volume']))
        self.call_service('media_player/volume_set', entity_id=kwargs['output_device'], volume_level=kwargs['volume'])
        self.call_service('media_player/sonos_restore', entity_id=kwargs['output_device'])
        localvars.Speech_InUse = 0

    def terminate(self):
        localvars.Speech_InUse = 0