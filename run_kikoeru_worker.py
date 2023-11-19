# fix python relative import bugs
from server.kikoeru_worker import main as worker_main

if __name__ == "__main__":
    worker_main()
