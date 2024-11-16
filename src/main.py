from src.config import Config
from src.driver import init_driver
from src.login import login


def main():
    Config.validate()

    driver = init_driver()

    try:
        login(driver)
    finally:
        print("Finished")


if __name__ == "__main__":
    main()
