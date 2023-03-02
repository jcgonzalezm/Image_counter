import os

from PIL import ImageDraw, ImageFont

DEBUG_FOLDER = '/tmp/debug/'
ARIAL_TTF_ADDRESS = 'counter/resources/arial.ttf'

class DrawingImage():
    def __init__(self, predictions, image, image_name, objdetectortype):
        self.predictions = predictions
        self.image_name = image_name
        self.objdetectortype = objdetectortype    
        self.image = image
        self.image_draw = ImageDraw.Draw(image, "RGBA")
        self.image_width, self.image_height = image.size
        self.font = ImageFont.truetype(ARIAL_TTF_ADDRESS, 20)
        self.frame_modifier = self._define_frame_modifications()

    @staticmethod
    def _check_tmp_debug_folder():
        if not os.path.exists(DEBUG_FOLDER):
            os.makedirs(DEBUG_FOLDER)

    def _save(self):    
        self._check_tmp_debug_folder()    
        self.image.save(f"{DEBUG_FOLDER}{self.image_name}", "JPEG")

    def draw(self):
        for _, prediction in enumerate(self.predictions):
            self.frame_modifier(prediction)
        self._save()

    def _define_frame_modifications(self):
        '''
        This function will parse the modifications to the distintic types of models that we manage
        #IMPORTANT NOTE this analysis its done on the first 'main' model, no the subsequent ones. We are asuming all subsquent models are from the same framework.
        '''
        available_types_of_models = {'object_count': self._object_count_frame_modification,
                                    'rfcn': self._rfcn_frame_modification,
                                    'fake': self._rfcn_frame_modification}

        return available_types_of_models[self.objdetectortype[0]] 

    def _object_count_frame_modification(self, prediction):
        '''Modifications requiered for 1 single prediction'''
        box = prediction.box
        self.image_draw.rectangle(
            [(box.xmin, box.ymin),(box.xmax, box.ymax)],
            outline='red')

        self.image_draw.text(
            (box.xmin, box.ymin - self.font.getsize(prediction.class_name)[1]),
            f"{prediction.class_name}: {prediction.score}", font=self.font, fill='black')

    def _rfcn_frame_modification(self, prediction):
        '''Modifications requiered for 1 single prediction'''
        box = prediction.box
        self.image_draw.rectangle(
            [(box.xmin * self.image_width, 
            box.ymin * self.image_height),
            (box.xmax * self.image_width, 
            box.ymax * self.image_height)],
            outline='red')
        
        self.image_draw.text(
            (box.xmin * self.image_width, 
            box.ymin * self.image_height - self.font.getsize(prediction.class_name)[1]),
            f"{prediction.class_name}: {prediction.score}", font=self.font, fill='black')



