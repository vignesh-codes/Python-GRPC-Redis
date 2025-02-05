# this is a gpt generated test code

import grpc
import bank_pb2
import bank_pb2_grpc
from concurrent import futures
from redis import Redis

r = Redis(host="localhost", port=6379, decode_responses=True)
def run_scenario(account_id, operations):
    """
    Helper function that connects to the server and runs a list of operations.
    Each operation is a lambda that takes a stub and returns a response.
    """
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = bank_pb2_grpc.BankServiceStub(channel)
        for op in operations:
            try:
                response = op(stub)
                # print("response is ", response)
                print(f"Account {account_id}: {response.message}, Balance: {response.balance}")

            except grpc.RpcError as e:
                print(f"Account {account_id} error: {e.code()}, {e.details()}")

def flush_db():
    """
    Helper function to flush the Redis database.
    """
    r.flushdb()
    print("Redis database flushed")
    return
def test_successful_flow():
    print("=== Test Successful Flow ===")
    account_id = "100"
    operations = [
        lambda stub: stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="savings")),
        lambda stub: stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=10000)),
        lambda stub: stub.Withdraw(bank_pb2.WithdrawRequest(account_id=account_id, amount=20)),
        lambda stub: stub.CalculateInterest(bank_pb2.InterestRequest(account_id=account_id, annual_interest_rate=5)),
        lambda stub: stub.GetBalance(bank_pb2.AccountRequest(account_id=account_id))
    ]
    run_scenario(account_id, operations)
    print()

def test_duplicate_account():
    print("=== Test Duplicate Account Creation ===")
    account_id = "101"
    operations = [
        lambda stub: stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="savings")),
        lambda stub: stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="savings"))
    ]
    run_scenario(account_id, operations)
    print()

def test_negative_deposit():
    print("=== Test Negative Deposit ===")
    account_id = "102"
    operations = [
        lambda stub: stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="checking")),
        lambda stub: stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=-100))
    ]
    run_scenario(account_id, operations)
    print()

def test_insufficient_funds_withdraw():
    print("=== Test Insufficient Funds Withdraw ===")
    account_id = "103"
    operations = [
        lambda stub: stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="savings")),
        lambda stub: stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=50)),
        lambda stub: stub.Withdraw(bank_pb2.WithdrawRequest(account_id=account_id, amount=100000))
    ]
    run_scenario(account_id, operations)
    print()

def test_invalid_interest_rate():
    print("=== Test Invalid Interest Rate ===")
    account_id = "104"
    operations = [
        lambda stub: stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="savings")),
        lambda stub: stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=500)),
        lambda stub: stub.CalculateInterest(bank_pb2.InterestRequest(account_id=account_id, annual_interest_rate=-5))
    ]
    run_scenario(account_id, operations)
    print()

def test_parallel_access():
    print("=== Test Parallel Access ===")
    account_id = "105"
    # Function to run operations on the same account concurrently.
    def run_ops(account_id):
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = bank_pb2_grpc.BankServiceStub(channel)
            try:
                # Try to create the account (only one should succeed)
                stub.CreateAccount(bank_pb2.AccountRequest(account_id=account_id, account_type="savings"))
            except grpc.RpcError:
                pass  # Ignore duplicate account creation errors
            try:
                response = stub.Deposit(bank_pb2.DepositRequest(account_id=account_id, amount=100))
                print(f"Parallel Access - Account {account_id}: {response.message}, Balance: {response.balance}")
            except grpc.RpcError as e:
                print(f"Parallel Access - Account {account_id}: {e.code()}, {e.details()}")

    # Execute parallel operations using a ThreadPoolExecutor.
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        tasks = [executor.submit(run_ops, account_id) for _ in range(3)]
        for task in tasks:
            task.result()
    print()

def main():
    flush_db()
    test_successful_flow()
    test_duplicate_account()
    test_negative_deposit()
    test_insufficient_funds_withdraw()
    test_invalid_interest_rate()
    test_parallel_access()

if __name__ == "__main__":
    main()
