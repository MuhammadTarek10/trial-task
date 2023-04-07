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
        # if ord(c) >= 2304 and ord(c) <= 2431:
        #     return True
        if unicodedata.name(c).startswith("DEVANAGARI") and unicodedata.category(c) == "Lo":
            return True
    return False



def extract_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "course-title"))
        )
    finally:
        driver.quit()
    return element


class Extractor:
    def __init__(self) -> None:
        self.driver: webdriver.Chrome = self.getDriver()
        self.url: str = None
        self.innerUrls: list = None
        self.pageRight: bool = True
        self.hindiUrls: bool = True
        self.imagesResolutions: bool = True
        self.workingButtons: bool = True
        self.output: dict[str:list] = {}

    def getDriver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def testGoogle(self) -> str:
        self.driver.get("https://google.com")
        return self.driver.page_source

    def startTesting(self, data: list) -> None:
        for url in data:
            self.url = url
            if not self.testPage():
                self.output[self.url] = "Page not working"
                continue
            elif not self.testWorkingButtons():
                self.output[self.url] = "Buttons not working"
                continue
            elif not self.testImagesResolutions():
                self.output[self.url] = "Images not working"
                continue
            elif not self.testHindiUrls():
                self.output[self.url] = "Inner pages not translated"
                continue

    def testPage(self) -> bool:
        if self.url:
            return True

    def testWorkingButtons(self) -> bool:
        return True

    def testImagesResolutions(self) -> bool:
        return True

    def testHindiUrls(self) -> bool:
        if self.url:
            self.driver.get(self.url)
            self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
            if self.getTextAndCheck():
                self.innerUrls = [a["href"] for a in self.soup.find_all("a", href=True)]
                self.innerUrls = [url for url in self.innerUrls if url.startswith("/")]
                return self.checkInner()

    def getTextAndCheck(self):
        allText = filter(None, self.soup.get_text().split("\n"))
        for text in allText:
            if isHindi(text):
                return True
        return False

    def checkInner(self):
        flag = True
        if self.innerUrls:
            import random
            for inner in random.choices(self.innerUrls, k=4):
                url = f"{self.url}{inner}"
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
]

if __name__ == "__main__":
    extractor = Extractor()
    extractor.startTesting(data)
    print(extractor.output)
