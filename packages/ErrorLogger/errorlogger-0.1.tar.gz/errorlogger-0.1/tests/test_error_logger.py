from ErrorLogger.logger import ErrorLogger, capture_exception

# Initialize the logger
error_logger = ErrorLogger(log_file='test_error_logs.log')

@capture_exception(error_logger, message="Error occurred in divide function")
def divide(x, y):
    return x / y

def main():
    print("Testing division with valid inputs...")
    print(divide(10, 2))  # This should work fine

    print("Testing division by zero...")
    try:
        divide(10, 0)  # This should raise an exception and be logged
    except ZeroDivisionError:
        print("Caught a ZeroDivisionError")

if __name__ == "__main__":
    main()
