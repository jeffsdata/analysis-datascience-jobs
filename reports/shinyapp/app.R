#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(ggplot2)

# Define UI for application that draws a histogram
ui <- fluidPage(
   
   # Application title
   titlePanel("Skills and Attributes of Data Jobs"),
   
   # Sidebar with a slider input for number of bins 
   sidebarLayout(
      sidebarPanel(
         selectInput("selectattr",
         						h3("Attribute"),
         						choices = colnames(df.compare[,-1:-2])),
         br(),
         hr(),

         helpText(h4("What's selected?")),
         htmlOutput("help_text")
      ),
      
      # Show a plot of the generated distribution
      mainPanel(
         plotOutput("distPlot")
      )
   )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
   
	output$help_text <- renderText({ 
		listofmatches = case_when(
			input$selectattr =="degree_bachelor" ~ paste(query_degree_bachelor, collapse = ', '),
			input$selectattr =="degree_masters" ~ paste(query_degree_masters, collapse = ', ' ),
			input$selectattr =="degree_phd" ~ paste(query_degree_phd, collapse = ', ' ),
			input$selectattr =="jobtitle_analyst" ~ paste(query_jobtitle_analyst, collapse = ', ' ),
			input$selectattr =="jobtitle_datascientist" ~ paste(query_jobtitle_datascientist, collapse = ', '),
			input$selectattr =="jobtitle_dataanalyst" ~ paste(query_jobtitle_dataanalyst, collapse = ', '),
			input$selectattr =="jobtitle_seniordataanalyst" ~ paste(query_jobtitle_seniordataanalyst, collapse = ', '),
			input$selectattr =="jobtitle_dataengineer" ~ paste(query_jobtitle_dataengineer, collapse = ', '),
			input$selectattr =="jobtitle_machinelearningengineer" ~ paste(query_jobtitle_machinelearningengineer, collapse = ', '),
			input$selectattr =="skill_abtesting" ~ paste(query_skill_abtesting, collapse = ', '),
			input$selectattr =="skill_agile" ~ paste(query_skill_agile, collapse = ', '),
			input$selectattr =="skill_algorithms" ~ paste(query_skill_algorithms, collapse = ', '),
			input$selectattr =="skill_bigdata" ~ paste(query_skill_bigdata, collapse = ', '),
			input$selectattr =="skill_commandline" ~ paste(query_skill_commandline, collapse = ', '),
			input$selectattr =="skill_containers" ~ paste(query_skill_containers, collapse = ', '),
			input$selectattr =="skill_csharp" ~ paste(query_skill_csharp, collapse = ', '),
			input$selectattr =="skill_databases" ~ paste(query_skill_databases, collapse = ', '),
			input$selectattr =="skill_datamining" ~ paste(query_skill_datamining, collapse = ', '),
			input$selectattr =="skill_datapipelines" ~ paste(query_skill_datapipelines, collapse = ', '),
			input$selectattr =="skill_deeplearning" ~ paste(query_skill_deeplearning, collapse = ', '),
			input$selectattr =="skill_deeplearning_vision" ~ paste(query_skill_deeplearning_vision, collapse = ', '),
			input$selectattr =="skill_deployment" ~ paste(query_skill_deployment, collapse = ', '),
			input$selectattr =="skill_devops" ~ paste(query_skill_devops, collapse = ', '),
			input$selectattr =="skill_etl" ~ paste(query_skill_etl, collapse = ', '),
			input$selectattr =="skill_excel" ~ paste(query_skill_excel, collapse = ', '),
			input$selectattr =="skill_machinelearning" ~ paste(query_skill_machinelearning, collapse = ', '),
			input$selectattr =="skill_machinelearning_nlp" ~ paste(query_skill_machinelearning_nlp, collapse = ', '),
			input$selectattr =="skill_machinelearning_timeseries" ~ paste(query_skill_machinelearning_timeseries, collapse = ', '),
			input$selectattr =="skill_problemsolving" ~ paste(query_skill_problemsolving, collapse = ', '),
			input$selectattr =="skill_python" ~ paste(query_skill_python, collapse = ', '),
			input$selectattr =="skill_r" ~ paste(query_skill_r, collapse = ', '),
			input$selectattr =="skill_reporting" ~ paste(query_skill_reporting, collapse = ', '),
			input$selectattr =="skill_sas" ~ paste(query_skill_sas, collapse = ', '),
			input$selectattr =="skill_java" ~ paste(query_skill_java, collapse = ', '),
			input$selectattr =="skill_julia" ~ paste(query_skill_julia, collapse = ', '),
			input$selectattr =="skill_scala" ~ paste(query_skill_scala, collapse = ', '),
			input$selectattr =="skill_simulation" ~ paste(query_skill_simulation, collapse = ', '),
			input$selectattr =="skill_sourcecontrol" ~ paste(query_skill_sourcecontrol, collapse = ', '),
			input$selectattr =="skill_sql" ~ paste(query_skill_sql, collapse = ', '),
			input$selectattr =="skill_ssrs" ~ paste(query_skill_ssrs, collapse = ', '),
			input$selectattr =="skill_statistics" ~ paste(query_skill_statistics, collapse = ', '),
			input$selectattr =="skill_webanalytics" ~ paste(query_skill_webanalytics, collapse = ', '),
			input$selectattr =="tool_cloudplatform" ~ paste(query_tool_cloudplatform, collapse = ', '),
			input$selectattr =="tool_datavis" ~ paste(query_tool_datavis, collapse = ', ')
		)
		
		paste0("You have selected <b>", input$selectattr,"</b>. This is looking for the word(s): ", listofmatches, "." )
	})
	
	output$distPlot <- renderPlot({
	  # data
	  x    <- df.compare %>% select(c(category, count, thirdcol = input$selectattr))
	  
	  # draw bar chart with selected column values
	  ggplot(x,aes(x=paste(category, " (",count,")"), y=thirdcol))	+ 
	  	geom_bar(stat="identity") + 
	  	ylim(0,1) + 
	  	xlab("Job Title (count)") +
	  	ylab(input$selectattr) +
	  	theme(axis.title.x = element_text("Arial", "bold", "#3a3a3c", 16, margin = margin(t = 20, r = 0, b = 0, l = 0))) +
	  	theme(axis.title.y = element_text("Arial", "bold", "#3a3a3c", 16, margin = margin(t = 0, r = 20, b = 0, l = 0))) +
	  	theme(axis.text.x = element_text(angle = 45, hjust = 1)) + 
	  	geom_text(aes(y = thirdcol + 0.03, label = paste0(round(thirdcol * 100, digits = 1),"%")))
	})
}

# Run the application 
shinyApp(ui = ui, server = server)

