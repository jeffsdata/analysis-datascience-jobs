library(tidyverse)
library(tidytext)

job_descriptions <- data.frame(lapply(df.final, as.character), stringsAsFactors=FALSE) %>%
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
	select(c("category", "jobdescription"))

custom_stopwords <- data_frame(word = c("â", "scientist", "data scientist", "amazon", "microsoft", "cirium", "data engineer",
																				"expedia", "analyst", "senior data analyst", "cerner", "senior business", "business analyst",
																				"mattersight", "engineer", "pimco", "kapsch", "swedish", "ods", "the ods"))

# 1-Grams (word)
job_words <- job_descriptions %>%
	unnest_tokens(word, jobdescription) %>%
	count(category, word, sort = TRUE) %>%
	anti_join(custom_stopwords, by = c("ngram" = "word")) %>%
	anti_join(stop_words, by = c("ngram" = "word"))

colnames(job_words) <- c("category", "ngram", "n")

# Add 2-grams
job_words_2gram <- job_descriptions %>%
	unnest_tokens(ngram, jobdescription, token="ngrams", n=2)%>%
	count(category, ngram, sort = TRUE)

all_the_grams <- job_words %>%
	union(job_words_2gram) %>%
	anti_join(custom_stopwords, by = c("ngram" = "word"))

words_per_category <- all_the_grams %>% 
	group_by(category) %>% 
	summarize(total = sum(n))

job_words_combined <- left_join(job_words, words_per_category) %>%
	bind_tf_idf(ngram, category, n) %>%
	filter(n > 10 & 
				 category == "1 - Data Scientist")

job_words_combined %>%
	arrange(desc(tf_idf)) %>%
	mutate(ngram = factor(ngram, levels = rev(unique(ngram)))) %>% 
	group_by(category) %>% 
	top_n(50) %>% 
	ungroup() %>%
	ggplot(aes(ngram, tf_idf, fill = category)) +
	geom_col(show.legend = FALSE) +
	labs(x = NULL, y = "tf-idf") +
	facet_wrap(~category, ncol = 2, scales = "free") +
	coord_flip()