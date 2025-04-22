import json
import os
import time
import hashlib
import base64
import copy

from get_image_url_keyword import get_pinterest_images
import datetime
import uuid
from tqdm import tqdm


def generate_hash(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()

def generate_image(prompt):
    # NOTE 直接返回一个 list 的 url,线上的，后续再下载
    global output_dir
    cache_path = os.path.join(output_dir, f'cache/{generate_hash(prompt)}.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    urls = get_pinterest_images(prompt)
    with open(cache_path, 'w') as f:
        json.dump(urls, f, indent=4)
    return urls


def get_images(round_item,type):
    if type == 'prompt':
        if len(round_item['prompt_image_captions']) == 0:
            return []
        assert len(round_item['prompt_image_captions']) == len(round_item['prompt_image_captions_judgement'])
        prompt_images = [''] * len(round_item['prompt_image_captions'])
        for idx in range(len(round_item['prompt_image_captions_judgement'])):
            if 'real' in (round_item['prompt_image_captions_judgement'][idx]).lower():
                prompt_images[idx] = generate_image(round_item['prompt_image_captions'][idx])
        return prompt_images
    
    elif type == 'response':
        if len(round_item['response_image_captions']) == 0:
            return []
        assert len(round_item['response_image_captions']) == len(round_item['response_image_captions_judgement'])
        response_images = [''] * len(round_item['response_image_captions'])
        for idx in range(len(round_item['response_image_captions_judgement'])):
            if 'real' in (round_item['response_image_captions_judgement'][idx]).lower():
                response_images[idx] = generate_image(round_item['response_image_captions'][idx])
        return response_images


def annotate_crawling(data):
    
    new_data = []
    
    for item in tqdm(data):
        new_item = copy.deepcopy(item)
        for idx in range(len(new_item['conversations'])):
            new_item['conversations'][idx]['prompt_images'] = get_images(new_item['conversations'][idx],'prompt')
            new_item['conversations'][idx]['response_images'] = get_images(new_item['conversations'][idx],'response')
        new_data.append(new_item)
        
    return new_data
    

if __name__ == "__main__":
    input_file = './debug_align_anything_ti2t_instruction_100k_previous_100/crawling/round_2_responses_before_get_images__classication_close.json'
    output_file = './debug_align_anything_ti2t_instruction_100k_previous_100/crawling/round_2_responses_get_images__crawling.json'
    global output_dir
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, 'r') as f:
        data = json.load(f)
        

    print(f'Generating images')
    new_data = annotate_crawling(data)
    print(f'Images generated')
    with open(output_file, 'w') as f:
        json.dump(new_data, f, indent=4)
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('./log.txt', 'a+') as f:
        f.write(f'时间: {current_time}\n Get images: Crawling\n 输入路径: {input_file}\n 输出路径: {output_file}\n')
    

    