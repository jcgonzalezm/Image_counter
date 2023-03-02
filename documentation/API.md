# API and frontend Documentation

This is the documentation for the inferance API of the Object_count solution.

## Request format

All calls to the API need to be executing following this format:
`curl -F threshold=<LEVEL_ON_DECIMAL_PERC> -F <ADDRESS_OF_THE_IMAGE_TO_BE_SENT> http://0.0.0.0:5000/<ENDPOINT>`

## Avaialble entrypoints

### @object-count

This endpoint will return a dictionary type answer with the object found in current image (current_objects), and sum of all the objects found in all calls during the same application session (total_objects). For every type of object, an object_class will be created with object_class='name of the object' and count='how many of those objects are'

    ```bash
    curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:5000/object-count
    ```

    This will return something similar to:
    ```bash
        {
    "current_objects": [
        {
        "count": 1, 
        "object_class": "person"
        }, 
        {
        "count": 1, 
        "object_class": "tennis racket"
        }, 
        {
        "count": 1, 
        "object_class": "sports ball"
        }
    ], 
    "total_objects": [
        {
        "count": 1, 
        "object_class": "test_object"
        }, 
        {
        "count": 1, 
        "object_class": "person"
        }, 
        {
        "count": 1, 
        "object_class": "tennis racket"
        }, 
        {
        "count": 1, 
        "object_class": "sports ball"
        }
    ]
    }
    ```

### @object-found  

This entrypoint will return us a list of all the objects identified in the current image.
    ```bash
    curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:5000/object-found
    ```

    This will return something similar to:
    ```bash
    [
    "person", 
    "tennis racket", 
    "sports ball"
    ]
    ```

## Building options

The application can be build using 2 distintict AI frameworks and 2 database types. To set out you option, you can execute them prior to the calling of the Flask execution as:

`ENV=<ENVIROMENT> DB_TYPE=<DATABASETYPE> AI_FRAMEWORK=<AIFRAMEWORK> python -m counter.entrypoints.webapp`

Avilable option at this commit are:
ENV: [prod, dev]
DB_TYPE: [mongo, mysql]
AI_FRAMEWORK: [tensor, torch]

Example:
    '''bash
    ENV=prod DB_TYPE=mongo AI_FRAMEWORK=tensor python -m counter.entrypoints.webapp
    ENV=prod DB_TYPE=mysql AI_FRAMEWORK=tensor python -m counter.entrypoints.webapp
    ENV=prod DB_TYPE=mongo AI_FRAMEWORK=torch python -m counter.entrypoints.webapp
    ENV=prod DB_TYPE=mysql AI_FRAMEWORK=torch python -m counter.entrypoints.webapp

    python -m counter.entrypoints.webapp #for DEV
    '''bash

## Frontend

The python application was created on FLASK as API framework and using a Bluiprint & Views design in order to allow escalability. You can find more information about blueprints and views on -> https://flask.palletsprojects.com/en/2.2.x/views/