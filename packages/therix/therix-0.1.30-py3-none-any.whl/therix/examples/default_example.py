from importlib import metadata
from therix.core.agent import Agent
from therix.core.inference_models import GroqLlama370b
from therix.core.system_prompt_config import SystemPromptConfig
from therix.core.output_parser import OutputParserWrapper

GROQ_API_KEY = ' '

metadata = {
    "name": "Abhishek Dubey",
}

agent = Agent(name="DEFAULT Agent")
(
    agent.add(GroqLlama370b(config={"groq_api_key": GROQ_API_KEY}))
    .add(SystemPromptConfig(config={"system_prompt": "new-prompt"}))
    .save()
)
print(agent.id)


ans = agent.invoke(question="What is the difference between eating an apple and eating a cake?")
print(ans)
