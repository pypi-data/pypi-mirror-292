## ⚙️ Installation
Python 3.10 or higher is required
```
pip install noxii
```

## 🚀 Example Usage
The API key can be passed as a parameter or set as the environment variable `API_KEY`.

### Sync Example
```python
from noxii import NoxiiAPI

api = NoxiiAPI(api_key="[YOUR_API_KEY]")

user_stats = api.test()  # Prints "Success!" if it is installed correctly
```