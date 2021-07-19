# VehicleTracer
An application to trace your vehicle path from security cameras of the city.

Outcome:
![Graph.gif](https://github.com/ayushakash990/VehicleTracer/blob/main/graph.gif)

(Note that the processing time has been cut down in this gif file to show the results faster. Original file will differ by having some processing time delay shown by a spinner. Execute locally to know more)


## Project Setup
1. Clone the project directory.
2. Create a virtual environment with python 2.7 and download the dependencies from requirements.txt using the below command:
   __pip install -r requirements.txt__
3. Create a directory named __cameraClips__ at the same level as __pretrained_OCR__.
4. Download camera clips from the below google drive link and paste them in __cameraClips__ directory.
   __https://drive.google.com/drive/folders/1krftQFv82gRdjU7-Xm7Cr7O4SOC7TSxI?usp=sharing__
5. Start django server using __python3 manage.py runserver__.
