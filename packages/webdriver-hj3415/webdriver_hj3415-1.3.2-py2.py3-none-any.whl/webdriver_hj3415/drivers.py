from selenium.webdriver.remote.webdriver import WebDriver
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.902.62 Safari/537.36 Edg/92.0.902.62",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",

    # Add more User-Agent strings as needed
]


def get(**kwargs) -> WebDriver:
    """
    browser: safari, edge, chrome...(default: chrome)\n
    driver_version: 크롬드라이버 버전(default:None)
    headless: (default: True)\n
    geolocation: (default: False)
    """
    browser_type = kwargs.get("browser", "chrome")
    driver_version = kwargs.get("driver_version", None)
    headless = kwargs.get("headless", True)
    geolocation = kwargs.get("geolocation", False)

    """
    os_n_browser = {
        "Darwin": "safari",
        "Linux": "chrome",
        "Windows": "edge"
    }

    if browser_type == '':
        # 운영체제별로 적절한 드라이버를 받아온다.
        os_it = utils.get_pc_info()['os']
        print(f"OS : {os_it}")
        browser_it = os_n_browser[os_it]
    else:
        assert browser_type in os_n_browser.values(), f"Browser type must be among {os_n_browser.values()}."
        browser_it = browser_type
    """

    if browser_type == 'safari':
        driver = get_safari()
    elif browser_type == 'edge':
        driver = get_edge()
    elif browser_type == 'chrome':
        driver = get_chrome(driver_version=driver_version, headless=headless, geolocation=geolocation)
    elif browser_type == 'firefox':
        driver = get_firefox(headless=headless)
    else:
        raise Exception(f"browser type error : {browser_type}")
    return driver


def get_safari() -> WebDriver:
    from selenium import webdriver

    # safari는 headless 모드를 지원하지 않음
    print("For using safari driver. You should safari setting first, 설정/개발자/원격자동화허용 on")
    driver = webdriver.Safari()
    print(f'Get safari driver successfully...')
    return driver


def get_edge() -> WebDriver:
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service as EdgeService
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    print(f'Get edge driver successfully...')
    return driver


def get_firefox(headless=True) -> WebDriver:
    # refered from https://www.zenrows.com/blog/selenium-user-agent#what-is-selenium-user-agent
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

    # Set up Firefox profile
    profile = FirefoxProfile()

    # Choose a random User-Agent from the list
    random_user_agent = random.choice(user_agents)
    profile.set_preference("general.useragent.override", random_user_agent)

    # Set up Firefox options
    firefox_options = Options()
    if headless:
        firefox_options.add_argument("-headless")
    firefox_options.profile = profile

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install())
                               , options=firefox_options)

    print(f'Get firefox driver successfully...')
    return driver


def get_chrome(driver_version: str = None, temp_dir: str = '', headless=True, geolocation=False) -> WebDriver:
    """ 크롬 드라이버를 반환
    Args:
        driver_version: 드라이버를 못찾는 에러가 가끔있으며 이때는 드라이버 버전을 넣어주면 해결됨
        temp_dir : 크롬에서 다운받은 파일을 저장하는 임시디렉토리 경로(주로 krx에서 사용)
        headless : 크롬 옵션 headless 여부
        geolocation : geolocation 사용여부

    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options

    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")

    # Choose a random User-Agent from the list
    random_user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"--user-agent={random_user_agent}")

    # Create a new instance of ChromeDriver with the desired options
    driver = webdriver.Chrome(options=chrome_options)

    prefs = {}

    if geolocation:
        # https://copyprogramming.com/howto/how-to-enable-geo-location-by-default-using-selenium-duplicate
        prefs.update(
            {
                'profile.default_content_setting_values': {'notifications': 1, 'geolocation': 1},
                'profile.managed_default_content_settings': {'geolocation': 1},
            }
        )

    if temp_dir != '':
        # print(f'Set temp dir : {temp_dir}')
        # referred from https://stackoverflow.com/questions/71716460/how-to-change-download-directory-location-path-in-selenium-using-chrome
        prefs.update({'download.default_directory': temp_dir,
                      "download.prompt_for_download": False,
                      "download.directory_upgrade": True})

    chrome_options.add_experimental_option('prefs', prefs)

    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    capabilities = DesiredCapabilities().CHROME
    capabilities.update(chrome_options.to_capabilities())


    # 크롬드라이버 준비
    # https://pypi.org/project/webdriver-manager/

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(driver_version=driver_version).install()), options=chrome_options)

    print(f'Get chrome driver successfully... headless : {headless}, geolocation : {geolocation}')
    return driver
