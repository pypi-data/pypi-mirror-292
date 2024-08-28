class NoxiiAPI:
    def __init__(self, api_key):
        if not api_key:
            print("No API Key found! Try NoxiiAPI(api_key=YOUR_API_KEY_HERE)")
        self.api_key = api_key

    def test(self):
        print("Success!")
