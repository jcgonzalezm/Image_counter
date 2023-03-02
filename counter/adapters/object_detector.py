import json
from io import BytesIO
from typing import List, BinaryIO, Dict, Callable

import numpy as np
import requests
from PIL import Image

from counter.domain.models import Prediction, Box
from counter.domain.ports import ObjectDetector
from counter.domain.models import Models, ObjectsClassNamesTriggers


class ModelScoringOrchestrator(ObjectDetector):
    '''
    IMPORTANT: On the definition that we are managing for subsequent model, they will respond with UNIQUE images recognized. 
    Meaning that the respond we are asuming will be a list with an unique Prediction object. 
    The original model idenified ALL models in image, in our case we will further DEFINE the objects found
    '''

    def __init__(self, models: Dict[Models, ObjectDetector]):
        self.__models = models
        self.__objects_to_subsequent_model = ObjectsClassNamesTriggers.available_triggers()


    def return_object_type_of_models(self):
        return [model.model_name for _, model in self.__models.items()]


    def _predict_sub_model(self, sub_model, image):
        '''Will check if the submodel apointed in the triggers was submited in the models of the __init__ class'''
        if not sub_model in self.__models:
            return []
        else:
            return self.__models[sub_model].predict(image)


    def execute_sub_models(self, objects_found , image):
        '''
        If model available in self.__models then it will predict them
        IMPORTANT NOTE As we only have 1 singlugar model at the end of the Models.CAT_BREED_COLOR we will return 'fat_grey_cat'
        '''
        sub_model = self.__objects_to_subsequent_model[objects_found.class_name]
        sub_model_respond = self._predict_sub_model(sub_model, image)

        objects_found_in_sub_models = []
        for sub_model_obj_found in sub_model_respond: # may find different breeds
            #TODO #updated_predictions.append(Prediction(class_name=sub_model_obj_found.class_name, score=sub_model_obj_found.detection_score, box=sub_model_obj_found.box))
            objects_found_in_sub_models.append(Prediction(class_name='fat_grey_cat', score=sub_model_obj_found.score, box=sub_model_obj_found.box)) # We do not have a second model
        return objects_found_in_sub_models


    def predict(self, image: BinaryIO) -> List[Prediction]:
        '''
        In this function we will execute **predict** on each model passed to us, and if a subsequent model its used, 
            the result thatr trigger it will be replaced by the result of the subsequent one.
        Ex: 
        Models.OBJECT_IDENTIFIER result:   [Prediction(class_name='cat', score=0.999763191, box=Box(xmin=0.373155236, ymin=0.364091396, xmax=0.547027707, ymax=0.811043084)), 
                                    Prediction(class_name='tennis racket', score=0.991948068, box=Box(xmin=0.502959073, ymin=0.628664196, xmax=0.635707498, ymax=0.809880435))]
        
        subsecuent_indentifier result:  [Prediction(class_name='Orange cat', score=0.999763191, box=Box(xmin=0.373155236, ymin=0.364091396, xmax=0.547027707, ymax=0.811043084)), 
                                        Prediction(class_name='tennis racket', score=0.991948068, box=Box(xmin=0.502959073, ymin=0.628664196, xmax=0.635707498, ymax=0.809880435))]
        '''
        obj_identifier = self.__models.get(Models.OBJECT_IDENTIFIER)
        obj_identifier_respond = obj_identifier.predict(image)

        updated_predictions = []
        for objects_found in obj_identifier_respond:
            if objects_found.class_name in self.__objects_to_subsequent_model:
                updated_predictions += self.execute_sub_models(objects_found, image)
            else:
                updated_predictions.append(objects_found)
        return updated_predictions

class AIFrameworkDetector(ObjectDetector):
    @staticmethod
    def _build_classes_dict():
        with open('counter/adapters/mscoco_label_map.json') as json_file:
            labels = json.load(json_file)
            return labels


    @staticmethod
    def _to_np_array(image: BinaryIO):
        image_ = Image.open(image)
        (im_width, im_height) = image_.size
        return np.array(image_.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


class FakeObjectDetector(AIFrameworkDetector):
    def __init__(self):
        self.model_name = 'fake'
    def predict(self, image: BinaryIO) -> List[Prediction]:
        return [Prediction(class_name='cat',
                           score=0.999190748,
                           box=Box(xmin=0.367288858, ymin=0.278333426,
                                   xmax=0.735821366, ymax=0.6988855))]


class TFSObjectDetector(AIFrameworkDetector):
    def __init__(self, host, port, model_name):
        self.model_name = model_name
        self.url = f"http://{host}:{port}/v1/models/{self.model_name}:predict"        


    def predict(self, image: BinaryIO) -> List[Prediction]:
        np_image = super()._to_np_array(image)
        predict_request = '{"instances" : %s}' % np.expand_dims(np_image, 0).tolist()
        response = requests.post(self.url, data=predict_request)
        predictions = response.json()['predictions'][0]
        return self.__raw_predictions_to_domain(predictions)


    def __raw_predictions_to_domain(self, raw_predictions: dict) -> List[Prediction]:
        num_detections = int(raw_predictions.get('num_detections'))
        processed_predictions = []
        for i in range(0, num_detections):
            detection_box = raw_predictions['detection_boxes'][i]
            box = Box(xmin=detection_box[1], ymin=detection_box[0], xmax=detection_box[3], ymax=detection_box[2])
            detection_score = raw_predictions['detection_scores'][i]
            detection_class = raw_predictions['detection_classes'][i]
            labels = super()._build_classes_dict()
            class_name = {label['id']: label['display_name'] for label in labels}
            processed_predictions.append(Prediction(class_name=class_name[detection_class], score=detection_score, box=box))
        return processed_predictions


class PTObjectDetector(AIFrameworkDetector):
    def __init__(self, host, port, model_name):
        self.model_name = model_name
        self.url = f"http://{host}:{port}/predictions/{self.model_name}"


    def predict(self, image: BinaryIO) -> List[Prediction]:
        image_array = Image.fromarray(super()._to_np_array(image))
        image2bytes = BytesIO()
        image_array.save(image2bytes, format="PNG")
        image2bytes.seek(0)
        image_as_bytes = image2bytes.read()
        response = requests.post(self.url, data=image_as_bytes)
        predictions = response.json()
        return self.__raw_predictions_to_domain(predictions , self.parse_torch_model)       
        

    def parse_torch_model(self, object_identified):
        obj_class_list = list(object_identified.keys())
        obj_class_list.remove('score')
        obj_class_name = obj_class_list[0]
        return Prediction(class_name = obj_class_name,
                            score = object_identified['score'], 
                            box = Box(xmin = object_identified[obj_class_name][2],
                                    xmax = object_identified[obj_class_name][3],
                                    ymin = object_identified[obj_class_name][1],
                                    ymax = object_identified[obj_class_name][0]))


    def __raw_predictions_to_domain(self, raw_predictions: dict, parser: Callable) -> List[Prediction]:
        processed_predictions = []
        for _,raw_detection in enumerate(raw_predictions):
            detection = parser(raw_detection)
            processed_predictions.append(detection)
        return processed_predictions