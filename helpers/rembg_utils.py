import requests, ctypes, sys, math

from copy import copy
from io import BytesIO
from PIL import Image, ImageSequence

from variables import variables_bot as varbot

try:
    import nextcord as discord
    import av, sniffpy
    from rembg import remove
    from wand.image import Image as ImageWand
    from wand.api import library as LibraryWand
except ImportError as error:
    print(error); input(); sys.exit()
    

image_mime_types = ['png', 'jpeg', 'gif', 'webp']
video_mime_types = ['mp4']

async def mime_type_sniff(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
    try:
        response = requests.get(url, stream=True, headers=headers)      
    except requests.exceptions.ConnectionError:
        type_validity = False
        mime_type = None
        errorEmbed = constructEmbedNotice('Invalid Link.')
        return type_validity, mime_type, errorEmbed

    mime_type = sniffpy.sniff(response.content).subtype
    
    if mime_type in image_mime_types + video_mime_types: 
        type_check = True 
        errorEmbed = None
        return type_check, mime_type, errorEmbed
    
    else: 
        type_check = False
        errorEmbed = constructEmbedNotice(f"Detected file mime type as: '{mime_type}', which is not supported.")
        return type_check, mime_type, errorEmbed


def constructEmbedNotice(noticeMessage):
    if isinstance(noticeMessage, str):
        EmbedNotice=discord.Embed(description=noticeMessage,  
                            type="rich", color=0xc82323)
        return EmbedNotice
    else: 
        noticeMessage = "Unexpected error occurred while creating embed message."
        EmbedNotice=discord.Embed(description=noticeMessage,  
                    type="rich", color=0xc82323)
        return EmbedNotice


async def send_embed(ctx, Image_IO, format='PNG'):
    image_filename = f'removed_background.{format}'
    file = discord.File(fp=Image_IO, filename=image_filename)
    
    descriptionText = 'Background exterminated!'
    
    embed=discord.Embed(title=f"", description=descriptionText)
    embed.set_image(url=f"attachment://{image_filename}")
    await ctx.reply(file=file, embed=embed, mention_author=False)   
   
    
def embed_iterator(idx, total_idx, initialization=False):
    if not initialization:
        embed=discord.Embed(title=f'', description=f'Processing {idx+1} out of {total_idx} frames.')
    else:
        embed=discord.Embed(title=f'', description=f'Initializing..')
    return embed


async def handle_image(ctx, image_url):
    Image_IO, num_frames, errorEmbed = await download_image(image_url)  
    
    if Image_IO is None: 
        await ctx.reply(embed=errorEmbed, mention_author=False); return
    
    elif num_frames == 1:
        rembg_image = await remove_background(Image_IO)
        await send_embed(ctx, rembg_image)
        
    elif num_frames > 1:  
        await process_animated(ctx, Image_IO)

                
async def process_animated(ctx, Image_IO):                
    animated_ImageFrames = await getAnimatedFrames(Image_IO)
    num_frames = len(animated_ImageFrames) 
    iterator_messsage = await ctx.channel.send(embed=embed_iterator(0, 0, initialization=True))
    
    for idx, data in animated_ImageFrames.items():
        print(f'Processing {idx+1} out of {num_frames}')
        await iterator_messsage.edit(embed=embed_iterator(idx, num_frames))
        data['image'] = await remove_background(Image.open(data['image']))
    await iterator_messsage.delete()
    
    rembg_gif = await reconstruct_gif(animated_ImageFrames)
    await send_embed(ctx, rembg_gif, format='gif')
        
        
async def reconstruct_gif(image_frames):     
    BackgroundDispose = ctypes.c_int(2)
    Image_IO = BytesIO()

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
        wand.save(file=Image_IO)
        
    Image_IO.seek(0)
    return Image_IO
    
    
def PIL_To_BytesIO(Image_PIL, format):
    Image_IO = BytesIO()
    Image_PIL.save(Image_IO, format=format)
    Image_IO.seek(0)
    return Image_IO 
    
    
async def getAnimatedFrames(Image_IO):
    image_frames = {idx:{'image':PIL_To_BytesIO(frame, 'PNG'), 'duration':frame.info['duration']} for idx, frame in enumerate(ImageSequence.Iterator(Image_IO))}
    return image_frames
        

async def remove_background(img_PIL):
    rembg_PIL = remove(img_PIL)
    rembg_IO = PIL_To_BytesIO(rembg_PIL, 'PNG')
    return rembg_IO


async def download_image(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
    response = requests.get(url, stream=True, headers=headers)      

    image_data = BytesIO(response.raw.read())
    PIL_formats = ['PNG', 'JPEG', 'WEBP', 'GIF']
    
    try:
        PIL_Image = Image.open(image_data)
        width, height = PIL_Image.size
        format = PIL_Image.format
        
        max_num_frames = varbot.max_frames_animated
        minimum_px = 32
        
        try:  num_frames = PIL_Image.n_frames
        except: num_frames = 1
            
        if num_frames == 1: max_px = varbot.max_px_image
        elif num_frames > 1: max_px = varbot.max_px_animated
            
            
        if format not in PIL_formats: 
            PIL_Image = None
            errorEmbed = constructEmbedNotice(f"Detected file type as: '{format}', which is not supported.")
            return PIL_Image, num_frames, errorEmbed
        
        if num_frames > max_num_frames: 
            PIL_Image = None
            errorEmbed = constructEmbedNotice(f"{format} exceeds maximum of {max_num_frames} frames, due to processing times required.\n\
                                              **Frame Count:** {num_frames}")
            
            return PIL_Image, num_frames, errorEmbed
        
        if width > max_px or height > max_px: 
            PIL_Image = None
            errorEmbed = constructEmbedNotice(f"{format} needs to be <{max_px}px in width or height.\n\
                                              **Resolution:** {width}x{height}")
            
            return PIL_Image, num_frames, errorEmbed
            
        if width < minimum_px or height < minimum_px:
            PIL_Image = None
            errorEmbed = constructEmbedNotice(f"{format} needs to be >{minimum_px}px in width or height.\n\
                                              **Resolution:** {width}x{height}")    
            
            return PIL_Image, num_frames, errorEmbed     
         
    except Exception as error:
        print(error)
        PIL_Image = None
        errorEmbed = constructEmbedNotice("Error occured while loading image!")
        return PIL_Image, num_frames, errorEmbed
    
    errorEmbed = None
    return PIL_Image, num_frames, errorEmbed


async def handle_video(ctx, image_url):
    Video_IO, errorEmbed = await download_video(image_url)  
    
    if Video_IO is None: 
        await ctx.reply(embed=errorEmbed, mention_author=False); return
    
    else: 
        await process_video(ctx, Video_IO)


async def process_video(ctx, Video_IO):                
    video_ImageFrames = await getVideoFrames(Video_IO)
    num_frames = len(video_ImageFrames) 
    iterator_messsage = await ctx.channel.send(embed=embed_iterator(0, 0, initialization=True))
    
    for idx, data in video_ImageFrames.items():
        print(f'Processing {idx+1} out of {num_frames}')
        await iterator_messsage.edit(embed=embed_iterator(idx, num_frames))
        data['image'] = await remove_background(Image.open(data['image']))
    await iterator_messsage.delete()
    
    rembg_gif = await reconstruct_gif(video_ImageFrames)
    await send_embed(ctx, rembg_gif, format='gif')


def getVideoDetails(bytes_file):
    try:
        av_container = av.open(copy(bytes_file), mode='r')
        frame_count = len([packet for packet in av_container.demux(video=0) if packet.size > 0])
        duration = av_container.duration / 1000000
        fps = math.ceil(frame_count / duration)

        av_container = av.open(copy(bytes_file), mode='r')
        width, height = next((frame.width, frame.height) for frame in av_container.decode(video=0) if frame.width and frame.height)
    except Exception as e:
        print(e); return None

    videoDetails = {'frame_count':frame_count, 'fps':fps, 'width': width, 'height': height, 'duration': duration}
    return videoDetails


async def getVideoFrames(bytes_file):
    videoDetails = getVideoDetails(bytes_file)
    av_container = av.open(copy(bytes_file), mode='r')

    max_fps = varbot.max_video_fps
    fps_ratio = math.ceil(videoDetails['fps']/max_fps)

    adjusted_frame_count = math.ceil(videoDetails['frame_count'] / fps_ratio)
    adjusted_fps = round(adjusted_frame_count / videoDetails['duration'], 2)
    adjusted_frame_duration = (1 / adjusted_fps) * 1000

    ratio_stepper = 0
    idx_stepper = 0
    video_ImageFrames = {} 
    

    for frame in av_container.decode(video=0):
        if ratio_stepper == 0:
            video_ImageFrames[idx_stepper] = {'image': PIL_To_BytesIO(frame.to_image(), 'PNG'), 
                                         'duration': adjusted_frame_duration} 
            idx_stepper += 1
        ratio_stepper += 1
        if ratio_stepper == fps_ratio: ratio_stepper = 0
    return video_ImageFrames


async def recalculate_fps(max_fps, video_fps, video_framecount, video_duration):
    fps_ratio = math.ceil(video_fps / max_fps)

    adjusted_frame_count = math.ceil(video_framecount / fps_ratio)
    adjusted_fps = round(adjusted_frame_count / video_duration, 2)
    adjusted_frame_duration = (1 / adjusted_fps) * 1000
    
    return fps_ratio, adjusted_fps, adjusted_frame_count, adjusted_frame_duration


async def download_video(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
    response = requests.get(url, stream=True, headers=headers)      

    Video_IO = BytesIO(response.raw.read())
    
    try:
        videoDetails = getVideoDetails(Video_IO)
        
        width, height = videoDetails['width'], videoDetails['height']
        fps = videoDetails['fps']
        frame_count = videoDetails['frame_count']
        duration = videoDetails['duration']
        max_fps = varbot.max_video_fps
        max_num_frames = varbot.max_frames_animated
        max_px = varbot.max_px_animated
        minimum_px = 32
        
        if fps > max_fps:
            _ , _, adjusted_framecount, _ = await recalculate_fps(max_fps, fps, frame_count, duration)
        else: 
            adjusted_framecount = frame_count
        

        if adjusted_framecount > max_num_frames: 
            Video_IO = None
            errorEmbed = constructEmbedNotice(f'Video exceeds maximum of {max_num_frames} frames.\n\
                                              **Frame Count:** {frame_count}')
            return Video_IO, errorEmbed
        
        if width > max_px or height > max_px: 
            Video_IO = None
            errorEmbed = constructEmbedNotice(f"Video needs to be <{max_px}px in width or height.\n\
                                              **Resolution:** {width}x{height}")
            return Video_IO, errorEmbed
        
        if width < minimum_px or height < minimum_px:
            Video_IO = None
            errorEmbed = constructEmbedNotice(f"Video needs to be >{minimum_px}px in width or height.\n\
                                              **Resolution:** {width}x{height}")  
            return Video_IO, errorEmbed      
         
    except Exception as error:
        print(error)
        Video_IO = None
        errorEmbed = constructEmbedNotice("Error occured while loading video!")
        return Video_IO, errorEmbed

    errorEmbed = None
    return Video_IO, errorEmbed
