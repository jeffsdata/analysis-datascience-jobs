# -*- coding: utf-8 -*-
import logging
import pandas as pd
import os
from datetime import date
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from retrying import retry
import glob

class GlassdoorJobScraper:
    @retry(wait_fixed=2000, stop_max_attempt_number=10)
    def __clickAndCatch(self, elem, driver, byitem, selector):
        """ Selenium - Click an element and try again if the element is stale.

        Args:
            elem (Selenium WebElement): The element you want to click
            driver (Selenium WebDriver): The current driver
            byitem (Selenium "By" String): The type you're searching by (By.XPATH, By.CSS_SELECTOR, etc...)
            selector (string): The selector to search for.
        """
        try:
            elem.click()
        except:
            elem = driver.find_element(byitem, selector)
            elem.click()

    def __getJobAttributeAndCatch(self, elem, attributeval):
        """ Get an attribute from a WebElement. If the attribute doesn't exist, Selenium will throw an exception - this returns None in that case.

        Args:
            elem (Selenium WebElement): The element to get the attribute from. 
            attributeval (string): The attribute name

        Returns:
            string: The attribute value or None (if the attribute doesn't exist)
        """
        try:
            return elem.get_attribute(attributeval)
        except:
            return None

    @retry(wait_fixed=2000, stop_max_attempt_number=10)
    def __waitAndClick(self, driver, byitem, selector):
        """ Wait for the element to show up and click it. If it doesn't show up, return None. If it does, click it.

        Args:
            driver (Selenium WebDriver): The current driver
            byitem (Selenium "By" String): The type you're searching by (By.XPATH, By.CSS_SELECTOR, etc...)
            selector (string): The selector to search for.

        Returns:
            Selenium WebElement: The element being search for (or None, if it doesn't exist)
        """
        elem = self.__waitForElement(driver, byitem, selector)
        if(elem is not None):
            self.__clickAndCatch(elem, driver, byitem, selector)
            return elem
        return None

    def __getTextAndCatch(self, driver, byitem, selector):
        """ Get the inner text from an element. If the element doesn't exist, return None. If the element is stale, try to find it and get text again. 

        Args:
            driver (Selenium WebDriver): The current driver
            byitem (Selenium "By" String): The type you're searching by (By.XPATH, By.CSS_SELECTOR, etc...)
            selector (string): The selector to search for.

        Returns:
            string: The element's inner text
        """
        # Selenium will throw an exception if element doesn't exist
        try:
            elem = driver.find_element(byitem, selector)
            if(elem is not None):
                try:
                    return elem.text
                except:
                    return driver.find_element(byitem, selector).text
            return None
        # if element doesn't exist, return None
        except:
            return None

    @retry(wait_fixed=2000, stop_max_attempt_number=10)
    def _waitAndGetText(self, driver, byitem, selector):
        elem = self.__waitForElement(driver, byitem, selector)
        if(elem is not None):
            try:
                return elem.text
            except:
                return driver.find_element(byitem, selector).text
        return None

    @retry(wait_fixed=2000, stop_max_attempt_number=10)
    def __waitForElement(self, driver, byitem, selector):
        """ Wait for an element to show up - if it never shows up, Selenium will throw an exception, so this catches that and returns None.

        Args:
            driver (Selenium WebDriver): The current driver
            byitem (Selenium "By" String): The type you're searching by (By.XPATH, By.CSS_SELECTOR, etc...)
            selector (string): The selector to search for.

        Returns:
            Selenium WebElement: The element you're waiting for (or None if it doesn't show up)
        """
        logger = logging.getLogger(__name__)
        try:
            return WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((byitem, selector))
            )
        # if element never shows up, just skip
        except:
           #logger.info('Boo. Couldn\'t find that...')
           pass
    
    def __getJobDataFromJob(self, jidx, job, row, driver):
        """ For a given job, get all the relevant data.

        Args:
            jidx (int): The current row number for the search results page. 
            job (Selenium WebElement): The current job.
            row (Pandas DataFrame Row): The row for job search metdata.
            driver (Selenium WebDriver): The current driver

        Returns:
            [type]: [description]
        """
        try:
            logger = logging.getLogger(__name__)
            newrow = {}
            newrow["date"] = date.today()
            newrow["jobsource"] = row["source"]
            newrow["jobsearch"] = row["job"]
            newrow["MetroID"] = row["MetroID"]
            try:
                job.click()
            except:
                joblist = driver.find_elements(By.CLASS_NAME, 'react-job-listing')
                job = joblist[jidx]
                job.click()
            # Click "X" on popover, if it exists (occurs on first click)
            if(jidx==0):
                self.__waitAndClick(driver,By.CSS_SELECTOR, '#JAModal > div > div.modal_main.jaCreateAccountModalWrapper > span > svg')
            newrow["jobtitlenorm"] = self.__getJobAttributeAndCatch(job, "data-normalize-job-title")
            newrow["jobeasyapply"] = self.__getJobAttributeAndCatch(job, "data-is-easy-apply")
            newrow["jobisorganic"] = self.__getJobAttributeAndCatch(job, "data-is-organic-job")
            newrow["companyname"] = self.__getTextAndCatch(job, By.CSS_SELECTOR, 'div.align-items-start > a.jobLink > span')
            newrow["jobdaysago"] = self.__getTextAndCatch(job, By.CSS_SELECTOR, 'div[data-test="job-age"]')
            
            currentarticle = self.__waitForElement(driver, By.CSS_SELECTOR, 'article.active')
            
            newrow["companysize"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="EmpBasicInfo"]/div[1]/div/div[1]/span[2]')
            newrow["companyfounded"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="EmpBasicInfo"]/div[1]/div/div[2]/span[2]')
            newrow["companytype"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="EmpBasicInfo"]/div[1]/div/div[3]/span[2]')
            newrow["companyindustry"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="EmpBasicInfo"]/div[1]/div/div[4]/span[2]')
            newrow["companysector"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="EmpBasicInfo"]/div[1]/div/div[5]/span[2]')
            newrow["companyrevenue"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="EmpBasicInfo"]/div[1]/div/div[6]/span[2]')
            newrow["companyrating"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="employerStats"]/div[1]/div[1]')
            newrow["companyratings"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="employerStats"]/div[2]/div[3]/div[2]/div[2]')
            newrow["companyrecommendfriend"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="employerStats"]/div[2]/div[1]/div[1]')
            newrow["companyapproveceo"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="employerStats"]/div[2]/div[2]/div')

            self.__waitAndClick(driver, By.XPATH, '//*[@id="JobDescriptionContainer"]/div[2]')
            jttext = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div[3]/div[1]/div[2]')
            newrow["jobtitle"] = jttext
            logger.info(f'Working on... {jttext}')
            newrow["cityname"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="JDCol"]/div/article/div/div[1]/div/div/div[1]/div/div[1]/div[3]')
            newrow["jobdescription"] = self.__getTextAndCatch(driver, By.CLASS_NAME, 'jobDescriptionContent')
            newrow["wageavg"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="JDCol"]/div/article/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[1]')
            newrow["wagemin"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="JDCol"]/div/article/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[2]/div[3]/span[1]')
            newrow["wagemax"] = self.__getTextAndCatch(driver, By.XPATH, '//*[@id="JDCol"]/div/article/div/div[2]/div[1]/div[2]/div/div[1]/div[1]/div[2]/div[3]/span[2]')
            return newrow
        except Exception as e:
            logger.error("******************** An unexpected error occurred on this job listing. Skipping it.")


    def scrapeAndSaveAllJobDataFromURL(self, row):
        """ From the row's URL, get job posting data for all result pages.
            - Opens the page from row (row["url"])
            - Gathers job posting data for each page in the results.
            - Skips result pages when we already have data

        Args:
            row (Pandas DataFrame Row): The row for job search metdata.
        """
        logger = logging.getLogger(__name__)
        print(os.getcwd())
        files = os.listdir("data/raw")
        files = [x.replace("jobspostings-", "").replace(".csv", "").split("-") for x in files if "jobspostings" in x]
        existingdata = pd.DataFrame(columns=["jobtitle", "MetroID", "pagenum", "date"], data=files)

        driver = webdriver.Chrome()
        driver.get(row["url"])  

        nextbuttonenabled = True
        pagenum = 0
        # Loop Through Pages
        while(nextbuttonenabled):
            currjob = row["job"].replace(" ", "")
            currmetroid = row["MetroID"]
            currdate = str(date.today()).replace("-", "")
            if(existingdata[(existingdata["MetroID"]==str(currmetroid)) & (existingdata["jobtitle"]==currjob) & (existingdata["pagenum"]==str(pagenum)) & (existingdata["date"]==currdate)].shape[0] == 0):
                #if(existingdata[existingdata["MetroID"]==currmetroid and existingdata["jobtitle"]==currjob and existingdata["pagenum"]==pagenum and existingdata["date"]==currdate].shape[1])
                logger.info(f'Working on page... #{pagenum}')
                df = pd.DataFrame()
                joblist = driver.find_elements(By.CLASS_NAME, 'react-job-listing')  
                # Loop through job postings
                for jidx, job in enumerate(joblist):
                    newrow = self.__getJobDataFromJob(jidx, job, row, driver)
                    df = df.append(newrow, ignore_index=True)
                df.to_csv(f'data/raw/jobspostings-{currjob}-{currmetroid}-{pagenum}-{currdate}.csv')
            self.__waitAndClick(driver,By.CSS_SELECTOR, '#JAModal > div > div.modal_main.jaCreateAccountModalWrapper > span > svg')
            nextbutton = self.__waitForElement(driver, By.CSS_SELECTOR, "button.nextButton")
            nextbuttonenabled = nextbutton.is_enabled()
            nextbutton.click()
            pagenum = pagenum + 1



def main():
    """ Gets job search metdata from joburls.csv, and 
        gathers job metadata from each page. 

        Note: Currently filtered to only look at 'data analyst' job searches.
    """
    logger = logging.getLogger(__name__)
    logger.info('Starting the job scraper...')

    gd = GlassdoorJobScraper()
    df = pd.read_csv("data/raw/joburls.csv")
    
    df = df[(df["job"]=="data engineer") & (df["MetroID"]>=20)]
    for i, row in df.iterrows():
        gd.scrapeAndSaveAllJobDataFromURL(row)




if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
