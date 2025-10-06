from api import cohere_API
from ui import lazyCatUI


def main():
    # This function builds UI and starts the main loop
    lazyCatUI.build_ui(cohere_API)

main()