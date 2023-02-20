import asyncio
import re
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import vk_api
import time 
import random
import os

#SETTINGS.

API_ID = "2685278"
API_SECRET = "hHbJug59sKJie78wjrH8"
TIME_SLEEP = 5.1

#OPENING ALL FILES.

post_info_list = []
match_info_list = []
log_pass = []
comments_list = []
tasks = []
names = ['Posts', 'Credentinals', 'Comments']

with open('login.txt') as f:
    for line in f:
        login, password = line.strip().split(':')
        log_pass.append((login, password))
            
with open('post_info.txt', 'r') as f:
    post_info = f.read().strip()
    
with open('comments.txt', 'r') as f:
    comments = f.read().strip()
    
comments_list = comments.split('\n')
post_info_list = post_info.split('\n')
    
for index, element in enumerate(post_info_list):
    if index == len(post_info_list) + 1:
        continue
        
    match = re.search(r'vk\.com/wall-(\d+)_(\d+)', post_info_list[index])
        
    if match:
        owner_id = int(match.group(1))
        post_id = int(match.group(2))
        match_info_list = match_info_list + [(owner_id, post_id)]

for i, lst in enumerate([post_info_list, log_pass, comments_list]):
    if not lst or '' in lst:
        print(f"{names[i]} is empty or contains an empty string")
        input("Press Enter to exit")
        quit()

print(log_pass)
    
#DEF FOR CREATING POSTS AND SCREENS.
        
async def take_screenshot(log_pass, post_info_list, match_info_list):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    await asyncio.sleep(TIME_SLEEP)
    
    browser = webdriver.Chrome(options=options)

    try:
        username = log_pass[0][0]
        password = log_pass[0][1]
        
        browser.get('https://vk.com/login')

        username_field = browser.find_element(By.XPATH, "//input[@name='login']")
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)

        time.sleep(TIME_SLEEP)

        password_field = browser.find_element(By.XPATH, "//input[@name='password']")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(TIME_SLEEP)

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
        print(f'Selenium Response: {str(e)}')
        browser.quit()


async def post_comment(comment, post_id, owner_id):
    
    try:
        print(f'https://vk.com/wall-{owner_id}_{post_id} is waiting for comment.')
        vk.wall.createComment(owner_id=-owner_id, post_id=post_id, message=comment)
        time.sleep(TIME_SLEEP)
        print(f'Comment {comment} posted successfully for https://vk.com/wall-{owner_id}_{post_id}.')
        
    except Exception as e:
        print(f'Error posting comment "{comment}": {str(e)}')
        return
        
#MAIN PROGRAMM.

async def main():
    start = time.time()

    while len(log_pass) != 0:
        try:
            global vk_session
            vk_session = vk_api.VkApi(log_pass[0][0], log_pass[0][1], app_id=API_ID, client_secret=API_SECRET)
            vk_session.auth()
            global vk
            vk = vk_session.get_api()

            if len(comments_list) == 0:
                print("Add new comments!")
                #break
            else:
                comment = comments_list[random.randrange(0, len(comments_list))]
                comments_list.remove(comment)
        
        except Exception as e:
            print(f'VK Response: {str(e)}')
            #continue

        for index, element in enumerate(match_info_list):
            if index == len(match_info_list) +1:
                continue
            tasks.append(asyncio.create_task(post_comment(comment, match_info_list[index][1], match_info_list[index][0])))
                
        #if error in tasks we have check this shit
        tasks.append(asyncio.create_task(take_screenshot(log_pass, post_info_list, match_info_list)))    
        results = await asyncio.gather(*tasks, return_exceptions=True)

        log_pass.pop(0)
            
        for result in results:
            if isinstance(result, Exception):
                for task in tasks:
                    task.cancel()

    end = time.time() - start 
    print(f'Time of working: {end}')


if __name__ == '__main__':
    asyncio.run(main())

    
