from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def isHindi(character) -> bool:
    import unicodedata
    for c in character:
        if unicodedata.name(c).startswith("DEVANAGARI") and unicodedata.category(c) == "Lo":
            return True
    return False

def isHighResolution(image) -> bool:
    return image.find("blur") == -1
    # TODO: remove
    import requests
    from io import BytesIO
    from PIL import Image
    response = requests.get(image)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    if width >= 500 and height >= 500:
        return True
    return False


class Extractor:
    def __init__(self) -> None:
        self.driver: webdriver.Chrome = self.getDriver()
        self.waiter: WebDriverWait = WebDriverWait(self.driver, 10)
        self.url: str = None
        self.innerUrls: list = None
        self.pageRight: bool = True
        self.hindiUrls: bool = True
        self.imagesResolutions: bool = True
        self.workingButtons: bool = True
        self.output: dict[str:list] = {}

    def getDriver(self) -> webdriver.Chrome:
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--headless")
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-usage")
        
        prefs = {"profile.managed_default_content_settings.images":2}
        chromeOptions.headless = True


        chromeOptions.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chromeOptions)

    def testGoogle(self) -> str:
        self.driver.get("https://google.com")
        return self.driver.page_source

    def startTesting(self, data: list) -> None:
        for url in data:
            self.url = url
            self.output[self.url] = []
            if not self.testPage():
                self.output[self.url] = "Wrong Page"
                continue
            if not self.testWorkingButtons():
                self.output[self.url].append("Javascript dropdown not working properly")
            if not self.testImagesResolutions():
                self.output[self.url].append("Images not high resolution")
            if not self.testHindiUrls():
                self.output[self.url].append("Inner pages not translated")

    def testPage(self) -> bool:
        self.driver.get(self.url)
        print(f"{self.url}: Page")
        try:
            self.driver.find_element(By.XPATH, '//*[@class="symbol-classcentral-navy symbol-medium hidden large-up-block"]')
            return True
        except:
            return False

    def testWorkingButtons(self) -> bool:
        # TODO: still working
        self.driver.get(self.url)
        print(f"{self.url}: Buttons")
        return True
        try:
            button1 = self.driver.find_element(By.XPATH, '//*[@id="page-home"]/div[1]/header/div[1]/nav/div[1]/button[1]')
            button2 = self.driver.find_element(By.XPATH, '//*[@id="page-home"]/div[1]/header/div[1]/nav/div[2]/a')
            try:
                button1.click()
                # //*[@id="page-home"]/div[1]/header/div[1]/nav/div[1]/nav
            except:
                pass
            try:
                # //*[@id="page-home"]/div[1]/header/div[1]/nav/div[2]/div
                pass
            except:
                pass
        except:
            return False
        return True

    def testImagesResolutions(self) -> bool:
        self.driver.get(self.url)
        print(f"{self.url}: Image")
        try:
            images = self.driver.find_elements(By.XPATH, '//img')
            for image in images:
                if not isHighResolution(image.get_attribute("src")):
                    return False
        except:
            pass
        return True

    def testHindiUrls(self) -> bool:
        if self.url:
            self.driver.get(self.url)
            self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
            if self.getTextAndCheck():
                self.innerUrls = [a["href"] for a in self.soup.find_all("a", href=True)]
                return self.checkInner()

    def getTextAndCheck(self)->bool:
        allText = filter(None, self.soup.get_text().split("\n"))
        for text in allText:
            if isHindi(text):
                return True
        return False

    def checkInner(self)->bool:
        flag = True
        if self.innerUrls:
            import random
            for inner in random.choices(self.innerUrls, k=4):
                url = f"{self.url}{inner}"
                print(f"{self.url}: Hindi")
                self.driver.get(url)
                self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
                if not self.getTextAndCheck():
                    flag = False
                    break
        return flag


data = [
    "https://graceful-sunburst-78f35d.netlify.app/www.classcentral.com/index.html",
    "https://ammardab3an99.github.io/",
    "https://sinistersup.github.io/classcentral-hindi/",
    "https://class-central.vercel.app/www.classcentral.com/index.html",
    "https://www.afternic.com/forsale/NA.CO?utm_source=TDFS&utm_medium=sn_affiliate_click&utm_campaign=TDFS_Affiliate_namefind_direct7&traffic_type=CL3&traffic_id=Namefind"
    "https://sinistersup.github.io/classcentral-hindi/",
]

if __name__ == "__main__":
    extractor = Extractor()
    extractor.startTesting(data)
    print(extractor.output)
