from clarifai.rest import ClarifaiApp
import json

app = ClarifaiApp(api_key='d198e7a734e34213add3f1711f0d349b')

# get the general model
model = app.models.get("general-v1.3")

# add image from image url
app.inputs.create_image_from_url

# predict with the model
output = model.predict_by_url(url='https://home.tai.net.au/api/camera_proxy/camera.pseye_image?token=890f3d89faaa30c484eb5204a251b43f6ea0431ccfbdef38760d5f157cd1eefb&time=1505612641457')

for i in output['outputs'][0]['data']['concepts']:
    if (i['name']) == 'people':
        print('Person Detected')
        print (i['value'])
