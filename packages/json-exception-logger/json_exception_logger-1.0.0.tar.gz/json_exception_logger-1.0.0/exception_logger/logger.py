import json
from datetime import datetime, timezone

class ExceptionLogger:
    def __init__(self, log_file='exception_logs.json'):
        self.log_file = log_file

    def log_exception(self, application_name, category, message, stack_trace, exception_details=None, exp_object=None, exp_process=None, inner_exception=None):
        """Log an exception into a JSON file."""
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'application_name': application_name,
            'category': category,
            'message': message,
            'exception_details': exception_details,
            'exp_object': exp_object,
            'exp_process': exp_process,
            'inner_exception': inner_exception,
            'stack_trace': stack_trace
        }

        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            print("Log entry committed to JSON file.")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
