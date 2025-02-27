import random
import math
import itertools

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from PIL import ImageOps

def button(race):
    
    highlight = Image.open('./graphics/round.png')
    enhancer = ImageEnhance.Brightness(highlight)
    highlight = enhancer.enhance(0.5)
    highlight = highlight.filter(ImageFilter.GaussianBlur(radius=5))
    mask = Image.open('./graphics/round-mask.png')

    icon = Image.open(f'./graphics/{race}_transparent_by_n80sire.png').convert('RGBA')
    enhancer = ImageEnhance.Brightness(icon)
    icon = enhancer.enhance(1.5) 
    button = Image.new('RGBA', mask.size)

    # Resize Icon
    icon = ImageOps.fit(icon, highlight.size, 
                        method=Image.LANCZOS, centering=(0.5, 0.5))

    # Create a helper image that will hold the icon after the reshape
    helper = button.copy()
    # Cut the icon by the shape of the mask
    helper.paste(icon, mask=mask)

    # Fill with a solid color by the mask's shape
    button.paste((0, 0, 0), mask=mask)
    # Get rid of the icon's alpha band
    icon = icon.convert('RGB')
    # Paste the icon on the solid background
    # Note we are using the reshaped icon as a mask
    button.paste(icon, mask=helper)
    
    # Get a copy of the highlight image without the alpha band
    overlay = highlight.copy().convert('RGB')
    button.paste(overlay, mask=highlight)

    return button 
     

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def add_corners_brd(im, rad=50, bg=True, bgCol='white', bgPix=2):
    bg_im = Image.new('RGB', tuple(x+(bgPix*2) for x in im.size), bgCol)
    ims = [im if not bg else im, bg_im]
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    for i in ims:
        alpha = Image.new('L', i.size, 'white')
        w, h = i.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        i.putalpha(alpha)
    bg_im.paste(im, (bgPix, bgPix), im)
    return im if not bg else bg_im

def draw_hexagon(ax, center, radius, color='w'):
        ax.add_patch(
            mpatches.RegularPolygon(
                xy=center,
                numVertices=6,
                radius=radius + 0.2,
                facecolor=color,
                edgecolor="none",
                orientation=0,
                fill=True))

def player_banner(b_text,race,corner_boarder=False):
    
    np.random.seed(2019)

    RADIUS = 2

    # Dimensions of the bounding box of the hexagons
    WIDTH = math.sqrt(3) * RADIUS
    HEIGHT = 2 * RADIUS

    mm_to_in = 0.03937008

    # positions for hexagon
    centers=list()
    for offset_x, offset_y in [(0, 0), (WIDTH / 2, (3 / 2) * RADIUS)]:
        rows = np.arange(start=offset_x, stop=105, step=WIDTH)
        columns = np.arange(start=offset_y, stop=105, step=3 * RADIUS)
        for x, y in itertools.product(rows, columns):
            centers.append((x,y))

    colormap = plt.get_cmap('plasma')

    figure, ax = plt.subplots(1, 1, 
                            figsize=(100 * mm_to_in, 100 * mm_to_in), 
                            frameon=False)
    for (x,y) in centers:
        # radius away from bottom left corner
        # proportional to the distance of the top right corner
        # i.e. 0 < r < 1
        r = math.hypot(x, y) / math.hypot(100, 100)
        draw_hexagon(ax, center=(x, y), radius=RADIUS, color=colormap(r + random.gauss(0, 0.01)))


    # Dimensions of the page in mm
    ax.set_xlim([0, 100])
    ax.set_ylim([0, 100])
    ax.axis("off")



    image_xaxis = 0.04
    image_yaxis = 0.08
    image_width = 0.25
    image_height = 0.25  # Same as width since our logo is a square

    ax_image = figure.add_axes([image_xaxis,
                            image_yaxis,
                            image_width,
                            image_height]
                        )

    # Display the image
    badge = button(race)
    ax_image.imshow(badge)
    ax_image.axis('off')  # Remove axis of the image

    ax_t = figure.add_axes([0,0,1,1])
    ax_t.text(0.22, 0.15, b_text, 
              color='white',
              fontname='fantasy', fontweight='extra bold', 
              fontsize=26, va='center')
    ax_t.axis('off')

    # 'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace'
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
    plt.show()
    figure.savefig(f'./graphics/{b_text}.png')

    banner = Image.open(f'./graphics/{b_text}.png')
    banner = banner.crop((0,250,393,375))
    if corner_boarder:
        banner = add_corners_brd(banner,20)
    else:
        banner = add_corners(banner, 20)
    banner.save(f'./graphics/{b_text}.png')

    return banner