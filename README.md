# Python-GRPC-Redis

Github Repo: [Python-GRPC-Redis](https://github.com/vignesh-codes/Python-GRPC-Redis) 

This project implements a scalable and reliable distributed banking system using gRPC for communication, Python for the application logic, and Redis for account storage. The system provides functionalities such as creating accounts, retrieving balances, depositing funds, withdrawing funds, and calculating interest. Concurrency control is managed through a custom read–write lock implementation to ensure data consistency in a multi-threaded environment.

## Features

- **gRPC Server:**  
  Implements a gRPC service with the following RPC methods:
  - **CreateAccount:** Create a new bank account.
  - **GetBalance:** Retrieve the balance of an account.
  - **Deposit:** Deposit funds into an account.
  - **Withdraw:** Withdraw funds from an account.
  - **CalculateInterest:** Calculate and apply interest to an account balance.

- **Redis Integration:**  
  Uses Redis as a key-value store to manage account information with account ID as the key and account details (account type and balance) as values.

- **Concurrency Control:**  
  Uses a custom read–write lock implementation to allow multiple readers while ensuring that write operations wait until all read operations are finished.
  I created a custom read–write lock to ensure that multiple readers can access the account data concurrently, while write operations are exclusive to prevent data inconsistency.

    ```python
    class ReadWriteLock:
        def __init__(self):
            self.lock = threading.Lock()  # Lock for modifying reader count
            self.readers = 0  # Count of active readers
            self.write_lock = threading.Lock()  # Lock for writers
            self.condition = threading.Condition(self.lock)

        def acquire_read(self):
            with self.lock:
                while self.write_lock.locked():
                    print("waiting for write lock to be released")
                    self.condition.wait()  # Wait if a writer is active
                self.readers += 1  # Increment reader count

        def release_read(self):
            with self.lock:
                self.readers -= 1  # Decrement reader count
                if self.readers == 0:
                    print("releasing all readers ---------- ")
                    self.condition.notify_all()  # Notify waiting writers

        def acquire_write(self):
            self.write_lock.acquire()  # Block other writers
            with self.lock:
                
                while self.readers > 0:  # Wait until all readers are done
                    print('waiting for readers to finish ', self.readers)
                    self.condition.wait()

        def release_write(self):
            with self.lock:
                self.condition.notify_all()  # Notify readers and writers
            self.write_lock.release()  # Release exclusive lock
    ```

  Ideally we would be going with distributed locks on redis to ensure that all readers can access the account data concurrently, while write operations are exclusive to prevent data inconsistency from multiple threads or processes (servers).

- **Error Handling:**  
  Implements robust error handling by returning appropriate gRPC status codes and descriptive error messages for scenarios such as account not found, invalid transaction amounts, and insufficient funds.

## Prerequisites

- **Docker:**  
  Used to run a Redis instance.
- **Python 3:**  
  Ensure Python 3 is installed.
- **Virtualenv:**  
  For creating an isolated Python environment.

## Setup Instructions

### 1. Run Redis

Start a Redis instance using Docker:

```bash
docker run -d --name redis-stack-server -p 6379:6379 redis/redis-stack-server:latest
```

### 2. Install Dependencies
Create a virtual environment and install the required packages:

```bash
virtualenv -p python3 env
source env/Scripts/activate
pip install grpcio grpcio-tools redis
```

### 3. Run gRPC Server

Run the gRPC server:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. bank.proto
python server.py
```      

### 4. Run gRPC Client

Run the gRPC client:

```bash
python client.py
```

Run the gRPC client unit tests:

```bash
python client_tests.py
```

### 5. Project Structure

```graphql
├── server.py               # Main gRPC server implementation
├── client.py               # Client implementation to interact with the gRPC server
├── client_tests.py         # Unit tests for the client - gpt generated
├── bank.proto              # Protocol Buffers definition file
├── bank_pb2.py             # Generated gRPC code (do not modify)
├── bank_pb2_grpc.py        # Generated gRPC service code (do not modify)
└── README.md               # This file
```

### 6. Testing Output

```bash
> python .\client_tests.py
Redis database flushed
=== Test Successful Flow ===
Account 100: Account created successfully., Balance: 0.0
Account 100: Deposit successful., Balance: 10000.0
Account 100: Withdrawal successful., Balance: 9980.0
Account 100: Interest added., Balance: 10479.0
Account 100: Balance retrieved., Balance: 10479.0

=== Test Duplicate Account Creation ===
Account 101: Account created successfully., Balance: 0.0
Account 101 error: StatusCode.ALREADY_EXISTS, Account already exists.

=== Test Negative Deposit ===
Account 102: Account created successfully., Balance: 0.0
Account 102 error: StatusCode.INVALID_ARGUMENT, Transaction amount must be positive.

=== Test Insufficient Funds Withdraw ===
Account 103: Account created successfully., Balance: 0.0
Account 103: Deposit successful., Balance: 50.0
Account 103 error: StatusCode.FAILED_PRECONDITION, Insufficient funds for the requested withdrawal.

=== Test Invalid Interest Rate ===
Account 104: Account created successfully., Balance: 0.0
Account 104: Deposit successful., Balance: 500.0
Account 104 error: StatusCode.INVALID_ARGUMENT, Annual interest rate must be a positive value.

=== Test Parallel Access ===
Parallel Access - Account 105: Deposit successful., Balance: 100.0
Parallel Access - Account 105: Deposit successful., Balance: 200.0
Parallel Access - Account 105: Deposit successful., Balance: 300.0
```

### 7. Acknowledgments
This project was built as part of the CS 4459/9644 assignment to understand scalable and reliable distributed systems using gRPC, Python, and Redis.
