import json
import sys


class CodeExecutionContext(object):
    def __init__(self, inputs):
        self.input_index = 0
        self.inputs = inputs
        self.outputs = []
        self.error_flag = False

    def __enter__(self):
        self.__stdin = sys.stdin
        self.__stdout = sys.stdout
        sys.stdin = self
        sys.stdout = self

    def __exit__(self, type, value, traceback):
        sys.stdin = self.__stdin
        sys.stdout = self.__stdout

    def write(self, value):
        self.outputs.append(value)

    def readline(self):
        input_value = self.inputs[self.input_index]
        self.outputs.append(input_value)
        self.input_index += 1
        return input_value


def lambda_handler(event, context):
    data = json.loads(event['body'])

    code = data['code']
    stdin = data['stdin']
    fileName = data['fileName']

    inputs = stdin.split('\n')

    executionContext = CodeExecutionContext(inputs)

    with executionContext:
        try:
            code = compile(code, fileName, 'exec')
            exec(code)
        except Exception as e:
            print(e)
            executionContext.error_flag = True

    responseBody = {}
    if executionContext.error_flag:
        responseBody['error'] = True
        responseBody['stderr'] = executionContext.outputs
    else:
        responseBody['error'] = False
        responseBody['stderr'] = []

    responseBody['output'] = executionContext.outputs

    response = {}
    response['body'] = json.dumps(responseBody)
    response['statusCode'] = 200

    return response
