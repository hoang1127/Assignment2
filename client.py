import grpc
import rocksdb
import replicator_pb2
# main class for client handle
class ReplicatorClient():
    #Set condition with constain host='192.168.0.1', port = 3000
    def __init__(self, host='192.168.0.1', port = 3000):
        self.db = rocksdb.DB("clientStoreDB.db", rocksdb.Options(create_if_missing = True))
        self.channel = grpc.insecure_channel('%s : %d' % (host, port))
        self.stub = replicator_pb2.ReplicatorStub(self.channel)

    def sync(self):
        synchronizer = self.stub.sync(replicator_pb2.SyncRequest())
        print("Connected to Server")
        for op in synchronizer:
            if op.op == 'put':
                print("Put {}:{} to clientStoreDB".format(op.key, op.data))
                self.db.put(op.key.encode(), op.data.encode())
            elif op.op == 'delete':
                print("Delete {} from clientStoreDB".format(op.key))
                self.db.delete(op.key.encode())
            else:
                pass
# Start the app
def main():
    client = ReplicatorClient()
    resp = client.sync()

if __name__ == "__main__":
    main()
