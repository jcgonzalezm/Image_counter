# Backend documentation

The code was structured on an Hexagonal desgin leaving available ports for the: fronted (API), model inference and database connections.
For a full diagram of the process, please reffer to the document ..

The strcture of the coding was using an Object Oriented Programming approach. More information available on: https://docs.python.org/3/tutorial/classes.html
In this area only mayor concepts after the frontend execution will be explained:

## config folder

__config.py__ its the main getway for the backend. the primarly pupose of it its to
1. Identify which enviroment was requested and if its found on available Enviroments.
2. Create the CountDetectedObjects.

__enviroments.py__ holds the available class objects for each enviroment and their own specifications:
1. Each of its class returns an Enviroment obj (ABS class) which define the methods for connecting to the databases and AI servers

## domain folder

actions.py holds the base class of the predictor obj: CountDetectedObjects. By its own represents the executor of the model. Meaning that it in charge of predict, save results, save debugging and return respond.

__predictions.py__ will include additional procudes exetables primarly by the CountDetectedObjects

__ports.py__ is the abstract constructor of the abstract classes that interfeer in the process as ObjectDetector, ObjectCountRepo, Enviroment

__models.py__ its the encompensation of the concret class that the solution manage (@dataclasses). They represent the most minimums elements of the model such as Box, Prediction, CountResponse, Models and ObjectsClassNamesTriggers. This last one holds the trigger class_names for any subsequent model. If a class_name a specific object its found, and it turns out that we may what to execute another *more specific* model on top of it, out ObjectsClassNamesTriggers class will hold all the class_name triggers and which model do they trigger.
Ex: if 'cat' its found by *Models.OBJECT_IDENTIFIER*, and our ObjectsClassNamesTriggers={'cat': Models.CAT_BREED} then Models.CAT_BREED will be executed over the same image. (This process its done by the *ModelScoringOrchestrator*)

__debug.py__ define the Draw obj which has the objective of parsing the objectes found by the AI into a graphical representation over the sampling images, as a way for us to review the accruacy of the finding and using afterwards. 

## adapters

The objective of all objects and processes inside the adapters folder its to create bridges acroos the ports functinoalities in a way that mantains them 'almost' intactly.

__count_repo.py__ will hold the procedures for saving the resulting information of each prediction made by the AI. In it we define, 3 distintict objects, all of which are 'childs' from ObjectDetector (minimal ABS class of anything found)
* *CountMongoDBRepo*: responsable of managing the mongodb read and update procedures
* *CountMySQLDBRepo*: responsable of managing the mysql read and update procedures, as well as the connections to it.
    1. As CountMySQLDBRepo needs to be treat it's own connection by each operation it execute on the database, a wrapper decorator its in place in order to execute _stablish_connection and _close_connection before and after each execution. 
    This way any new addtional method, will not have the need to call them at begging and end, but rather only the decorator its needed.
    2. The updating of the values on the tables, was optimized in order to execute a sinlge INSERT statement with multiply VALUES. The parsing of this query its done on: define_values_to_update
* *CountInMemoryRepo*: Its the simulation used on the DEV to hold counting only in the application memory storage (if the apps die, all information its lost)

__object_detector.py__ holds the refference to all types of models and how they will be called from __actions.py__ CountDetectedObjects. The main focus in here its to build the necesary processes for treating all the variabilities and distinctive calls that the resultings CountDetectedObjects may have. The following objects inherit from ObjectDetector:
* *ModelScoringOrchestrator*: its an orchestrator of the models to be call the a sinlge request. Meaning that, if we are in the need to execute several subsequent models into a single image, our orchestrator will:
    1. Proceed to identify available models
    2. Execute them
    3. Review if any class_name its inside the appointed triggers for other models (ObjectsClassNamesTriggers)
        3.1 If it is: Then execute subsequent model 
        3.2 Substitute previoius results for the new ones
    4. Loop over step 3 until no class_name was found in triggers
    5. Return a final output. 
* *AIFrameworkDetector*: Represent the existinace of an AI Framework used by the model.
* *FakeObjectDetector*: Represent a fake AI server. It will return a mock of results.
* *TFSObjectDetector*: Its the TensorFlow server object in charge of calling the server and parsing results.
* *PTObjectDetector*: Its the Torchserve server object in charge of calling the server and parsing results.