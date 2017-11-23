import grpc
import replicator_pb2
# A test run to update the server collections
class RunReplicator():
    #Set the connection
    def __init__(self, host='192.168.0.1', port = 3000):
        self.channel = grpc.insecure_channel('%s : %d' % (host, port))
        self.stub = replicator_pb2.ReplicatorStub(self.channel)
    # Put data 
    def put(self, key, data):
        return self.stub.put(replicator_pb2.Request(key=key, data=data))
    # Remove collection
    def delete(self, key):
        return self.stub.delete(replicator_pb2.Request(key=key))

def main():
    run_replicator = RunReplicator()
    # Update the server by adding
    resp = run_replicator.put('Fruits', 'Apple')
    print('Update: put Fruits : Apple')
    print(resp.data)

    resp = run_replicator.put('Fruits', 'Banana')
    print('Update: put Fruits : Banana')
    print(resp.data)
 
    resp = run_replicator.put('Fruits', 'Orange')
    print('Update: put Fruits : Orange')
    print(resp.data)
    # Delete
    resp = run_replicator.delete('Fruits')
    print('Delete Fruits')
    print(resp.data)
    # Adding again
    resp = run_replicator.put('Animals', 'Tiger')
    print('Put Animals : Tiger')
    print(resp.data)

    resp = run_replicator.put('Animals', 'Elephant')
    print('Put Animals : Elephant')
    print(resp.data)

    resp = run_replicator.put('Animals', 'Bear')
    print('Put Animals : Bear')
    print(resp.data)

if __name__ == "__main__":
    main()

