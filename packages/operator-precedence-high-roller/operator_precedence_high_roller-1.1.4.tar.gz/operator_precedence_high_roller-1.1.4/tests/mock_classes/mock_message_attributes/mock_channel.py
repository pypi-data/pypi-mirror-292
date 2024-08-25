class MockChannel:
    def __init__(self, name: str):
        self.name = name
    
    async def send(self, content: str):
        print(content)