import grpc
import bank_pb2
import bank_pb2_grpc
from concurrent import futures


def run(account_id):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bank_pb2_grpc.BankServiceStub(channel)

        try:
            # Create account
            response = stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id))
            # Deposit funds
            response = stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=10000))
            print(f"Account {account_id}: {response.message}, New balance: {response.balance}")
            # Get balance
            response = stub.GetBalance(bank_pb2.AccountRequest(account_id=account_id))
            print(f"Account {account_id}: {response.message}, Balance: {response.balance}")
            # Withdraw funds
            response = stub.Withdraw(bank_pb2.WithdrawRequest(account_id=account_id, amount=20))
            print(f"Account {account_id}: {response.message}, New balance: {response.balance}")
            # Get balance
            response = stub.GetBalance(bank_pb2.AccountRequest(account_id=account_id))
            print(f"Account {account_id}: {response.message}, Balance: {response.balance}")
            # Calculate interest
            response = stub.CalculateInterest(bank_pb2.InterestRequest(account_id=account_id, annual_interest_rate=5))
            print(f"Account {account_id}: {response.message}, New balance: {response.balance}")
            # Get balance
            response = stub.GetBalance(bank_pb2.AccountRequest(account_id=account_id))
            print(f"Account {account_id}: {response.message}, Balance: {response.balance}")

        except grpc.RpcError as e:
            status_code = e.code()
            details = e.details()
            print(f"Error occurred: {status_code}, {details}")

def test_semaphore_parallelism():
    # Account ids to test in parallel
    account_ids = ["1", "2", "1", "2", "1"]
    
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks for each account_id to the executor
        tasks = [executor.submit(run, account_id) for account_id in account_ids]

        for future in tasks:
            future.result()

if __name__ == "__main__":
    test_semaphore_parallelism()
