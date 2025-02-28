
### Goal
The goal is to develop a BERT model to detect the information types each sentence of a comment/post of a github issue is providng in order to support various software engineering activities. 

### Dataset 
The dataset and taxonomy of the types of information has been taken from the following paper:  *__Analysis and Detection of Information Types of Open Source Software Issue Discussions by Deeksha Arya, Wenting Wang, Jin L.C. Guo, Jinghui Cheng__*. 

### Taxonomy 
This is a multi-class classification problem. The following 13 information types will be detected: 
1. Action on Issue
2. Bug Reproduction
3. Contribution and Commitment 
4. Expected Behaviour
5. Investigation and Exploration
6. Motivation 
7. Observed Bug Behaviour
8. Potential New Issues and Requests
9. Social Conversation 
10. Solution Discussion
11. Task Progress
14. Usage 
15. Workarounds

This project will be in python language. 

### Liscence
The project is liscensed under MIT License. Get to know about the [liscense](https://github.com/tamanna037/InformationTypesDetectionNLP/blob/main/LICENSE) from here.

### How to contribute
For contribution guidelines, kindly check [CONTRIBUTING.md](https://github.com/tamanna037/InformationTypesDetectionNLP/blob/main/CONTRIBUTING.md) file. 

### How to run 
Note: Run this project in an environment that has **GPU available**.
* Download the repository and run the python file from 'code' folder in your loacal machine.             
                                or
* Use docker to run the scripts following these steps:
  1. Install [docker desktop](https://www.docker.com/get-started/) compatible with your machine.  
  2. Clone the repository of the project
  3. Open terminal and go tho folder of the repository.
  4. Run this command
   ```
    docker build --no-cache -t infotypes .
   ``` 
  5. In the docker app, go to **image** tab and find **infotypes** image and then run it. 
  6. Next, go to **containers** tab, open terminal from the running container. 
  7. Run following commands:
     ```
      cd ./code
     ``` 
     ```
      python InfoTypesDetectionOss.py
     ``` 
  8. The code will start running and training the model. You can see the output below
