from PIL import Image, ImageDraw, ImageFont
import os
import time
import sys
import glob

folder_path  = "./sample_gif/"
saved_path = f"{folder_path}/converted/"

def convert_image_to_ascii(image):
    font = ImageFont.load_default() # load default bitmap monospaced font
    (chrx, chry) = font.getsize(chr(32))
    # calculate weights of ASCII chars
    weights = []
    for i in range(32,127):
        chrImage = font.getmask(chr(i))
        ctr = 0
        for y in range(chry):
            for x in range(chrx):
                if chrImage.getpixel((x, y)) > 0:
                    ctr += 1
        weights.append(float(ctr) / (chrx * chry))
    
    output = ""
    (imgx, imgy) = image.size
    imgx = int(imgx / chrx)
    imgy = int(imgy / chry)
    # NEAREST/BILINEAR/BICUBIC/ANTIALIAS
    image = image.resize((imgx, imgy), Image.BICUBIC)
    image = image.convert("L") # convert to grayscale
    pixels = image.load()
    for y in range(imgy):
        for x in range(imgx):
            w = float(pixels[x, y]) / 255
            # find closest weight match
            wf = -1.0
            k = -1
            for i in range(len(weights)):
                if abs(weights[i] - w) <= abs(wf - w):
                    wf = weights[i]
                    k = i
            output+=chr(k+ 32)
        output+="\n"
    return output

def extract_gif_frames(gif, fillEmpty=False):
    frames = []
    try:
        while True:
            gif.seek(gif.tell()+1)
            new_frame = Image.new('RGBA',gif.size)
            new_frame.paste(im,(0,0),im.convert('RGBA'))

            if fillEmpty:
                canvas = Image.new('RGBA',new_frame.size,(255,255,255,255))
                canvas.paste(new_frame,mask=new_frame)
                new_frame = canvas
            frames.append(new_frame)
    except EOFError:
        pass
    return frames

def convert_frames_to_ascii(frames):
    ascii_frames = []
    for frame in frames:
        new_frame = convert_image_to_ascii(frame)
        ascii_frames.append(new_frame)
    return ascii_frames
def save_ascii(ascii_frames):
    frames = []
    try:
        for i in ascii_frames:
            canvas = Image.new("RGB",im.size,(0,0,0))
            draw = ImageDraw.Draw(canvas)
            draw.text((0,0),i)
            frames.append(canvas)
    except EOFError:
        pass
    return frames

# reading the image
for filename in glob.iglob(f"{folder_path}*.gif",recursive=True):
    im = Image.open(f"{filename}")
    # extracting the frames from gif
    frames = extract_gif_frames(im,fillEmpty=True)
    ascii_frames = convert_frames_to_ascii(frames)

    saved_frames = save_ascii(ascii_frames)
    saved_frames[0].save(f'{saved_path}{filename.split("/")[-1]}',save_all=True,append_images=saved_frames[1:])
    print(f"{filename} saved successfully")

