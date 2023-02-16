import asyncio
import re
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import vk_api
import time 

API_ID = "2685278"
API_SECRET = "hHbJug59sKJie78wjrH8"

async def take_screenshot(post_id, owner_id):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    await asyncio.sleep(3)
    
    browser = webdriver.Chrome(options=options)
    
    try:

        #Cycles also here for loggining and making screenshots for a all links in post and owner.
        
        browser.get(f'https://vk.com/wall-{owner_id}_{post_id}')
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        screenshot_path = f'post_comments_{post_id}.png'
        browser.save_screenshot(screenshot_path)
        
        browser.quit()
        print(f'Screenshot saved to {screenshot_path}!')
        
    except Exception as e:
        print(f'Error taking screenshot: {str(e)}')
        browser.quit()


async def post_comment(comment, post_id, owner_id):
    try:

        #I think, that we will add here cycles.
        
        print(f'https://vk.com/wall-{owner_id}_{post_id} is waiting for comment.')
        vk.wall.createComment(owner_id=-owner_id, post_id=post_id, message=comment) 
        print(f'Comment "{comment}" posted successfully for https://vk.com/wall-{owner_id}_{post_id}.')
        
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
        

    match = re.search(r'vk\.com/wall-(\d+)_(\d+)', post_info) 
    if match:
        owner_id = int(match.group(1))
        post_id = int(match.group(2))
    else:
        print('Invalid post info!')
        return

    try:
        global vk_session
        vk_session = vk_api.VkApi(login, password, app_id=API_ID, client_secret=API_SECRET)
        vk_session.auth()
        global vk
        vk = vk_session.get_api()
        
    except Exception as e:
        print(f'Error setting up VK API (maybe u should use VPN): {str(e)}')
        return

    comments = ['It is my test comment!']

    tasks = []
    tasks.append(asyncio.create_task(take_screenshot(post_id, owner_id)))
    for comment in comments:
        tasks.append(asyncio.create_task(post_comment(comment, post_id, owner_id)))
        
    try:
        await asyncio.gather(*tasks)
        
    except Exception as e:
        print(f'Error running tasks: {str(e)}')


    end = time.time() - start 
    print(f'Time of working: {end}')

if __name__ == '__main__':
    asyncio.run(main())

    
