import llm
from llm import Model, hookimpl
import openai
from typing import Optional, List
from pydantic import Field

def get_model_ids_with_aliases():
    return [
        ("meta-llama/Meta-Llama-3.1-70B-Instruct", ["hyper-chat"]),
        ("meta-llama/Meta-Llama-3.1-405B-FP8", ["hyper-base"]),
    ]

class HyperbolicOptions(llm.Options):
    temperature: Optional[float] = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=14)

class HyperbolicModel(Model):
    needs_key = "hyperbolic"
    key_env_var = "HYPERBOLIC_API_KEY"
    can_stream = True

    class Options(HyperbolicOptions):
        pass

    def __init__(self, model_id):
        self.model_id = model_id
        self.api_base = "https://api.hyperbolic.xyz/v1/"

    def execute(self, prompt, stream, response, conversation):
        client = self.get_client()

        kwargs = self.build_kwargs(prompt)
        kwargs["stream"] = stream

        if "Instruct" in self.model_id:
            messages = self.build_messages(prompt, conversation)
            completion = client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                **kwargs
            )
            if stream:
                for chunk in completion:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
            else:
                yield completion.choices[0].message.content
        else:
            completion = client.completions.create(
                model=self.model_id,
                prompt=prompt.prompt,
                **kwargs
            )
            if stream:
                for chunk in completion:
                    text = chunk.choices[0].text
                    if text:
                        yield text
            else:
                yield completion.choices[0].text

        response.response_json = completion.model_dump()

    def get_client(self):
        return openai.OpenAI(
            api_key=self.get_key(),
            base_url=self.api_base
        )

    def build_messages(self, prompt, conversation):
        messages = []
        if prompt.system:
            messages.append({"role": "system", "content": prompt.system})
        if conversation:
            for prev_response in conversation.responses:
                messages.append({"role": "user", "content": prev_response.prompt.prompt})
                messages.append({"role": "assistant", "content": prev_response.text()})
        messages.append({"role": "user", "content": prompt.prompt})
        return messages

    def build_kwargs(self, prompt):
        return {k: v for k, v in prompt.options.dict().items() if v is not None}

@hookimpl
def register_models(register):
    models_with_aliases = get_model_ids_with_aliases()
    for model_id, aliases in models_with_aliases:
        register(HyperbolicModel(model_id), aliases=aliases)

@hookimpl
def register_commands(cli):
    @cli.command()
    def hyperbolic_models():
        "List available Hyperbolic models"
        models_with_aliases = get_model_ids_with_aliases()
        for model_id, aliases in models_with_aliases:
            print(f"Hyperbolic Model: {model_id}")
            if aliases:
                print(f"  Aliases: {', '.join(aliases)}")
            print()
