from javonet.core.interpreter.Interpreter import Interpreter


class Receiver:

    def __init__(self):
        self.python_interpreter = Interpreter()

    def SendCommand(self, messageByteArray, messageByteArrayLen):
        return bytearray(self.python_interpreter.process(messageByteArray, len(messageByteArray)))

    def HeartBeat(self, messageByteArray, messageByteArrayLen):
        response_byte_array = bytearray(2)
        response_byte_array[0] = messageByteArray[11]
        response_byte_array[1] = messageByteArray[12] - 2
        return response_byte_array
