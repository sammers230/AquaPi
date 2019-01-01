# AquaPi
Automated water changer and auto top off with flask web server to monitor and control.

I have started building this project to automate doing water changes to my marine aquarium and include the auto top off so that whilst water changes are being done the ATO is locked out.
Ontop of the automated water changes the system is long term to be built so that all that the system can fill a storage container that has had salt put in and will automate the filling of the container and run a small internal pump to assist mixing, the system will also intermittently run the mixing pump every couple days just to ensure of no settlement.

The Changer.py file is included as it is the existing running file that had no flask server and only ran through the terminal and with GPIO inputs to run parts fo the code and update an Epaper display with times, the epaper files havent been included in this repository and the lines in the Changer.py file have been (#) as this is something I would liek to reintroduce once the flask server and the app is running properly.

This project has been built on a Raspberry Pi 2B / Zero W with both flask and schedule installed so that the system can be monitored / controlled through a web page and have the main cycle run at a scheduled time. 

This project is very much in its infancy and I myself am working with a very big learning curve as I have no real background of coding so there is most likely some very basic errors and very messy coding so I apologise in advance and greatly welcome assistance to write this code properly and efficiently.
