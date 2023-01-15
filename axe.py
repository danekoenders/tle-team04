

from pymongo import MongoClient
client = MongoClient('localhost', 8444)
db = client.sites
sites = db.sites

def scan_website(url):
    from selenium import webdriver
    from time import sleep
    from selenium.webdriver.chrome.options import Options
    from axe_selenium_python import Axe
    from selenium.common.exceptions import InvalidSessionIdException

    CHROMEDRIVER_PATH = '/usr/local/bin/chromedriver'
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                            chrome_options=chrome_options)
    # sleep(3)

    driver.get(url)
    #driver.close()

    
    axe = Axe(driver)
    # Inject axe-core javascript into page.
    axe.inject()

    # Run axe accessibility checks.
    results = axe.run()
    # Write results to file
    axe.write_results(results["violations"], 'a11.json')
    # sites.insert_one({"site_name":url, "issues_count": len(results["violations"]), "issues": results["violations"]})
    driver.close()


    # driver.quit()
    # Assert no violations are found
    #assert len(results["violations"]) == 0, axe.report(results["violations"])
    #report= axe.report(results["violations"])
    # print(report)




