import openai

# Configure your OpenAI API key here
API_KEY = 'your-api-key'


def setup_openai_api():
    openai.api_key = API_KEY


def chat_with_gpt(prompt):
    setup_openai_api()
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error communicating with OpenAI API: {str(e)}")
        return None


def get_detailed_response(prompt):
    response_text = chat_with_gpt(prompt)
    if response_text is not None:
        return {"status": "success", "response": response_text}
    else:
        return {"status": "error", "response": "Failed to get response from OpenAI API"}
