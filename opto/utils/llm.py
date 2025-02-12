from typing import List, Tuple, Dict, Any, Callable, Union
import os
import time
import json
import autogen  # We import autogen here to avoid the need of installing autogen
import litellm
import os


class AbstractModel:
    """
    A minimal abstraction of a model api that refreshes the model every
    reset_freq seconds (this is useful for long-running models that may require
    refreshing certificates or memory management).
    """

    def __init__(self, factory: Callable, reset_freq: Union[int, None] = None) -> None:
        """
        Args:
            factory: A function that takes no arguments and returns a model that is callable.
            reset_freq: The number of seconds after which the model should be
                refreshed. If None, the model is never refreshed.
        """
        self.factory = factory
        self._model = self.factory()
        self.reset_freq = reset_freq
        self._init_time = time.time()

    # Overwrite this `model` property when subclassing.
    @property
    def model(self):
        """ When self.model is called, text responses should always be available at ['choices'][0].['message']['content'] """
        return self._model

    # This is the main API
    def __call__(self, *args, **kwargs) -> Any:
        """ The call function handles refreshing the model if needed. """
        if self.reset_freq is not None and time.time() - self._init_time > self.reset_freq:
            self._model = self.factory()
            self._init_time = time.time()
        return self.model(*args, **kwargs)

    def __getstate__(self):
        state = self.__dict__.copy()
        state["_model"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._model = self.factory()


class AutoGenLLM(AbstractModel):
    """ This is the main class Trace uses to interact with the model. It is a wrapper around autogen's OpenAIWrapper. For using models not supported by autogen, subclass AutoGenLLM and override the `_factory` and  `create` method. Users can pass instances of this class to optimizers' llm argument. """

    def __init__(self, config_list: List = None, filter_dict: Dict = None, reset_freq: Union[int, None]  = None) -> None:
        if config_list is None:
            try:
                config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
            except:
                config_list = auto_construct_oai_config_list_from_env()
                if len(config_list) > 0:
                    os.environ.update({"OAI_CONFIG_LIST": json.dumps(config_list)})
                config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        if filter_dict is not None:
            config_list = autogen.filter_config_list(config_list, filter_dict)

        factory = lambda *args, **kwargs: self._factory(config_list)
        super().__init__(factory, reset_freq)

    @classmethod
    def _factory(cls, config_list):
        return autogen.OpenAIWrapper(config_list=config_list)

    @property
    def model(self):
        return lambda *args, **kwargs: self.create(*args, **kwargs)

    # This is main API. We use the API of autogen's OpenAIWrapper
    def create(self, **config: Any) -> autogen.ModelClient.ModelClientResponseProtocol:
        """Make a completion for a given config using available clients.
        Besides the kwargs allowed in openai's [or other] client, we allow the following additional kwargs.
        The config in each client will be overridden by the config.

        Args:
            - context (Dict | None): The context to instantiate the prompt or messages. Default to None.
                It needs to contain keys that are used by the prompt template or the filter function.
                E.g., `prompt="Complete the following sentence: {prefix}, context={"prefix": "Today I feel"}`.
                The actual prompt will be:
                "Complete the following sentence: Today I feel".
                More examples can be found at [templating](/docs/Use-Cases/enhanced_inference#templating).
            - cache (AbstractCache | None): A Cache object to use for response cache. Default to None.
                Note that the cache argument overrides the legacy cache_seed argument: if this argument is provided,
                then the cache_seed argument is ignored. If this argument is not provided or None,
                then the cache_seed argument is used.
            - agent (AbstractAgent | None): The object responsible for creating a completion if an agent.
            - (Legacy) cache_seed (int | None) for using the DiskCache. Default to 41.
                An integer cache_seed is useful when implementing "controlled randomness" for the completion.
                None for no caching.
                Note: this is a legacy argument. It is only used when the cache argument is not provided.
            - filter_func (Callable | None): A function that takes in the context and the response
                and returns a boolean to indicate whether the response is valid. E.g.,
            - allow_format_str_template (bool | None): Whether to allow format string template in the config. Default to false.
            - api_version (str | None): The api version. Default to None. E.g., "2024-02-01".

        Example:
            >>> # filter_func example:
            >>> def yes_or_no_filter(context, response):
            >>>    return context.get("yes_or_no_choice", False) is False or any(
            >>>        text in ["Yes.", "No."] for text in client.extract_text_or_completion_object(response)
            >>>    )

        Raises:
            - RuntimeError: If all declared custom model clients are not registered
            - APIError: If any model client create call raises an APIError
        """
        return self._model.create(**config)


def auto_construct_oai_config_list_from_env() -> List:
    """
    Collect various API keys saved in the environment and return a format like:
    [{"model": "gpt-4", "api_key": xxx}, {"model": "claude-3.5-sonnet", "api_key": xxx}]

    Note this is a lazy function that defaults to gpt-40 and claude-3.5-sonnet.
    If you want to specify your own model, please provide an OAI_CONFIG_LIST in the environment or as a file
    """
    config_list = []
    if os.environ.get("OPENAI_API_KEY") is not None:
        config_list.append(
            {"model": "gpt-4o", "api_key": os.environ.get("OPENAI_API_KEY")}
        )
    if os.environ.get("ANTHROPIC_API_KEY") is not None:
        config_list.append(
            {
                "model": "claude-3-5-sonnet-latest",
                "api_key": os.environ.get("ANTHROPIC_API_KEY"),
            }
        )
    return config_list


class LiteLLM(AbstractModel):
    """
    This is an LLM backend supported by LiteLLM library.

    https://docs.litellm.ai/docs/completion/input

    To use this, set the credentials through the environment variable as
    instructed in the LiteLLM documentation. For convenience, you can set the
    default model name through the environment variable DEFAULT_LITELLM_MODEL.
    When using Azure models via token provider, you can set the Azure token
    provider scope through the environment variable AZURE_TOKEN_PROVIDER_SCOPE.
    """

    def __init__(self, model: Union[str, None] = None, reset_freq: Union[int, None] = None,
                 cache=True) -> None:
        if model is None:
            model = os.environ.get('DEFAULT_LITELLM_MODEL', 'gpt-4o')
        self.model_name = model
        self.cache = cache
        factory = lambda : self._factory(self.model_name)  # an LLM instance uses a fixed model
        super().__init__(factory, reset_freq)

    @classmethod
    def _factory(cls, model_name : str):
        if model_name.startswith('azure/'):  # azure model
            azure_token_provider_scope = os.environ.get('AZURE_TOKEN_PROVIDER_SCOPE', None)
            if azure_token_provider_scope is not None:
                from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                credential = get_bearer_token_provider(DefaultAzureCredential(), azure_token_provider_scope)
                return lambda *args, **kwargs: litellm.completion(model_name, *args,
                                            azure_ad_token_provider=credential, **kwargs)
        return lambda *args, **kwargs: litellm.completion(model_name, *args, **kwargs)

    @property
    def model(self):
        """
        response = litellm.completion(
            model=self.model,
            messages=[{"content": message, "role": "user"}]
        )
        """
        return lambda *args, **kwargs: self._model(*args, **kwargs)
