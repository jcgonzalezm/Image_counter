from io import BytesIO
from flask import Flask, request, jsonify
from flask.views import View
from counter.config import config

class AW(object):  # ApplicationWrapper

    def __init__(self):
        self.app = self.create_app()
        self.count_action = config.get_count_action()
        self.add_rules()

    class object_listing(View):
        methods = ['POST']

        def __init__(self, AW):
            self.AW = AW
            parsed_request = self.AW.parse_request(request)
            self.threshold = parsed_request.get('threshold', None)
            self.image = parsed_request.get('image', None)

        def dispatch_request(self):
            count_response = self.AW.count_action.execute(self.image, self.threshold)
            return jsonify([object_detected.object_class for object_detected in count_response.current_objects])        

    class object_detection(View):
        methods = ['POST']

        def __init__(self, AW):
            self.AW = AW
            parsed_request = self.AW.parse_request(request)
            self.threshold = parsed_request.get('threshold', None)
            self.image = parsed_request.get('image', None)
            
        def dispatch_request(self):
            count_response = self.AW.count_action.execute(self.image, self.threshold)
            return jsonify(count_response)          

    @staticmethod
    def parse_request(request):
        uploaded_file = request.files['file']
        threshold = float(request.form.get('threshold', 0.5))
        image = BytesIO()
        uploaded_file.save(image)
        return {'threshold': threshold,
                'image': image}

    def create_app(self):
        return Flask(__name__)

    def add_rules(self):
        self.app.add_url_rule('/object-count', view_func=self.object_detection.as_view('object-count', self))
        self.app.add_url_rule('/object-found', view_func=self.object_listing.as_view('object-found', self))

    def _return_app(self):
        return self.app

if __name__ == '__main__':
    AppWrapper = AW()  # ApplicationWrapper
    app = AppWrapper._return_app()
    app.run('0.0.0.0', debug=True)
