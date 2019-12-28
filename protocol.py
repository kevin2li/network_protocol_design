import pickle


class HEMSProtocol:
    def __init__(self, type, id=None, sn=None, power=None, state=None, time=None, control_msg=None):
        # 消息头
        self.header = {
            "type": type
        }
        # 消息体
        if self.header['type'] == 'data':
            self.body = {
                "id": id,
                "sn": sn,
                "power": power,
                "state": state,
                "time": time
            }
        elif self.header['type'] == 'control':
            self.body = {
                "control_msg": control_msg
            }

    def serilize(self):
        return pickle.dumps({
            "header": self.header,
            "body": self.body
        })
    
    @staticmethod
    def unserilize(msg):
        return pickle.loads(msg)
