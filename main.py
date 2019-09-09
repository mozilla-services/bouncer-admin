import os

import nazgul


if __name__ == "__main__":
    nazgul.create_app()
    nazgul.run(host="0.0.0.0", port=os.environ.get("PORT", 8000))
