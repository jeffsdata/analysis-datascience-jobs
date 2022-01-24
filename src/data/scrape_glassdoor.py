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
        try:
            elem.click()
        except:
            elem = driver.find_element(byitem, selector)
            elem.click()

    def __getJobAttributeAndCatch(self, elem, attributeval):
        try:
            elem.get_attribute(attributeval)
        except:
            pass

    @retry(wait_fixed=2000, stop_max_attempt_number=10)
    def __waitAndClick(self, driver, byitem, selector):
        elem = self.__waitForElement(driver, byitem, selector)
        if(elem is not None):
            self.__clickAndCatch(elem, driver, byitem, selector)
            return elem
        return None

    def __getTextAndCatch(self, driver, byitem, selector):
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
            logger.error("*** An unexpected error occurred on this job listing. Skipping it.")
            logger.error("Error is:", e)

    def scrapeAndSaveAllJobDataFromURL(self, row):
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
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Starting the job scraper...')

    gd = GlassdoorJobScraper()
    df = pd.read_csv("data/raw/joburls.csv")
    df = df[df["job"]=='data analyst']
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
