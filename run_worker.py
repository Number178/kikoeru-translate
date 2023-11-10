# fix python relative import bugs
from server.background_task import main as worker_main

if __name__ == "__main__":
    worker_main()
