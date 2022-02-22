library("tidyverse")

df <- read.csv("jobs/dsj-all.csv",header=TRUE)

query_degree_bachelor <- c("(^| |(?![a-z]))bs((?![a-z])| |$)", "(^| |(?![a-z]))ba((?![a-z])| |$)", "bachelor")
query_degree_masters <- c("masters", "(^| |(?![a-z]))ma((?![a-z])| |$)")
query_degree_phd <- c("phd")
query_jobtitle_analyst <- c("analyst")
query_jobtitle_datascientist <- c("data scientist", "data science")
query_jobtitle_dataanalyst <- c("data analyst")
query_jobtitle_seniordataanalyst <- c("senior data analyst")
query_jobtitle_dataengineer <- c("data engineer")
query_jobtitle_machinelearningengineer <- c("machine learning engineer", "ml engineer")
query_jobtitle_businessanalyst <- c("business analyst")
query_jobtitle_businessintelligence <- c("(^| |(?![a-z]))bi((?![a-z])| |$)", "business intelligence")
query_jobtitle_level_junior <- c("junior", "entry level", "(^| |(?![a-z]))i|jr|1((?![a-z])| |$)")
query_jobtitle_level_senior <- c("senior", "(^| |(?![a-z]))sr|iii|3((?![a-z])| |$)", "lead")
query_jobtitle_level_architect <- c("architect")
query_jobtitle_level_principle <- c("principle", "principal")
query_jobtitle_level_manager <- c("manager")
query_jobtitle_level_director <- c("director")
query_jobtitle_keyword_research <- c("research")
query_skill_abtesting <- c("a\\/b", "ab testing", "a b testing", "abn testing", "a\\/b\\/n testing", "multivariate test")
query_skill_agile <- c("agile", "scrum")
query_skill_algorithms <- c("algorithm", "big-o", "big o")
query_skill_bigdata <- c("big data", "spark", "hadoop", "hive", "pig", "kafka", "map reduce", "mapreduce", "redshift", "teradata")
query_skill_commandline <- c("bash", "kornshell", "powershell", "power shell")
query_skill_containers <- c("docker", "container", "kubernetes")
query_skill_csharp <- c("c#", "c sharp", "csharp", "dotnet", "\\.net", "mvc", "software development", "software engineer")
query_skill_databases <- c("sql", "postgres", "mongo", "mysql", "access", "relational database", "oracle", "data warehous")
query_skill_datamining <- c("data mining")
query_skill_datapipelines <- c("ssis", "data factory", "pipeline")
query_skill_deeplearning <- c("tensorflow", "pytorch", "torch", "deep learning", "keras", "neural network", "caffe", "mxnet", "cntk")
query_skill_deeplearning_vision <- c("computer vision", "object tracking", "object notation", "image notation", "image classification")
query_skill_deployment <- c("deployment", "productionize")
query_skill_devops <- c("development operations", "devops", "dev ops", "teamcity", "octopus", "jenkins", "puppet")
query_skill_etl <- c("etl", "database development")
query_skill_excel <- c("excel", "solver", "spreadsheet")
query_skill_machinelearning_simple <- c("prediction", "regression", "linear model", "statistical modeling", "predictive analytic", "data modeling")
query_skill_machinelearning_advanced <- 
	c("machine learning", "clustering", "supervised learning", "decision trees", "random forest", "gbm", 
		"gradient boosting machine", "sklearn", "mllib", "sk-learn", "h2o", "anomaly", "causal inference", "reinforcement learning",
		"dimensionality reduction")
query_skill_machinelearning_nlp <- 
	c("nlp", "natural language", "topic modeling", "(^| |(?![a-z]))ner((?![a-z])| |$)", "named entitiy recognition",
		 "sentiment", "(^| |(?![a-z]))lda((?![a-z])| |$)", "nltk", "spacy")
query_skill_machinelearning_timeseries <- c("time-series", "time series")
query_skill_problemsolving <- c("problem solving")
query_skill_python <- c("python", "matplotlib", "pandas", "numpy")
query_skill_r <- c("(^| |(?![a-z]))r((?![a-z])| |$)", "dplyr", "ggplot", "tidyverse", "r studio")
query_skill_reporting <- c("kpi", "metric", "reporting", "trends", "analytics", "analysis", "adhoc report")
query_skill_sas <- c("sas")
query_skill_java <- c("java")
query_skill_julia <- c("julia")
query_skill_scala <- c("scala")
query_skill_simulation <- c("simulation", "monte carlo")
query_skill_sourcecontrol <- c("source control", "git", "tfvc", "tfs", "svn", "subversion", "mercurial", "gitlab")
query_skill_sql <- c("sql")
query_skill_ssrs <- c("ssrs")
query_skill_statistics <- c("statist", "bayes", "probability")
query_skill_testing <- c("(^| |(?![a-z]))qa((?![a-z])| |$)", "quality assurance", "testable code", "test design")
query_skill_userexperience <- c("user experience", "user research", "product research", "(^| |(?![a-z]))ux((?![a-z])| |$)")
query_skill_webanalytics <- c("google analytics", "adobe analytics", "web analytic", "cookies", "internet", "web traffic", "web log", "webtrends")
query_tool_cloudplatform <- c("google cloud", "azure", "aws")
query_tool_datavis <- c("looker", "tableau", "powerbi", "power bi", "spotfire", "visualization", "d3", "matplotlib", "microstrategy")

query_department_humanresources <- c("human resources", "(^| |(?![a-z]))hr((?![a-z])| |$)")
query_department_finance <- c("financ", "payroll", "accounting")
query_department_marketing <- c("marketing", "(^| |(?![a-z]))sem((?![a-z])| |$)", "advertising")
query_department_supplychain <- c("supply chain")
query_department_operations <- c("operations")
query_department_customerservice <- c("customer service")
query_department_it <- c("(^| |(?![a-z]))it((?![a-z])| |$)", "information tech")


## CLEAN THE RESULT SET
df.final <- df %>%
		# Clear Unnecessary Text (ie: remove stars from rating, dash from city/state...)
		mutate(
			companyrating = str_replace(companyrating, " \\?", ""),
			location = str_replace(location, "– ", ""),
			payestimate = str_replace(payestimate, " \\(Glassdoor est\\.\\)", "")
		) %>%
	# only keep jobs that contain one of the matchingJobs
	#filter(grepl(paste(query_jobtitle, collapse="|"), tolower(jobtitle))) %>%
	# get rid of id column, url column
	select(-c("web.scraper.order", "web.scraper.start.url")) %>%
	unique() %>%
	# New columns
	mutate(
		degree_bachelor  = ifelse(grepl(paste(query_degree_bachelor ,collapse="|"), tolower(jobdescription)),1,0),
		degree_masters  = ifelse(grepl(paste(query_degree_masters ,collapse="|"), tolower(jobdescription)),1,0),
		degree_phd  = ifelse(grepl(paste(query_degree_phd ,collapse="|"), tolower(jobdescription)),1,0),
		jobtitle_analyst  = ifelse(grepl(paste(query_jobtitle_analyst ,collapse="|"), tolower(jobtitle)),1,0),
		jobtitle_datascientist  = ifelse(grepl(paste(query_jobtitle_datascientist ,collapse="|"), tolower(jobtitle)),1,0),
		jobtitle_dataanalyst  = ifelse(grepl(paste(query_jobtitle_dataanalyst ,collapse="|"), tolower(jobtitle)),1,0),
		jobtitle_seniordataanalyst  = ifelse(grepl(paste(query_jobtitle_seniordataanalyst ,collapse="|"), tolower(jobtitle)),1,0),
		jobtitle_dataengineer  = ifelse(grepl(paste(query_jobtitle_dataengineer ,collapse="|"), tolower(jobtitle)),1,0),
		jobtitle_machinelearningengineer  = ifelse(grepl(paste(query_jobtitle_machinelearningengineer ,collapse="|"), tolower(jobtitle)),1,0),
		jobtitle_businessanalyst  = ifelse(grepl(paste(query_jobtitle_businessanalyst ,collapse="|"), tolower(jobtitle)),1,0),
		skill_abtesting  = ifelse(grepl(paste(query_skill_abtesting ,collapse="|"), tolower(jobdescription)),1,0),
		skill_agile  = ifelse(grepl(paste(query_skill_agile ,collapse="|"), tolower(jobdescription)),1,0),
		skill_algorithms  = ifelse(grepl(paste(query_skill_algorithms ,collapse="|"), tolower(jobdescription)),1,0),
		skill_bigdata  = ifelse(grepl(paste(query_skill_bigdata ,collapse="|"), tolower(jobdescription)),1,0),
		skill_commandline  = ifelse(grepl(paste(query_skill_commandline ,collapse="|"), tolower(jobdescription)),1,0),
		skill_containers  = ifelse(grepl(paste(query_skill_containers ,collapse="|"), tolower(jobdescription)),1,0),
		skill_csharp  = ifelse(grepl(paste(query_skill_csharp ,collapse="|"), tolower(jobdescription)),1,0),
		skill_databases  = ifelse(grepl(paste(query_skill_databases ,collapse="|"), tolower(jobdescription)),1,0),
		skill_datamining  = ifelse(grepl(paste(query_skill_datamining ,collapse="|"), tolower(jobdescription)),1,0),
		skill_datapipelines  = ifelse(grepl(paste(query_skill_datapipelines ,collapse="|"), tolower(jobdescription)),1,0),
		skill_deeplearning  = ifelse(grepl(paste(query_skill_deeplearning ,collapse="|"), tolower(jobdescription)),1,0),
		skill_deeplearning_vision  = ifelse(grepl(paste(query_skill_deeplearning_vision ,collapse="|"), tolower(jobdescription)),1,0),
		skill_deployment  = ifelse(grepl(paste(query_skill_deployment ,collapse="|"), tolower(jobdescription)),1,0),
		skill_devops  = ifelse(grepl(paste(query_skill_devops ,collapse="|"), tolower(jobdescription)),1,0),
		skill_etl  = ifelse(grepl(paste(query_skill_etl ,collapse="|"), tolower(jobdescription)),1,0),
		skill_excel  = ifelse(grepl(paste(query_skill_excel ,collapse="|"), tolower(jobdescription)),1,0),
		skill_machinelearning_simple  = ifelse(grepl(paste(query_skill_machinelearning_simple ,collapse="|"), tolower(jobdescription)),1,0),
		skill_machinelearning_advanced  = ifelse(grepl(paste(query_skill_machinelearning_advanced ,collapse="|"), tolower(jobdescription)),1,0),
		skill_machinelearning_nlp  = ifelse(grepl(paste(query_skill_machinelearning_nlp ,collapse="|"), tolower(jobdescription)),1,0),
		skill_machinelearning_timeseries  = ifelse(grepl(paste(query_skill_machinelearning_timeseries ,collapse="|"), tolower(jobdescription)),1,0),
		skill_problemsolving  = ifelse(grepl(paste(query_skill_problemsolving ,collapse="|"), tolower(jobdescription)),1,0),
		skill_python  = ifelse(grepl(paste(query_skill_python ,collapse="|"), tolower(jobdescription)),1,0),
		skill_r  = ifelse(grepl(paste(query_skill_r ,collapse="|"), tolower(jobdescription)),1,0),
		skill_reporting  = ifelse(grepl(paste(query_skill_reporting ,collapse="|"), tolower(jobdescription)),1,0),
		skill_sas  = ifelse(grepl(paste(query_skill_sas ,collapse="|"), tolower(jobdescription)),1,0),
		skill_java  = ifelse(grepl(paste(query_skill_java ,collapse="|"), tolower(jobdescription)),1,0),
		skill_julia  = ifelse(grepl(paste(query_skill_julia ,collapse="|"), tolower(jobdescription)),1,0),
		skill_scala  = ifelse(grepl(paste(query_skill_scala ,collapse="|"), tolower(jobdescription)),1,0),
		skill_simulation  = ifelse(grepl(paste(query_skill_simulation ,collapse="|"), tolower(jobdescription)),1,0),
		skill_sourcecontrol  = ifelse(grepl(paste(query_skill_sourcecontrol ,collapse="|"), tolower(jobdescription)),1,0),
		skill_sql  = ifelse(grepl(paste(query_skill_sql ,collapse="|"), tolower(jobdescription)),1,0),
		skill_ssrs  = ifelse(grepl(paste(query_skill_ssrs ,collapse="|"), tolower(jobdescription)),1,0),
		skill_statistics  = ifelse(grepl(paste(query_skill_statistics ,collapse="|"), tolower(jobdescription)),1,0),
		skill_testing = ifelse(grepl(paste(query_skill_testing ,collapse="|"), tolower(jobdescription)),1,0),
		skill_webanalytics  = ifelse(grepl(paste(query_skill_webanalytics ,collapse="|"), tolower(jobdescription)),1,0),
		tool_cloudplatform  = ifelse(grepl(paste(query_tool_cloudplatform ,collapse="|"), tolower(jobdescription)),1,0),
		tool_datavis  = ifelse(grepl(paste(query_tool_datavis ,collapse="|"), tolower(jobdescription)),1,0)
	)

## SUMMARY
df.compare <- df.final %>%
	mutate(category = case_when(
		jobtitle_datascientist == 1 ~ "1 - Data Scientist",
		jobtitle_seniordataanalyst == 1 ~ "2 - Senior Data Analyst",
		jobtitle_dataengineer == 1 ~ "3 - Data Engineer",
		jobtitle_dataanalyst == 1 ~ "4 - Data Analyst",
		jobtitle_machinelearningengineer == 1 ~ "5 - Machine Learning Engineer",
		jobtitle_businessanalyst == 1 ~ "6 - Business Analyst",
		jobtitle_dataanalyst == 0 
			& jobtitle_datascientist == 0 
			& jobtitle_seniordataanalyst == 0 
			& jobtitle_businessanalyst == 0 
			& jobtitle_machinelearningengineer == 0 
			& jobtitle_dataengineer == 0 ~ "7 - Other Data Jobs"
	)) %>%
	group_by(category) %>%
	summarize(count = n(),
						degree_bachelor = mean(degree_bachelor),
						degree_masters = mean(degree_masters),
						degree_phd = mean(degree_phd),
						jobtitle_analyst = mean(jobtitle_analyst),
						jobtitle_datascientist = mean(jobtitle_datascientist),
						jobtitle_dataanalyst = mean(jobtitle_dataanalyst),
						jobtitle_seniordataanalyst = mean(jobtitle_seniordataanalyst),
						jobtitle_dataengineer = mean(jobtitle_dataengineer),
						jobtitle_machinelearningengineer = mean(jobtitle_machinelearningengineer),
						jobtitle_businessanalyst = mean(jobtitle_businessanalyst),
						skill_abtesting = mean(skill_abtesting),
						skill_agile = mean(skill_agile),
						skill_algorithms = mean(skill_algorithms),
						skill_bigdata = mean(skill_bigdata),
						skill_commandline = mean(skill_commandline),
						skill_containers = mean(skill_containers),
						skill_csharp = mean(skill_csharp),
						skill_databases = mean(skill_databases),
						skill_datamining = mean(skill_datamining),
						skill_datapipelines = mean(skill_datapipelines),
						skill_deeplearning = mean(skill_deeplearning),
						skill_deeplearning_vision = mean(skill_deeplearning_vision),
						skill_deployment = mean(skill_deployment),
						skill_devops = mean(skill_devops),
						skill_etl = mean(skill_etl),
						skill_excel = mean(skill_excel),
						skill_machinelearning_simple = mean(skill_machinelearning_simple),
						skill_machinelearning_advanced = mean(skill_machinelearning_advanced),
						skill_machinelearning_nlp = mean(skill_machinelearning_nlp),
						skill_machinelearning_timeseries = mean(skill_machinelearning_timeseries),
						skill_problemsolving = mean(skill_problemsolving),
						skill_python = mean(skill_python),
						skill_r = mean(skill_r),
						skill_reporting = mean(skill_reporting),
						skill_sas = mean(skill_sas),
						skill_java = mean(skill_java),
						skill_julia = mean(skill_julia),
						skill_scala = mean(skill_scala),
						skill_simulation = mean(skill_simulation),
						skill_sourcecontrol = mean(skill_sourcecontrol),
						skill_sql = mean(skill_sql),
						skill_ssrs = mean(skill_ssrs),
						skill_statistics = mean(skill_statistics),
						skill_testing = mean(skill_testing),
						skill_webanalytics = mean(skill_webanalytics),
						tool_cloudplatform = mean(tool_cloudplatform),
						tool_datavis = mean(tool_datavis))
	

