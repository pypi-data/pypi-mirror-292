import logging
import os
import warnings


def disable_logging():

    warnings.filterwarnings("ignore", category=UserWarning)

    # disable tensorflow warnings
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # Set the logging level for the entire module
    logging.basicConfig(level=logging.ERROR)

    try:
        log = logging.getLogger("pytorch")
        log.propagate = False
        log.setLevel(logging.ERROR)
    except Exception as error:
        print(f"Pytorch logging not disabled: {error}")

    for logger_name in [
        "tensorflow",
        "h5py",
        "numexpr",
        "git",
        "wandb.docker.auth",
        "langchain",
        "distutils",
        "urllib3",
        "elasticsearch",
        "packaging",
    ]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)

    # Remove all existing handlers
    logging.getLogger().handlers = []

    # Get the workspace directory from the environment variables
    workspace_dir = os.environ["WORKSPACE_DIR"]

    # Check if the workspace directory exists, if not, create it
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)

    # Create a file handler to log errors to the file
    file_handler = logging.FileHandler(
        os.path.join(workspace_dir, "error.txt")
    )
    file_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(file_handler)

    # Create a stream handler to log errors to the terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(stream_handler)
