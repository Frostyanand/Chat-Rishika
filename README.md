# Chat-Rishika
# Chat Rishika - A Caring AI Chatbot

## Description

Chat Rishika is an AI-powered chatbot designed to simulate a deeply caring, affectionate, and warm friend. Rishika listens intently, responds with empathy, and makes the user feel truly heard. The chatbot is capable of remembering key user details to create a personalized, continuous, and meaningful conversation experience. It uses OpenAI's GPT-3.5-turbo model and stores user memories locally in a JSON format.

## Features

- **Personalized Conversations**: Rishika can remember key facts about the user, such as their name, preferences, and interests, allowing it to respond in a more personalized and human-like manner.
  
- **Short-term Memory**: Rishika retains a history of up to 50 most recent interactions, helping it maintain context within a conversation.
  
- **Long-term Memory**: It can identify important user details such as life events, preferences, or interests, and store them for future reference in JSON format. This helps build a deeper relationship over time.

- **Empathy & Care**: Rishika's responses are designed to be warm, understanding, and empathetic, providing a comforting experience to the user.

- **User-Specific Memory**: Each user has their own memory file that stores their conversation history and key facts, which ensures that every interaction is unique and personalized.

- **Error Handling**: The chatbot has error handling in place to handle issues with the OpenAI API and gracefully inform users if something goes wrong.

## Requirements

- Python 3.12 (or any recent version)
- `openai` Python package
- A valid OpenAI API key (can be set in your environment variables)
  
To install the required packages, run:

```bash
pip install openai
```

## Setup

1. **API Key**: Make sure you have an OpenAI API key. You can get one by signing up on [OpenAI's website](https://platform.openai.com/).

2. **Set up Environment Variables**: For security reasons, it's best to store your API key as an environment variable instead of hardcoding it into the code.

   - On Windows, run this command in your command prompt:
     ```bash
     set OPENAI_API_KEY="your_api_key_here"
     ```
   - On macOS/Linux, use this command in the terminal:
     ```bash
     export OPENAI_API_KEY="your_api_key_here"
     ```

3. **Run the Code**: After setting up your environment variables, simply run the Python script.

```bash
python chatbot.py
```

## How It Works

1. **Initialization**: When you run the program, Rishika will ask for your name. This name is used as a key to store and load your personal memory.

2. **User Interaction**: After setting the name, you can start chatting with Rishika. It will remember important details from your conversations and personalize its responses.

3. **Memory Handling**:
   - **Short-Term Memory**: The chatbot keeps the last 50 messages from the user for context.
   - **Long-Term Memory**: Rishika extracts key details (like preferences, interests, life events, etc.) from your messages and stores them for future interactions.

4. **API Call**: For every message, the chatbot communicates with OpenAI’s GPT-3.5 API to generate an empathetic response. If an error occurs with the API, the chatbot will notify you with an error message.

5. **Exit**: Type `exit` or `quit` at any time to end the conversation.

## Memory Storage

Rishika stores the conversation history and key facts in a local directory called `chat_memories`. Each user’s memory is saved in a separate file named `{user_id}.json`. The JSON file is organized as:

```json
{
    "short_term": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ],
    "long_term": {
        "name": "Anu",
        "preferences": ["reading", "traveling"]
    }
}
```

## Error Handling

- **Quota Exceeded**: If you exceed your OpenAI API quota, the chatbot will inform you and suggest trying again later.
- **API Errors**: If there's any issue with the OpenAI API, the chatbot will display an error message.

## Contribution

Feel free to fork the repository and submit pull requests for improvements or bug fixes. Contributions are always welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project uses [OpenAI's GPT-3.5 API](https://openai.com) to generate human-like responses.
- Special thanks to OpenAI for providing such powerful models and making AI accessible for everyone.

All rights reserved.

Permission is not granted to copy, modify, distribute, or use this software or any part of it without explicit written permission from the copyright holder.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
