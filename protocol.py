import pickle
class HEMSProtocol:
    def __init__(self, type, id=None, sn=None, power=None, state=None, time=None, command=None, value=None):
        # 消息头
        self.header = {
            "type": type
        }
        # 消息体
        type = self.header["type"]
        if type == 'data':
            self.body = {
                "id": id,
                "sn": sn,
                "power": power,
                "state": state,
                "time": time
            }
        elif type == 'control':
            self.body = {
                "command": command,
                "value": value
            }

    def serilize(self):
        return pickle.dumps({
            "header": self.header,
            "body": self.body
        })
    
    @staticmethod
    def unserilize(msg):
        return pickle.loads(msg)
