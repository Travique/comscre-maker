import asyncio
import re
import aiofiles
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import vk_api
from vk_api.exceptions import ApiError
import requests
import json
import time 
import random
import os
import sys

#SETTINGS.

API_ID = "2685278"
API_SECRET = "hHbJug59sKJie78wjrH8"
TIME_SLEEP = 5.1
#OPENING ALL FILES.

async def open_file(filename):
    async with aiofiles.open(filename, mode='r') as f:
        return [line.strip() for line in await f.readlines()]


async def open_files():
    post_info_list, log_pass = await asyncio.gather(
        open_file('post_info.txt'),
        open_file('login.txt')
    )

    comment_dict = {}
    with open('comments.txt', 'r') as f:
        for line in f:
            if line.strip():
                comment, path_photo = line.strip().split(':')
                comment_dict[comment] = path_photo.strip()

    match_info_list = []
    
    for index, element in enumerate(post_info_list):
        if index == len(post_info_list) + 1:
            continue
        
        match = re.search(r'vk\.com/wall-(\d+)_(\d+)', post_info_list[index])
        
        if match:
            owner_id = int(match.group(1))
            post_id = int(match.group(2))
            match_info_list = match_info_list + [(owner_id, post_id)]

    for i, lst in enumerate([post_info_list, log_pass, comment_dict]):
        if not lst or '' in lst:
            print(f"{['Posts', 'Credentials', 'Comments'][i]} is empty or contains an empty string")
            input("Press Enter to exit")
            quit()
            
    return comment_dict, match_info_list, post_info_list, [tuple(line.strip().split(':')) for line in log_pass]


'''This def create a scrinshots of comments which
attempd by function create_comment'''        
async def take_screenshot(log_pass, post_info_list, match_info_list, author_id):
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    await asyncio.sleep(TIME_SLEEP)
    
    browser = webdriver.Chrome(options=options)
    
    try:
        username = log_pass[0]
        password = log_pass[1]
        
        browser.get('https://vk.com/login')

        username_field = browser.find_element(By.XPATH, "//input[@name='login']")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
 
        password_field = WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='password']")))
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(TIME_SLEEP)
        
        for index, element in enumerate(match_info_list):
            if index == len(match_info_list) + 1:
                continue

            try: 
                browser.get(match_info_list[index])

                button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.post_replies_reorder_wrap")))
                button.click()

                button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-order="desc"]')))
                button.click()
                time.sleep(5)
                
                screenshot_path = f'post_comment_{random.randrange(0,100000)}_{index}_{random.randint(0,1000000)}.png'
                browser.save_screenshot(f'{os.getcwd()}\Screens\{screenshot_path}')
                print(f'Screenshot saved to {screenshot_path}!')
            except:
                continue

        browser.quit()
        
    except Exception as e:
        print(f'Selenium Response: {str(e)}')
        browser.quit()



#POST COMMENT&PHOTO DEF
async def post_comment(comment, photo_path, post_id, owner_id, log_pass):     
    try:
        if photo_path is None:
            vk.wall.createComment(owner_id=owner_id, post_id=post_id, message=comment)
            print(f'Comment "{comment}" posted successfully for https://vk.com/wall-{owner_id}_{post_id}.')
        else:
            upload_url = vk.photos.getWallUploadServer()['upload_url']
            with open(photo_path, 'rb') as f:
                response = requests.post(upload_url, files={'photo': f})
            response_json = json.loads(response.text)
            photo = vk.photos.saveWallPhoto(photo=response_json['photo'], server=response_json['server'], hash=response_json['hash'])[0]

            attachment = f"photo{photo['owner_id']}_{photo['id']}"
            vk.wall.createComment(owner_id=owner_id, post_id=post_id, message=f"{comment}", attachment=attachment)
            print(f'Comment "{comment} and {attachment}" posted successfully for https://vk.com/wall-{owner_id}_{post_id}.')
    except Exception as e:
        print(f'Error posting comment: {str(e)}')
        if isinstance(e, ApiError) and e.code == 17:
            with open('invalid_acc.txt', 'a') as f:
                f.write(f'{log_pass[0]}:{log_pass[1]} - Phone required\n')

#MAIN PROGRAMM.

async def main():
    comment_dict, post_info_list, match_info_list, log_pass_list = await open_files()

    start = time.time()
    for log_pass in log_pass_list:
        try:
            vk_session = vk_api.VkApi(log_pass[0], log_pass[1], app_id=API_ID, client_secret=API_SECRET)
            vk_session.auth()
            global vk
            vk = vk_session.get_api()
        except Exception as e:
            print(f'VK Response: {str(e)}')
            if str(e) == 'Bad password':
                with open('invalid_acc.txt', 'a') as f:
                    f.write(f'{log_pass[0]}:{log_pass[1]} - Invalid password or login\n')
            continue
        try:
            user = vk.users.get(fields='first_name, last_name')[0]
        except vk_api.exceptions.ApiError as e:
            print(f'VK Response: {str(e)}')
            if isinstance(e, ApiError) and e.code == 5:
                with open('invalid_acc.txt', 'a') as f:
                    f.write(f'{log_pass[0]}:{log_pass[1]} - Need mobile authentication or account is blocked.\n')
                sys.exit()
        
        author_id = user['first_name'] + " " + user['last_name']
        print(author_id)

        tasks = []
        keys = list(comment_dict.keys())
        values = list(comment_dict.values())
        comment, photo_path = keys[0], values[0]
        for index, element in enumerate(post_info_list):
            if index == len(match_info_list):
                continue
            owner_id, post_id = element
            if photo_path:
                tasks.append(asyncio.create_task(post_comment(comment, photo_path, post_id, -owner_id, log_pass)))
            else:
                tasks.append(asyncio.create_task(post_comment(comment, None, post_id, -owner_id, log_pass)))

        tasks.append(asyncio.create_task(take_screenshot(log_pass, post_info_list, match_info_list, author_id)))
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                for task in tasks:
                    task.cancel()

    end = time.time() - start
    print(f'Time of working: {end}')

if __name__ == '__main__':
    asyncio.run(main())

    
