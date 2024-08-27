#!Python3
# resizeAndAddLogo.py -- resizes all image incurrent working dir to fit
# in a 300*300 square, and adds catlog.png to the lower-right corner.
import os
from PIL import Image
os.chdir(r'D:\Python学习\automate_online-materials')
SQUARE_FIT_SIZE = 300
LOGO_FILENAME = 'catlogo.png'

logoIm = Image.open(LOGO_FILENAME)
logWidth,logHeight = logoIm.size
logoIm.save(os.path.join('withlog','yyy1.jpg'))

os.makedirs('withlog',exist_ok=True)
logoIm.save(os.path.join('withlog','yyy2.jpg'))

# Loop over all files in working directory
for filename in os.listdir('.'):
    if not (filename.endswith('.png') or filename.endswith('.jpg')) \
       or filename == LOGO_FILENAME:
        continue # skip non-image files and the logo file itself
    im = Image.open(filename)
    width,height = im.size
    if width > SQUARE_FIT_SIZE and height > SQUARE_FIT_SIZE:
        #Calculate the new width and height to resize to.
        if width > height:
            logHeight = int((SQUARE_FIT_SIZE / logWidth) * logHeight)
            logWidth = SQUARE_FIT_SIZE
        else:
            logWidth = int((SQUARE_FIT_SIZE/logHeight) * logWidth)
            logHeight = SQUARE_FIT_SIZE

        #Resize the image.
        print('Resizing %s ...' % (filename))
        logoIm.save(os.path.join('withlog','yyy.jpg'))
        logoIm = logoIm.resize((logWidth,logHeight))
    print('Adding logo to %s ...' % (filename))
    logoIm.save(os.path.join('withlog','xxx.jpg'))
    im.paste(logoIm,(width - logWidth,height - logHeight),logoIm)

    im.save(os.path.join('withlog',filename))
    
