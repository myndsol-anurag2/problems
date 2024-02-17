from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            if request.json.get('number'):
                number = request.json.get('number')
                res = {}
                if type(number) == int:
                    res['result'] = number * number
                    return res
                else:
                    return Response('{"message":"please enter integer value"}', status=400, mimetype='application/json')
            else:
                return Response('{"message":"please enter number field along with integer value in json format"}', status=400, mimetype='application/json')
        else:
            return Response('{"message":"please enter data in json format"}', status=400, mimetype='application/json')
    else:
        return Response('{"message":"method not allowed"}', status=405, mimetype='application/json')
            
    
 
 
if __name__ == '__main__':
    app.run()   