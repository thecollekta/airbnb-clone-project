# airbnb-clone-project/scripts/test_celery.py
import os
import sys
import time

from celery import Celery

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "airbnb_clone.settings")

# Initialize Django
import django

django.setup()

# Initialize Celery
app = Celery("airbnb_clone")
app.config_from_object("django.conf:settings", namespace="CELERY")


# A simple test task
@app.task(bind=True, name="test_task")
def test_task(self, message):
    print(f"[TASK] Received message: {message}")
    time.sleep(2)  # Simulate work
    return f"Processed: {message}"


def test_celery_setup():
    print("Testing Celery worker...")

    # Test async task
    print("Sending test task...")
    result = test_task.delay("Hello from Celery!")

    # Wait for result with timeout
    try:
        task_result = result.get(timeout=10)
        print(f"Task completed successfully: {task_result}")
        return True
    except Exception as e:
        print(f"Error executing task: {e}")
        return False


if __name__ == "__main__":
    if test_celery_setup():
        print("Celery setup is working correctly!")
        sys.exit(0)
    else:
        print("Celery setup has issues!")
        sys.exit(1)
