import requests, ctypes, sys
import nextcord as discord

from io import BytesIO
from PIL import Image, ImageSequence
from wand.image import Image as ImageWand
from wand.api import library as LibraryWand

from variables import variables_bot as varbot

try:
    from rembg import remove
except ImportError as error:
    print(error); input(); sys.exit()


async def send_embed(ctx, imageio, format='PNG'):
    image_filename = f'removed_background.{format}'
    file = discord.File(fp=imageio, filename=image_filename)
    
    descriptionText = 'Background exterminated!'
    
    embed=discord.Embed(title=f"", description=descriptionText)
    embed.set_image(url=f"attachment://{image_filename}")
    await ctx.reply(file=file, embed=embed, mention_author=False)    
   
    
def embed_iterator(idx, total_idx, initialization=False):
    if not initialization:
        embed=discord.Embed(title=f'', description=f'Processing {idx+1} out of {total_idx}')
    else:
        embed=discord.Embed(title=f'', description=f'Initializing..')
    return embed


async def handle_image(ctx, image_url):
    imageio, num_frames, errorMessage = await download_image(image_url)  
    
    if imageio is None: 
        await ctx.reply(errorMessage, mention_author=False); return
    
    elif num_frames == 1:
        rembg_image = await remove_background(imageio)
        await send_embed(ctx, rembg_image)
        
    elif num_frames > 1:  
        await handle_animated(ctx, imageio)

                
async def handle_animated(ctx, imageio):                
    image_frames = await return_animated_frames(imageio)
    num_frames = len(image_frames) 
    iterator_messsage = await ctx.channel.send(embed=embed_iterator(0, 0, initialization=True))
    
    for idx, data in image_frames.items():
        print(f'Processing {idx+1} out of {num_frames}')
        await iterator_messsage.edit(embed=embed_iterator(idx, num_frames))
        data['image'] = await remove_background(Image.open(data['image']))
    await iterator_messsage.delete()
    
    rembg_gif = await reconstruct_gif(image_frames)
    await send_embed(ctx, rembg_gif, format='gif')
        
        
async def reconstruct_gif(image_frames):     
    BackgroundDispose = ctypes.c_int(2)
    image_IO = BytesIO()

    with ImageWand() as wand:
        for idx, data in image_frames.items():
            with ImageWand(blob=data['image']) as wand_image:
                
                with ImageWand(width = wand_image.width,
                            height=wand_image.height, 
                            background=None) as wand_bg_composite:
                    
                    wand_bg_composite.composite(wand_image, 0, 0)
                    LibraryWand.MagickSetImageDispose(wand_bg_composite.wand, BackgroundDispose)
                    wand.sequence.append(wand_bg_composite)
        
        for idx, data in image_frames.items():
            with wand.sequence[idx] as frame:
                frame.delay = int(data['duration']/10)
                
        wand.type = 'optimize'
        wand.format = 'GIF'
        wand.save(file=image_IO)
        
    image_IO.seek(0)
    return image_IO
    
    
def PIL_To_BytesIO(PIL_Image, format):
    io_image = BytesIO()
    PIL_Image.save(io_image, format=format)
    io_image.seek(0)
    return io_image 
    
    
async def return_animated_frames(imageio):
    image_frames = {idx:{'image':PIL_To_BytesIO(frame, 'PNG'), 'duration':frame.info['duration']} for idx, frame in enumerate(ImageSequence.Iterator(imageio))}
    return image_frames
        

async def remove_background(img_PIL):
    rembg_PIL = remove(img_PIL)
    rembg_IO = PIL_To_BytesIO(rembg_PIL, 'PNG')
    return rembg_IO


async def download_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
    response = requests.get(url, stream=True, headers=headers)      

    image_data = BytesIO(response.raw.read())

    try:
        PIL_Image = Image.open(image_data)
        width, height = PIL_Image.size
        format = PIL_Image.format
       
        max_num_frames = varbot.max_frames_animated
        image_formats = ['PNG', 'JPEG', 'WEBP', 'GIF']
        
        try: 
            num_frames = PIL_Image.n_frames
        except:
            num_frames = 1
            
        if num_frames == 1:
            max_px = varbot.max_px_image
   
        elif num_frames > 1:
            max_px = varbot.max_frames_animated
            
        if num_frames > max_num_frames: return None, num_frames, f'`{format} exceeds maximum of {max_num_frames} frames, due to processing times required.\nNumber of Frames: {num_frames}`'
        if format not in image_formats: return None, num_frames, f"'{format} formats are currently not supported.'"
        if width > max_px or height > max_px: return None, num_frames, f"`{format} needs to be <{max_px}px in width or height.`"              
         
    except Exception as e:
        return None, num_frames, "`Error occured while loading image!`"  

    return PIL_Image, num_frames, None
