# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import glob

class TaggingData:
    def makeDataTaggingData(self):
        path = "data\\raw"
        all_files = glob.glob(path + "/jobspostings-*.csv")
        df_from_each_file = (pd.read_csv(f) for f in all_files[:5])
        concatenated_df   = pd.concat(df_from_each_file, ignore_index=True)
        concatenated_df["processed_description"] = concatenated_df.apply(lambda x: x["jobdescription"].replace(",",""), axis=1)
        stringlist = ",".join(concatenated_df["processed_description"].to_list())
        text_file = open("data/processed/jobdescriptions-csv.txt", "w", encoding='utf-8')
        n = text_file.write(stringlist)
        text_file.close()
        wee = "yay"

class DataScienceJobs:
    def __turnWageIntoNumber(self, wageval):
        if "K" in str(wageval):
            return int(wageval.replace("K","000").replace("$",""))
        elif("/yr (est.)" in str(wageval)):
            return int(wageval.replace("$","").replace(",","").replace(" /yr (est.)",""))
        else:
            return wageval

    def makeDataScienceJobsData(self):
        logger = logging.getLogger(__name__)
        logger.info('--> Reading in files...')
        df = pd.concat(map(pd.read_csv, glob.glob('data/raw/jobspostings-*.csv')))
        
        logger.info('--> Filtering to only data science jobs...')
        df["DataSci_Ind"] = df.apply(lambda x: True if "data scientist" in str(x["jobtitle"]).lower() else False, axis=1)
        df = df[df["DataSci_Ind"]]
        
        # Change Wage values into integers
        logger.info('--> Converting wage strings into numbers...')
        df["wageavg"] = pd.to_numeric(df.apply(lambda x: self.__turnWageIntoNumber(x["wageavg"]), axis=1), errors='coerce')
        df["wagemin"] = pd.to_numeric(df.apply(lambda x: self.__turnWageIntoNumber(x["wagemin"]), axis=1), errors='coerce')
        df["wagemax"] = pd.to_numeric(df.apply(lambda x: self.__turnWageIntoNumber(x["wagemax"]), axis=1), errors='coerce')
        
        df.to_csv("data/processed/data-science-jobs.csv")



def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)

    ### Job Description Tagging Data
    # logger.info('making final data set from raw data')
    # td = TaggingData()
    # td.makeDataTaggingData()
    # logger.info("Yeet! All done.")

    ### Data Scientist Job Data
    logger.info('STEP 2: Making data scientist jobs...')
    dj = DataScienceJobs()
    dj.makeDataScienceJobsData()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
