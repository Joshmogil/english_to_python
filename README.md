Side project building a plain english interpreter using LLMs.

To use:

1. Get an api key from https://platform.openai.com/api-keys
2. Create a file called .env, add the api key: OPENAI_API_KEY=sk-G3 ...
3. Run python3 ./engterpreter.py

The agent will build out an application model, which will get converted to python.

You can watch it work by viewing application_model.json as you respond to prompts.
When the you and the agent are satisfied with the application model, it will translate the intermediary application model to python and output it in the file .py

This project is strictly for demonstration purposes, and will not be updated in any meaningful ways in the future.