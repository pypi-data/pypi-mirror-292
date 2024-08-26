from openai import OpenAI

class Nika:
    def __init__(self, api_key: str, model: str = "gpt-4-o"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key = api_key)

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"An error occurred: {str(e)}"



