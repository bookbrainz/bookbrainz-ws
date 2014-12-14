
from bbws import create_app

import os
os.environ['DEBUG'] = 'true'

app = create_app('../config/deploy.py')
app.run(debug=True)
