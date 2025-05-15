from modules.WebDriverInstaller import *
from modules.AditivosTools import *

args = {
    'auto_detect_browser': True,
    'chrome': False,
    'firefox': False,
    'edge': False,
    'safari': False,
    'custom_browser_location': '',
    'no_headless': False,
}

driver = None
webdriver_path = None
browser_name = GOOGLE_CHROME
custom_browser_location = None if args['custom_browser_location'] == '' else args['custom_browser_location']
webdriver_installer = WebDriverInstaller(browser_name, custom_browser_location)

if args['auto_detect_browser']:
    result = webdriver_installer.detect_installed_browser()
    if result is not None:
        browser_name = result[0]
        webdriver_installer = WebDriverInstaller(browser_name, custom_browser_location)
    else: # if a supported browser was not found, we try to use Selenium Manager
        args['skip_webdriver_menu'] = True 
else:
    if args['chrome']:
        browser_name = GOOGLE_CHROME
    elif args['firefox']:
        browser_name = MOZILLA_FIREFOX
    elif args['edge']:
        browser_name = MICROSOFT_EDGE
    elif args['safari']:
        browser_name = APPLE_SAFARI
    webdriver_installer = WebDriverInstaller(browser_name, custom_browser_location)

webdriver_path, custom_browser_location = webdriver_installer.menu()
driver = initSeleniumWebDriver(browser_name, webdriver_path, custom_browser_location, (not args['no_headless']))

tools = AditivosTools(driver)
results = tools.scrapeAdditives()
tools.save_to_db(results)
