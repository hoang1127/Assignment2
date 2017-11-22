import time
import rocksdb
import grpc
import queue

import replicator_pb2
import replicator_pb2_grpc

from concurrent import futures

SECONDS_OF_DAY = 24*60*60

class ReplicatorService(replicator_pb2.ReplicatorServicer):
    def __init__(self): 
        self.db = rocksdb.DB("serverStore.db", rocksdb.Options(create_if_missing = True))
        self.operations_queue = queue.Queue()

    def push_to_client(func):
        def wrapper(self, request, context):
            operate = replicator_pb2.SyncOperation( operate = func.__name, key= request.key.encode(),
                        data = request.data.encode())

            self.operations_queue.put(operate)

            return func(self, request, context)
        return wrapper

    @push_to_client 
    def put(self, request, context):
        print("Put {}:{} to server store".format(request.key, request.data))

        self.db.put(request.key.encode(), request.data.encode())
        return replicator_pb2.Response(data = 'ok')

    @push_to_client
   
    def get(self, request, context):
        print("Get {} from Server Store".format(request.key))
        value = self.db.get(request.key.encode())

        return replicator_pb2.Response(data = value)

    def sync (self, request, context):
        print(" Client-Server is connected")
        while True :
            ope = self.operations_queue.get()
            print("Sending ({}, {}, {}) to Client".format(ope.op, ope.key, ope.data))
            yield ope
    
    def delete(self, request , context):
        print("Delete {} from Server Store".format(request.key))
        self.db.delete(request.key.encode())

        return replicator_pb2.Response(data = 'ok')


def run(host, port):
    #Run the GRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 2))
    replicator_pb2_grpc.add_ReplicatorServicer_to_server(ReplicatorService(), server)
    server.add_insecure_port('%s:%d' %(host, port))
    server.start()

    try:
        while True:
            print("Server started: %d" %port)
            time.sleep(SECONDS_OF_DAY)

    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    run('0.0.0.0' , 3000)
