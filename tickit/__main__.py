import asyncio
import sys

from tickit.cli import main

# test with:
#     pipenv run python -m tickit
if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
