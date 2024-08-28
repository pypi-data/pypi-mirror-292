"""
Here we are using the https://message.style/app/editor
platform with a Web Scrapper to obtain the nice Discord
images they generate.
"""
from yta_general_utils.experimental.chrome_scrapper import start_chrome, go_to_and_wait_loaded
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep

import json

WEB_URL = 'https://message.style/app/editor'

chrome_driver = None

def __get_chrome_driver():
    if not chrome_driver:
        chrome_driver = start_chrome(False)

    return chrome_driver

def __go_to_website(url):
    go_to_and_wait_loaded(__get_chrome_driver(), url)

def __build_string_json(username: str, user_avatar_url: str, message: str):
    """
    Returns the json that will create the message in the platform,
    but as a string.
    """
    json_content = {
        "content": message,
        "tts": False,
        "username": username,
        "avatar_url": user_avatar_url,
        "embeds": [],
        "components": [],
        "actions": {}
    }

    return json.dumps(json_content, ensure_ascii = False).encode('utf-8').decode('utf-8')

def create_discord_message(username: str, user_avatar_url: str, message: str, output_filename: str):
    if not username:
        raise Exception('No "username" provided')
    
    if not user_avatar_url:
        raise Exception('No "user_avatar_url" provided.')
    
    if not message:
        raise Exception('No "message" provided.')
    
    json_string = __build_string_json(username, user_avatar_url, message)
    TEXT_AREA_ID = 'textarea_to_copy_912312' # a random one

    # We go to the main website
    __go_to_website(WEB_URL)

    # We need to fake a textarea to be able to copy the content
    # as clipboard is not working
    js_code = "var p = document.createElement('textarea'); p.setAttribute('id', '" + TEXT_AREA_ID + "'); p.value = '" + json_string + "'; document.getElementsByTagName('body')[0].appendChild(p);"
    # I create a new element to put the text, copy it and be able to paste
    __get_chrome_driver().execute_script(js_code)

    # Focus on textarea
    textarea = chrome_driver.find_elements(By.ID, TEXT_AREA_ID)[0]
    textarea.click()
    textarea.send_keys(Keys.CONTROL, 'a')
    textarea.send_keys(Keys.CONTROL, 'c')
    # TODO: I can use 'textarea.send_keys(Keys.CONTROL, 'c') to copy, validate
    actions = ActionChains(chrome_driver)
    # actions.key_down(Keys.CONTROL).send_keys('A').key_up(Keys.CONTROL).perform()
    # actions.key_down(Keys.CONTROL).send_keys('C').key_up(Keys.CONTROL).perform()

    # Remove the textarea, it is no longer needed
    js_code = "var element = document.getElementById('" + TEXT_AREA_ID + "'); element.parentNode.removeChild(element);"
    chrome_driver.execute_script(js_code)

    # We will now change the JSON to format the message we want
    go_to_and_wait_loaded(chrome_driver, WEB_URL + '/json')
    
    for i in range(25):  # Manually detected, to focus on json editor
        actions.send_keys(Keys.TAB)
    actions.perform()

    # Select the whole previous json, delete it and paste our own
    actions.key_down(Keys.CONTROL).send_keys('A').key_up(Keys.CONTROL).perform()
    actions.send_keys(Keys.DELETE).perform()
    active_element = chrome_driver.switch_to.active_element
    active_element.click()
    actions.send_keys(Keys.DELETE).perform()
    active_element.send_keys(Keys.CONTROL, 'v')

    # Press the save button
    save_button = chrome_driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
    save_button.click()
    # TODO: This could be a 'wait-for-element-change' waiting,
    # by now it is manually chosen
    sleep(2)
    message_element = chrome_driver.find_element(By.XPATH, '//div[@class="discord-message"]')

    # Save the screenshot with the requested name
    message_element.screenshot(output_filename)

    return


"""
Useful discord messages below

{
  "content": "Welcome to **Embed Generator**! 🎉 Create stunning embed messages for your Discord server with ease!\n\nIf you're ready to start, simply click on the \"Clear\" button at the top of the editor and create your own message.\n\nShould you need any assistance or have questions, feel free to join our [support server](/discord) where you can connect with our helpful community members and get the support you need.\n\nWe also have a [complementary bot](/invite) that enhances the experience with Embed Generator. Check out our [Discord bot](/invite) which offers features like formatting for mentions, channels, and emoji, creating reaction roles, interactive components, and more.\n\nLet your creativity shine and make your server stand out with Embed Generator! ✨",
  "tts": false,
  "embeds": [
    {
      "id": 652627557,
      "title": "About Embed Generator",
      "description": "Embed Generator is a powerful tool that enables you to create visually appealing and interactive embed messages for your Discord server. With the use of webhooks, Embed Generator allows you to customize the appearance of your messages and make them more engaging.\n\nTo get started, all you need is a webhook URL, which can be obtained from the 'Integrations' tab in your server's settings. If you encounter any issues while setting up a webhook, our bot can assist you in creating one.\n\nInstead of using webhooks you can also select a server and channel directly here on the website. The bot will automatically create a webhook for you and use it to send the message.",
      "color": 2326507,
      "fields": []
    },
    {
      "id": 10674342,
      "title": "Discord Bot Integration",
      "description": "Embed Generator offers a Discord bot integration that can further enhance your the functionality. While it is not mandatory for sending messages, having the bot on your server gives you access to a lot more features!\n\nHere are some key features of our bot:",
      "color": 2326507,
      "fields": [
        {
          "id": 472281785,
          "name": "Interactive Components",
          "value": "With our bot on your server you can add interactive components like buttons and select menus to your messages. Just invite the bot to your server, select the right server here on the website and you are ready to go!"
        },
        {
          "id": 608893643,
          "name": "Special Formatting for Mentions, Channels, and Emoji",
          "value": "With the /format command, our bot provides special formatting options for mentions, channel tags, and ready-to-use emoji. No more manual formatting errors! Simply copy and paste the formatted text into the editor."
        },
        {
          "id": 724530251,
          "name": "Recover Embed Generator Messages",
          "value": "If you ever need to retrieve a previously sent message created with Embed Generator, our bot can assist you. Right-click or long-press any message in your server, navigate to the apps menu, and select Restore to Embed Generator. You'll receive a link that leads to the editor page with the selected message."
        },
        {
          "id": 927221233,
          "name": "Additional Features",
          "value": "Our bot also supports fetching images from profile pictures or emojis, webhook management, and more. Invite the bot to your server and use the /help command to explore all the available features!"
        }
      ]
    }
  ],
  "components": [],
  "actions": {}
}
"""