import grpc
import rocksdb
import replicator_pb2
import replicator_pb2_grpc
import queue
import time


from concurrent import futures

SECONDS_OF_DAY = 24*60*60

class ReplicatorService(replicator_pb2.ReplicatorServicer):
    def __init__(self):
        self.db = rocksdb.DB("serverStoreDB.db", rocksdb.Options(create_if_missing = True))
        self.operations_queue = queue.Queue()

    def push_client(func):
        def wrapper(self, request, context):
            op = replicator_pb2.SyncOperation(
                    op=func.__name__, 
                    key=request.key.encode(), 
                    data=request.data.encode()
                 ) 
            self.operations_queue.put(op)
            return func(self, request, context)
        return wrapper

    @push_client
    def put(self, request, context):
        print("Put {} : {} to serverStoreDB".format(request.key, request.data))
        self.db.put(request.key.encode(), request.data.encode())
        return replicator_pb2.Response(data = 'ok')

    @push_client
    def delete(self, request, context):
        print("Delete {} from serverStoreDB".format(request.key))
        self.db.delete(request.key.encode())
        return replicator_pb2.Response(data = 'ok')
 
    def sync(self, request, context):
        print("Client is connected")
        while True:
            operation = self.operations_queue.get()
            print("Sending data ({}, {}, {}) to Client".format(operation.op, operation.key, operation.data))
            yield operation
       
    def get(self, request, context):
        print("Get {} from serverStoreDB".format(request.key))
        value = self.db.get(request.key.encode())
        return replicator_pb2.Response(data=value)


def run(host, port):
    #Run the GRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    replicator_pb2_grpc.add_ReplicatorServicer_to_server(ReplicatorService(), server)
    server.add_insecure_port('%s:%d' % (host, port))
    server.start()

    try:
        while True:
            print("Server port: %d" % port)
            time.sleep(SECONDS_OF_DAY)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    run( '0.0.0.0', 3000)


