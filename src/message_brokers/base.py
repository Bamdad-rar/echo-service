
# if later we want to add kafka as message broker we must implement these two methods
class MessageBroker:
    def run(self):
        raise NotImplemented
    def register_callback(self, callback):
        raise NotImplemented


