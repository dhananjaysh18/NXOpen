
Code fix for test_simple.py and config.json

I want High quylity Studio images, I am using Truestudio if other class available better image output quality, please use that.

The main script takes camera parameters from the json file, like dimensions of output image, views/positions, background color, maybe lights, brightness level(enumerator), scale/fit(scale is better like 0.9), I do not whatelse available in NX maybe scenes, I just want diverese images 


Views I need: Front, top, bottom, back, right, left, front right side 45°, front left side 45°, front top side 45°, front bottom side 45° and isometric(camera position should be from front bottom cornor to up)


Later, I can also add more or change image output options, like differet background, or lights or brightness in json file. My goal is that i have to train the images from NX and validate on real camera photos, So I can change the image positions in json and get as similar real camera images from NX.

test_simple.py is giving images but not so high quality and with origin marker in the centre which i do not need.



