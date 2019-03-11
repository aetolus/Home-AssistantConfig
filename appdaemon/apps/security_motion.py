import appdaemon.plugins.hass.hassapi as hass
from queue import Queue
import threading
import random
import time
from clarifai.rest import ClarifaiApp
import shutil


class Motion(hass.Hass):
    def initialize(self):
        # Create Queue & Create worker thread#
        self.queue = Queue(maxsize=0)
        t = threading.Thread(target=self.worker)
        t.daemon = True
        t.start()
        # Listen for Notification Repo
        self.listen_state(self.announce, entity='sensor.mqtt_motion')

    def announce(self, entity, attribute, old, new, text):
        self.log("Motion detected")
        self.queue.put(new)

    def worker(self):
        while True:
            try:
                # Get image to send
                self.log("Waiting for motion")
                text = self.queue.get()
                # Ensure valid file
                if text != 'unknown':
                    shutil.copy2(text, '/home/homeassistant/.homeassistant/www/images')
                    img = str(text).replace('/var/lib/motion/', "")
                    img = 'https://home.tai.net.au/local/images/' + img
                    self.log(img)
                    # start clarifai
                    app = ClarifaiApp(api_key='d198e7a734e34213add3f1711f0d349b')
                    # get the general model
                    model = app.models.get("general-v1.3")
                    # add image from image url
                    app.inputs.create_image_from_url
                    # predict with the model
                    output = model.predict_by_url(url=img)
                    for i in output['outputs'][0]['data']['concepts']:
                        if (i['name']) == 'people' and (i['value']) > 0.8:
                            self.log("Calling telegram_bot service")
                            self.call_service('telegram_bot/send_photo', file=text)
                            self.log("Called telegram_bot service")
                            # Sleep to avoid overloading telegram notifications
                            time.sleep(5)
                # Rinse and repeat
                self.log("Rinse & Repeat")
                self.queue.task_done()
            except:
                self.log("Error")
