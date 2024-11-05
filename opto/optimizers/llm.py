from typing import List, Tuple, Dict, Any, Callable, Union
import time

class LLM:
    """
    A minimal abstraction of an LLM api that refreshes the model every
    reset_freq seconds (this is useful for long-running models that may require
    refreshing certificates or memory management).
    """
    def __init__(self, factory: Callable, reset_freq: Union[int, None] = None) -> None:
        """
        Args:
            factory: A function that takes no arguments and returns an LLM model.
            reset_freq: The number of seconds after which the model should be
                refreshed. If None, the model is never refreshed.
        """

        self.factory = factory
        self._model = factory()
        self.reset_freq = reset_freq
        self._init_time = time.time()

    @property
    def model(self):
        return self._model

    def __call__(self, *args, **kwargs) -> Any:
        if self.reset_freq is not None and time.time() - self._init_time > self.reset_freq:
            self._model = self.factory()
            self._init_time = time.time()
        return self.model(*args, **kwargs)


class AutoGenLLM(LLM):

    def __init__(self, config_list: List = None, filter_dict: Dict = None, reset_freq: Union[int, None]  = None) -> None:

        import autogen  # We import autogen here to avoid the need of installing autogen

        if config_list is None:
            config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
        if filter_dict is not None:
            config_list = autogen.filter_config_list(config_list, filter_dict)

        def factory():
            return autogen.OpenAIWrapper(config_list=config_list)

        super().__init__(factory, reset_freq)


    @property
    def model(self):
        return lambda *args, **kwargs : self._model.create(*args, **kwargs)
