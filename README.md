# ini_to_json
Need to setup python3 virtual environment to run (I just used pycharm for everything)  

How to use:
1- in ini directory, add whichever ini file you want to convert to new json output schema format, or edit an existing ini file  
2- in output_files directory, put all the output_files corresponding to that technology in the correct technology folder. It is ok to overwrite files that already exist, since we want to have the most updated version of the output files  
3- If there are new table_mappings, please add those following the format to the table_mappings directory  
4- Change SOLUTION_PATH global variable in .py file to whatever solution folder you are targeting (ex: C:\core-services-api)
5- run ini_to_json  
6- your new json output schema file should be in the json directory  
7- Move the output schema json file to the corresponding technology folder in the api (should be: {API_PATH}/LLamasoft.Services.{technology_name}.OutputProcessing)
