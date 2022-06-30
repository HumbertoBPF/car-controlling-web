# car-controlling-web

:information_source: Overview

This repository is the Django web application that is used in the car games of the repository https://github.com/HumbertoBPF/car-controlling. 
This web application stores the scores and accounts of the players in a SQLite database. The scores are sent from the games via a Restful API (also implemented in the
Django application of this repository) and the accounts can be created through a website implemented in this repository or through the Android application of the 
repository https://github.com/HumbertoBPF/car-controlling-mobile. In addition, a visualization of the game rankings and of the profiles is also provided.

:computer: Website

As mentioned, one of the features of this Django application is a website where users can create and access their accounts and visualize their scores. Below some 
screenshots are provided to show these functionalities in a browser:

- Signup page:

![image](https://user-images.githubusercontent.com/31226297/175855147-1814ba2c-0229-487a-a777-b0afaf06cb68.png)

- Login page:

![image](https://user-images.githubusercontent.com/31226297/175855180-8ecb2ccb-b4fe-46d1-8c9a-9d7e3be0f132.png)

- Homepage:

![image](https://user-images.githubusercontent.com/31226297/176579109-c45a6d13-09bb-44e0-9f7e-03f207733d90.png)

- Rankings page:

![image](https://user-images.githubusercontent.com/31226297/175855285-d98de194-9fe7-4bb7-aeff-cedaaf728b07.png)

- Profile page:

![image](https://user-images.githubusercontent.com/31226297/176578996-80bfc98a-608e-4619-80f0-cd024f24e2f7.png)

:arrow_down: Installation instructions

This section describes how to install and run this project on any machine. All that is going to be presented was tested on Windows, but it is probably similar for other OS. 

First of all, you must have Python installed on your OS (the version used to build the project was Python 3.10). Then, it is necessary to install the following Python libraries and frameworks, which can be done by using the requirements.txt file on the root of the root folder:
 
- Install django (pip install django). Version used to build the project was Django 4.0.5
- Install pillow (pip install pillow). Version used to build the project was 9.1.1
- Install djangorestframework (pip install djangorestframework). Version used to build the project was 3.13.1

Finally, you can run "python manage.py runserver" from the root folder on the command line. This should launch the server on the local port 8000. Type "localhost:8000/dashboard" on your browser. It should exhibit the home page of the website.
