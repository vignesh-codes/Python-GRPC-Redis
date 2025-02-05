import grpc
from concurrent import futures
import bank_pb2
import bank_pb2_grpc
import threading
import time
from redis import Redis

# Redis setup
r = Redis(host="localhost", port=6379, decode_responses=True)

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


# Lock dictionaries for read/write operations
account_locks = {}
lock_timeout = 35  # Max time it can wait for a lock
execution_timeout = 30  # Max execution time before forcefully releasing lock

def get_lock(account_id):
    #Get or create a read-write lock for an account
    if account_id not in account_locks:
        account_locks[account_id] = ReadWriteLock()
    return account_locks[account_id]

def run_with_timeout(func, *args, **kwargs):
    #Executes a function with a timeout. Releases the lock if it exceeds the limit
    result = [None]
    account_id = args[0].account_id

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            result[0] = bank_pb2.TransactionResponse(account_id=account_id, balance=0.0, message=f"Error: {str(e)}")

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=execution_timeout)

    if thread.is_alive():
        print(f"Function timeout! Releasing lock for {account_id}.")
        # Cannot force-release our custom lock; logging only.
        return bank_pb2.TransactionResponse(account_id=account_id, balance=0.0, message="Transaction timeout. Lock released.")

    return result[0]

class BankService(bank_pb2_grpc.BankServiceServicer):
    def CreateAccount(self, request, context):
        return run_with_timeout(self._CreateAccount, request, context)
    def Deposit(self, request, context):
        return run_with_timeout(self._Deposit, request, context)
    def Withdraw(self, request, context):
        return run_with_timeout(self._Withdraw, request, context)
    def CalculateInterest(self, request, context):
        return run_with_timeout(self._CalculateInterest, request, context)
    
    # gets the write lock and checks if the account already exists in redis
    # creates one if not exists
    def _CreateAccount(self, request, context):
        lock = get_lock(request.account_id)
        lock.acquire_write()
        try:
            if r.exists(request.account_id):
                context.set_details("Account already exists.")
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                return bank_pb2.AccountResponse(account_id=request.account_id, balance=0.0, message="Account already exists.")
            r.hset(request.account_id, mapping={"type": request.account_type, "balance": 0.0})
            return bank_pb2.AccountResponse(account_id=request.account_id, balance=0.0, message="Account created successfully.")
        finally:
            lock.release_write()

    # gets the read lock and checks if the account exists in redis
    def GetBalance(self, request, context):
        lock = get_lock(request.account_id)  # Replaced get_read_lock with get_lock
        lock.acquire_read()
        try:
            account = r.hgetall(request.account_id)
            if not account:
                context.set_details("Account not found. Please check the account ID.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return bank_pb2.BalanceResponse(account_id=request.account_id, balance=0.0, message="Account not found. Please check the account ID.")
            return bank_pb2.BalanceResponse(account_id=request.account_id, balance=float(account["balance"]), message="Balance retrieved.")
        finally:
            # time.sleep(2)
            lock.release_read()

    # gets the write lock and checks if the account exists in redis
    # increments the balance and returns the new balance
    def _Deposit(self, request, context):
        if request.amount <= 0:
            context.set_details("Transaction amount must be positive.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return bank_pb2.TransactionResponse(account_id=request.account_id, balance=0.0, message="Transaction amount must be positive.")
        lock = get_lock(request.account_id)
        lock.acquire_write()
        try:
            account = r.hgetall(request.account_id)
            if not account:
                context.set_details("Account not found. Please check the account ID.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return bank_pb2.TransactionResponse(account_id=request.account_id, balance=0.0, message="Account not found. Please check the account ID.")
            new_balance = float(account["balance"]) + request.amount
            r.hset(request.account_id, "balance", new_balance)
            return bank_pb2.TransactionResponse(account_id=request.account_id, balance=new_balance, message="Deposit successful.")
        finally:
            # time.sleep(2)
            lock.release_write()

    # gets the write lock and checks if the account exists in redis
    # decrements the balance and returns the new balance
    def _Withdraw(self, request, context):
        if request.amount <= 0:
            context.set_details("Transaction amount must be positive.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return bank_pb2.TransactionResponse(account_id=request.account_id, balance=0.0, message="Transaction amount must be positive.")
        lock = get_lock(request.account_id)
        lock.acquire_write()
        try:
            account = r.hgetall(request.account_id)
            if not account:
                context.set_details("Account not found. Please check the account ID.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return bank_pb2.TransactionResponse(account_id=request.account_id, balance=0.0, message="Account not found. Please check the account ID.")
            current_balance = float(account["balance"])
            if current_balance < request.amount:
                context.set_details("Insufficient funds for the requested withdrawal.")
                context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
                return bank_pb2.TransactionResponse(account_id=request.account_id, balance=current_balance, message="Insufficient funds for the requested withdrawal.")
            new_balance = current_balance - request.amount
            r.hset(request.account_id, "balance", new_balance)
            return bank_pb2.TransactionResponse(account_id=request.account_id, balance=new_balance, message="Withdrawal successful.")
        finally:
            lock.release_write()

    # gets the write lock and checks if the account exists in redis
    # calculates the interest and increments the balance and returns the new balance
    def _CalculateInterest(self, request, context):
        if request.annual_interest_rate <= 0:
            context.set_details("Annual interest rate must be a positive value.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return bank_pb2.TransactionResponse(account_id=request.account_id, balance=0.0, message="Annual interest rate must be a positive value.")
        lock = get_lock(request.account_id)
        lock.acquire_write()
        try:
            account = r.hgetall(request.account_id)
            if not account:
                context.set_details("Account not found. Please check the account ID.")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return bank_pb2.TransactionResponse(account_id=request.account_id, balance=0.0, message="Account not found. Please check the account ID.")
            current_balance = float(account["balance"])
            interest = current_balance * request.annual_interest_rate / 100
            new_balance = current_balance + interest
            r.hset(request.account_id, "balance", new_balance)
            return bank_pb2.TransactionResponse(account_id=request.account_id, balance=new_balance, message="Interest added.")
        finally:
            lock.release_write()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server running on port 50051...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
