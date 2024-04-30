# AQ Scoring
This repository contains code to calculate population within a project buffer, as part of the air quality scoiring for TIP projects. 

# Requirements
These install instructions assume [Anaconda](https://www.anaconda.com/) is installed to run Python. Download and install the standard, free Anaconda software if needed and accept all defaults. [Visual Studio Code](https://code.visualstudio.com/) is not required, but is a free and helpful tool for debugging and editing code. This code was tested on PSRC's model servers, which have 512 GB RAM. The code will likely run on a local laptop, but may be quite slow since these machines may have as little as 16 GB of RAM. 

# Setup
Clone this repository to a local directory. Open an Anaconda prompt and change directory to the location of the local repository (e.g., C:/users/staff/transportation/aq_scoring). 

## Virtual Environment
From the Anaconda prompt in this project directory root, enter the following to install a virtual environment that includes all required versions of Python libraries:
 - `conda env create -f environment.yml`

After install is complete enter: 
- `conda activate AQ_SCORING`. 
You should see (AQ_SCORING) in the prompt. This indicates that the prompt is using all the libraries associated with the virtual environment. This environment will need to be activated using this command any time a new prompt is opened.

## Elmer Connections
Check that the ODBC driver is installed on your workspace by searching for it in Windows - it should show up as ODBC Data Sources (64-bit). If not, [download the ODBC Driver 17 here](https://go.microsoft.com/fwlink/?linkid=2200732) and follow the install instructions, selecting all defaults. If there are problems connecting with Elmer, contact Brice or Chris Peak. 

## Input Data and Configuration
Configuration settings for the script are controlled by **configuration.toml**. Projects to be buffered and analyzed should be stored in a shapefile, with the path defined in **project_dir**. The code assumes project shapefile includes the following columns:
- projID (project ID for reference)
- App_ID (unique application ID)

Outputs are written locally to the working directory, in an folder called **outputs** by default. 

Users should specify the population data in **ofm_estimate_year** and **ofm_vintage**. Generally, these should be the same year and reflect the most current available data. 

The **buffer_distance** configuration specifies distance around each project to consider. The value is in feet and is set to 1/2 mile (2,640 feet) by default. 

# Usage and Outputs
To run the script, use the Anaconda prompt and ensure the AQ_SCORING environment is active (see above). From the project directory enter:
`python process_data.py`

On a high-powered server the script takes about 90 seconds to run. Less powerful machines will take longer, perhaps several minutes. When the script is complete, the total processing time will be reported and the outputs will be available at **outputs\project_population.csv.**
