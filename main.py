import os

import nazgul


if __name__ == "__main__":
    app = nazgul.create_app()
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 8000))
