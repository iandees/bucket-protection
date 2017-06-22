import os
from app import create_app

app = create_app(os.environ.get('BUCKET_ENV', 'default'))

if __name__ == '__main__':
    app.run(debug=True)
