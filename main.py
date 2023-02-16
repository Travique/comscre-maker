import asyncio
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import vk_api


async def take_screenshot(post_id):

    #Need try to do or Telegram bot with settings
    #Or add Python UI
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    browser = webdriver.Chrome(options=options)
    browser.get(f'https://vk.com/wall-{vk_session.token["user_id"]}_{post_id}')
    #Need to check urls for VK.COM posts.
    #I will add this in next update

    await asyncio.sleep(3)

    screenshot_path = f'post_comments_{post_id}.png'
    browser.save_screenshot(screenshot_path)
    browser.quit()

    print(f'Screenshot saved to {screenshot_path}!')


async def post_comment(comment, post_id):

    #owner_id = vk_session.token['user_id'] only for tests.
    #Need to change it after alpha.
    #owner_id = '111111111' for example.
    #We can take it from: https://vk.com/victim?w=wall<owner_id>_<post_id>%2Fall
    #Can be different comment and screen photos!
    vk.wall.createComment(owner_id=vk_session.token['user_id'], post_id=post_id, message=comment) 
    print(f'Comment "{comment}" posted successfully!')


async def main():
    with open('login.txt', 'r') as f:
        login, password = f.read().strip().split(':')

    with open('post_id.txt', 'r') as f:
        post_id = int(f.read().strip())

    global vk_session
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    global vk
    vk = vk_session.get_api()

    comments = ['This is my first comment!']

    tasks = []
    tasks.append(asyncio.create_task(take_screenshot(post_id)))
    for comment in comments:
        tasks.append(asyncio.create_task(post_comment(comment, post_id)))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
