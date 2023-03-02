# Machine Learning & Hexagonal Architecture

The main treat of the project its the implementation of an Hexagonal Architecture in a ML based system, showing the perks of it in order to treat the ML layer as the 'center' of the several plugins.

The model used in this example has been taken from 
[IntelAI](https://github.com/IntelAI/models/blob/master/docs/object_detection/tensorflow_serving/Tutorial.md)

---

## :closed_book: Table of Contents

- [:clipboard: Project Description](#Project_description)
- [:rocket:Getting Started](#hammer_and_wrench-getting-started)
- [:mage_man: Usage](#mage_man-usage)
- [:open_book: Documentation](#computer-credits)

---

## :clipboard: Project Description

We will encapuslate in this repo a AI powered object recognizer tool. By sending an image to the AI, it will identify all the objects in the image and inform us only those that suprass a confidence threshold of accuracy. All the executions findings that up pass the threshold, will be going to be storage in databases for further use. We will as well identify in which part of the images the objects are been identified for further testing and debbing processes.

In our to replicate databases and AI servers, 4 Docker containers :whale: are going to be build specifically for:
* [![MongoDB][MongoDB]][https://www.mongodb.com/]
* [![MySQL][MySQL]][https://www.mysql.com/]
* [![TensorFlow Serving][TensorFlow Serving]][https://www.tensorflow.org/tfx/guide/serving]
* [![Torchserve][Torchserve]][https://pytorch.org/serve/]

NOTE: On our executions we will only work with 1 database service and with 1 AI framework.

## :hammer_and_wrench: Getting Started

In the following you will review the prerequits that you must comply before even downloadin the project and a subsecuent list of steps in order for build and start your application.

### Prerequisites

Please, be absolutly sure that you have:
*   A Linux machine with at least 8gb RAM and 5gb of space in disc, and AVX instruction specification.
*   Have a user with root accesses
*   On it should be installed:
    -   Docker _OPTIONAL 20.10.12_
    -   Python>=3.8,<=3.10
    -   python[your vserion]-dev


### Building App

Please follow this steps in order for setting up your application:

1. Download/move this repository in an empty folder of your Linux machine
2. Decompress it `tar object_count_master.zip`
3. _OPTIONAL_ Remove the .zip file with `rm object_count_master.zip`
4. Go into our project `cd object_count_master`
5. Let us cretae a virtual enviroment for our project. Execute the followings commands: _Execute them one by one_

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
5. We need to build and run our Docker containers. Please execute the following comand. It will take some minutes to complete :coffee: :

    ```bash
    source ./_containers/build_containers.sh
    ```

   The terminal will start printing a bunch of stuff, please ignore them. At the end you should see something as: \
   `---------------CONTAINERS UP AND RUNNING--------------`
   If any problem has araised, a notification below the previous message will be shown.

6. Now as a last step. Please execute:
    ```bash
    ENV=prod python -m counter.entrypoints.webapp
    ```
    Now your application should be up and running :slightly_smiling_face:

## :mage_man: Usage

From the same folder you execute the previous steps, you can send images to your app in order to receive information of the objectes found on it.
The API request needs to be structure as:
    ```bash
    curl -F threshold=<LEVEL_ON_DECIMAL_PERC> -F <ADDRESS_OF_THE_IMAGE_TO_BE_SENT> http://0.0.0.0:5000/<ENDPOINT>
    ```

There primarly 2 endpoints: object-count and object-found. You can call them by: \
    ```bash
    curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:5000/object-count
    curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:5000/object-found
    ```

## :open_book: Documentation and simple test

Additional documentation its available in: `$(pwd)/documentation/`
You can execute an overall testing by `python test.py` on project root folder.