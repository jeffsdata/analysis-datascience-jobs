# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import numpy as np
import glob
from datetime import date

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

    def __isANumber(self, num):
        try:
            pd.to_numeric(num)
            return True
        except:
            return False

    def __turnRevenueToNumber(self, rev):
        splitter = str(rev).split(" ")
        if("Unknown" in splitter):
            return np.nan
        elif("million" in splitter):
            if(splitter[0]=="Less"):
                return 500000
            else:
                return int(str(splitter[0]).replace("$", "")) * 1000000
        elif("billion" in splitter):
            return int(str(splitter[0]).replace("$", "").replace("+","")) * 1000000000
        else:
            return np.nan

    def __turnCompanySizeToNumber(self, comp):
        if("Employ" in str(comp)):
            return str(comp).split(" ")[0].replace("+", "")
        return np.nan

    def __checkContainsList(self, value, titlelist):
        return any(title in str(value).lower() for title in titlelist)

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

        df["jobdaysago"] = [str(x).replace("d+", "").replace("d", "") for x in df["jobdaysago"]]
        df["companyratings"] = [str(x).replace(" Ratings", "").replace(" Rating", "") for x in df["companyratings"]]

        # Revenue, sector, industry, type - data shift for those without a company founded date
        logger.info('--> Data shift: company founded, type, industry, sector, revenue...')
        df["companyfounded_isanumber"] = df["companyfounded"].apply(self.__isANumber)
        df["companyrevenue"] = df.apply(lambda x: x["companysector"] if "$" in str(x["companysector"]) else x["companyrevenue"], axis=1)
        df["companysector"] = df.apply(lambda x: x["companyindustry"] if not x["companyfounded_isanumber"] else x["companysector"], axis=1)
        df["companyindustry"] = df.apply(lambda x: x["companytype"] if not x["companyfounded_isanumber"] else x["companyindustry"], axis=1)
        df["companytype"] = df.apply(lambda x: x["companyfounded"] if not x["companyfounded_isanumber"] else x["companytype"], axis=1)
        df["companyfounded"] = df.apply(lambda x: np.nan if not x["companyfounded_isanumber"] else x["companyfounded"], axis=1)

        df["companyfounded_yearsago"] = [date.today().year - x for x in pd.to_numeric(df["companyfounded"], errors="coerce")]

        df["companyfounded_yearsago_isnan"] = pd.isnull(df["companyfounded_yearsago"])
        df["companyfounded_yearsago"].fillna(df["companyfounded_yearsago"].mean(skipna=True), inplace=True)

        df["companyrevenue"] = [self.__turnRevenueToNumber(x) for x in df["companyrevenue"]]

        df["companysize"] = [self.__turnCompanySizeToNumber(x) for x in df["companysize"]]

        # Job Title Processing - Level
        title_junior = ["junior", "jr ", "jr.", "entry level", "college", "university", "associate", "gradu"]
        df["jobtitle_junior"] = df.apply(lambda x: self.__checkContainsList(x["jobtitle"], title_junior), axis=1)

        title_senior = ["senior", " ii", "sr ", "sr.", " iv", "mid"]
        df["jobtitle_senior"] = df.apply(lambda x:  self.__checkContainsList(x["jobtitle"], title_senior), axis=1)

        title_lead = ["lead"]
        df["jobtitle_lead"] = df.apply(lambda x:  self.__checkContainsList(x["jobtitle"], title_lead), axis=1)

        title_manager = ["manager"]
        df["jobtitle_manager"] = df.apply(lambda x: self.__checkContainsList(x["jobtitle"], title_manager), axis=1)

        title_director = ["director"]
        df["jobtitle_director"] = df.apply(lambda x: self.__checkContainsList(x["jobtitle"], title_director), axis=1)

        title_staff = ["staff"]
        df["jobtitle_staff"] = df.apply(lambda x: self.__checkContainsList(x["jobtitle"], title_staff), axis=1)

        title_princ = ["principle"]
        df["jobtitle_principle"] = df.apply(lambda x: self.__checkContainsList(x["jobtitle"], title_princ), axis=1)

        title_arch = ["architect"]
        df["jobtitle_architect"] = df.apply(lambda x: self.__checkContainsList(x["jobtitle"], title_arch), axis=1)

        # Job Skills
        skills = [
            { "abtesting": ["a/b", "ab testing", "a b testing", "abn testing", "a/b/n testing", "multivariate test"] },
            { "agile": ["agile", "scrum"] },
            { "algorithms": ["algorithm", "big-o", "big o", "data structures"] },
            { "bigdata": ["big data", "spark", "hadoop", "hive", "pig", "kafka", "map reduce", "mapreduce", "redshift", "teradata", "large scale", "petabyte scale"] },
            { "commandline": ["bash", "kornshell", "powershell", "power shell", "command line"] },
            { "containers": ["docker", "container", "kubernetes"] },
            { "databases": ["sql", "postgres", "mongo", "mysql", "access", "relational database", "oracle", "data warehous", "cosmos"] },
            { "datapipeline": ["ssis", "data factory", "pipeline", "airflow"]},
            { "datavis": ["looker", "tableau", "powerbi", "power bi", "spotfire", "visualization", "d3", "matplotlib", "microstrategy", "dashboard", "business intelligence", " bi "]},
            { "deeplearning": ["tensorflow", "pytorch", "torch", "deep learning", "keras", "neural network", "caffe", "mxnet", "cntk"]},
            { "devops": ["development operations", "devops", "dev ops", "teamcity", "octopus", "jenkins", "puppet", "mlops", "machine learning operations", "machine learning ops"]},
            { "etl": ["etl", "database develop", "data warehouse develop"]},
            { "excel": ["excel", "solver", "spreadsheet"]},
            { "machinelearning_basic": ["prediction", "regression", "linear model", "statistical modeling", "predictive analytic", "data modeling"]},
            { "machinelearning_advanced": ["machine learning", "clustering", "supervised learn", "decision trees", "random forest", "gbm", 
                                            "gradient boosting machine", "sklearn", "mllib", "sk-learn", "h2o", "anomaly", "causal inference", 
                                            "reinforcement learn", "dimensionality reduc", "unsupervised learn", "churn", "ltv", "lifetime value",
                                            "collaborative filtering", "recommendation engine", "recommender"] },
            { "nlp": ["nlp", "natural language", "topic modeling", "named entitiy recognit","sentiment", "nltk", "spacy"]},
            { "timeseries": ["time-series", "time series"]},
            { "lang_python": ["python", "matplotlib", "pandas", "numpy"] },
            { "lang_r": ["dplyr", "ggplot", "tidyverse", "r studio", " r ", "statistical software", " r.", " r,"]},
            { "lang_csharp": ["c#", "c sharp", "csharp", "dotnet"] },
            { "lang_cplusplus": ["c++", "cplusplus", "cpp"]},
            { "lang_java": ["java"]},
            { "lang_julia": ["julia"]},
            { "lang_scala": ["scala"]},
            { "lang_sas": [" sas "]},
            { "lang_sql": ["sql", "database lang", "query data"]},
            { "product": ["product direction", "product analy", "data product"]},
            { "simulation": ["simulation", "monte carlo"]},
            { "sourcecontrol": ["source control", "git", "tfvc", "tfs", "svn", "subversion", "mercurial", "gitlab"]},
            { "webanalytics": ["google analytics", "adobe analytics", "web analytic", "cookies", "internet", "web traffic", "web log", "webtrends"]},
            { "cloud_gcp": ["google cloud"]},
            { "cloud_azure": ["azure"]},
            { "cloud_aws": ["aws"]}, 
            { "degree_bachelors": ["bachelor", "bs degree", "ba degree", "b.s.", "b.a."]},
            { "degree_masters": ["masters"]},
            { "degree_phd": ["phd"]}
            ]

        for skill in skills:
            key = list(skill.keys())[0]
            df[f'skill_{key}'] = df.apply(lambda x: self.__checkContainsList(x["jobdescription"], skill.get(key)), axis=1)

        # standardize nans
        df.fillna(np.nan, inplace=True)

        df.to_csv("data/processed/data-science-jobs-2022.csv")



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
