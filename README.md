# text_composer

text_composer is a CLI tool that composes text blocks according to a predefined series.

## Overview
The text blocks (paragraphs) are listed in one or multiple json file(s). The blocks may contain variables.  
In a second json file, the text blocks are combined to series. The series may contain fix values for the variables of the blocks.  

The user can choose one series which will create a jinja template.  
After that, the program fills the fix variables from the series for the final text.  
If there are variables, that can't be found in the series' definition, the user is asked to enter the needed values.
