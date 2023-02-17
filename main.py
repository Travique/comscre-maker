import asyncio
import re
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import vk_api
import time 
import random
import os

API_ID = "2685278"
API_SECRET = "hHbJug59sKJie78wjrH8"
TIME_SLEEP = 5.1

async def take_screenshot(post_info_list):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    await asyncio.sleep(TIME_SLEEP)
    
    browser = webdriver.Chrome(options=options)
    
    try:
        for index, element in enumerate(post_info_list):
            if index == len(post_info_list) + 1:
                continue
            
            browser.get(post_info_list[index])
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            screenshot_path = f'post_comment_{random.randrange(0,100000)}_{index}_{random.randint(0,1000000)}.png'
            browser.save_screenshot(f'{os.getcwd()}\Screens\{screenshot_path}')
            print(f'Screenshot saved to {screenshot_path}!')

        browser.quit()
       
            
    except Exception as e:
        print(f'Error taking screenshot: {str(e)}')
        browser.quit()


async def post_comment(comment, post_id, owner_id):
    
    try:
        print(f'https://vk.com/wall-{owner_id}_{post_id} is waiting for comment.')
        vk.wall.createComment(owner_id=-owner_id, post_id=post_id, message=comment)
        time.sleep(TIME_SLEEP)
        print(f'Comment {comment} posted successfully for https://vk.com/wall-{owner_id}_{post_id}.')
        
    except Exception as e:
        print(f'Error posting comment "{comment}": {str(e)}')


async def main():
    start = time.time()

    try:
        with open('login.txt', 'r') as f:
            login, password = f.read().strip().split(':')
            
    except Exception as e:
        print(f'Error reading login information: {str(e)}')
        return
    
    try:
        with open('post_info.txt', 'r') as f:
            post_info = f.read().strip()
            
    except Exception as e:
        print(f'Error reading post information: {str(e)}')
        return

    try:
        with open('comments.txt', 'r') as f:
            comments = f.read().strip()
            
    except Exception as e:
        print(f'Error reading post information: {str(e)}')
        return

    comments_list = comments.split('\n')
    comment = comments_list[random.randrange(0, len(comments_list))]
    match_info_list = []
    post_info_list = post_info.split('\n')
    
    for index, element in enumerate(post_info_list):
        if index == len(post_info_list) + 1:
            continue
        
        match = re.search(r'vk\.com/wall-(\d+)_(\d+)', post_info_list[index])
        
        if match:
            owner_id = int(match.group(1))
            post_id = int(match.group(2))
            match_info_list = match_info_list + [(owner_id, post_id)]
            
        else:
            print('Invalid post info!')
            
    try:
        global vk_session
        vk_session = vk_api.VkApi(login, password, app_id=API_ID, client_secret=API_SECRET)
        vk_session.auth()
        global vk
        vk = vk_session.get_api()
        
    except Exception as e:
        print(f'Error setting up VK API (maybe u should use VPN): {str(e)}')
        return

    tasks = []
    tasks.append(asyncio.create_task(take_screenshot(post_info_list)))
    while len(match_info_list) != 0:
        tasks.append(asyncio.create_task(post_comment(comment, match_info_list[0][1], match_info_list[0][0])))
        match_info_list.pop(0)
            
    try:
        await asyncio.gather(*tasks)
        
    except Exception as e:
        print(f'Error running tasks: {str(e)}')


    end = time.time() - start 
    print(f'Time of working: {end}')

if __name__ == '__main__':
    asyncio.run(main())

    
