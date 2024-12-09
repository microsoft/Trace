:py:mod:`opto.optimizers.textgrad`
==================================

.. py:module:: opto.optimizers.textgrad

.. autodoc2-docstring:: opto.optimizers.textgrad
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`GradientInfo <opto.optimizers.textgrad.GradientInfo>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.GradientInfo
          :summary:
   * - :py:obj:`TextGrad <opto.optimizers.textgrad.TextGrad>`
     -

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`construct_tgd_prompt <opto.optimizers.textgrad.construct_tgd_prompt>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.construct_tgd_prompt
          :summary:
   * - :py:obj:`construct_reduce_prompt <opto.optimizers.textgrad.construct_reduce_prompt>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.construct_reduce_prompt
          :summary:
   * - :py:obj:`rm_node_attrs <opto.optimizers.textgrad.rm_node_attrs>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.rm_node_attrs
          :summary:
   * - :py:obj:`get_short_value <opto.optimizers.textgrad.get_short_value>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.get_short_value
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`GLOSSARY_TEXT <opto.optimizers.textgrad.GLOSSARY_TEXT>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.GLOSSARY_TEXT
          :summary:
   * - :py:obj:`OPTIMIZER_SYSTEM_PROMPT <opto.optimizers.textgrad.OPTIMIZER_SYSTEM_PROMPT>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.OPTIMIZER_SYSTEM_PROMPT
          :summary:
   * - :py:obj:`TGD_PROMPT_PREFIX <opto.optimizers.textgrad.TGD_PROMPT_PREFIX>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_PROMPT_PREFIX
          :summary:
   * - :py:obj:`TGD_MULTIPART_PROMPT_INIT <opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_INIT>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_INIT
          :summary:
   * - :py:obj:`TGD_MULTIPART_PROMPT_PREFIX <opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_PREFIX>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_PREFIX
          :summary:
   * - :py:obj:`TGD_PROMPT_SUFFIX <opto.optimizers.textgrad.TGD_PROMPT_SUFFIX>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_PROMPT_SUFFIX
          :summary:
   * - :py:obj:`MOMENTUM_PROMPT_ADDITION <opto.optimizers.textgrad.MOMENTUM_PROMPT_ADDITION>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.MOMENTUM_PROMPT_ADDITION
          :summary:
   * - :py:obj:`CONSTRAINT_PROMPT_ADDITION <opto.optimizers.textgrad.CONSTRAINT_PROMPT_ADDITION>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.CONSTRAINT_PROMPT_ADDITION
          :summary:
   * - :py:obj:`IN_CONTEXT_EXAMPLE_PROMPT_ADDITION <opto.optimizers.textgrad.IN_CONTEXT_EXAMPLE_PROMPT_ADDITION>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.IN_CONTEXT_EXAMPLE_PROMPT_ADDITION
          :summary:
   * - :py:obj:`GRADIENT_TEMPLATE <opto.optimizers.textgrad.GRADIENT_TEMPLATE>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.GRADIENT_TEMPLATE
          :summary:
   * - :py:obj:`GRADIENT_MULTIPART_TEMPLATE <opto.optimizers.textgrad.GRADIENT_MULTIPART_TEMPLATE>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.GRADIENT_MULTIPART_TEMPLATE
          :summary:
   * - :py:obj:`GLOSSARY_TEXT_BACKWARD <opto.optimizers.textgrad.GLOSSARY_TEXT_BACKWARD>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.GLOSSARY_TEXT_BACKWARD
          :summary:
   * - :py:obj:`BACKWARD_SYSTEM_PROMPT <opto.optimizers.textgrad.BACKWARD_SYSTEM_PROMPT>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.BACKWARD_SYSTEM_PROMPT
          :summary:
   * - :py:obj:`CONVERSATION_TEMPLATE <opto.optimizers.textgrad.CONVERSATION_TEMPLATE>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.CONVERSATION_TEMPLATE
          :summary:
   * - :py:obj:`CONVERSATION_START_INSTRUCTION_CHAIN <opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_CHAIN>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_CHAIN
          :summary:
   * - :py:obj:`OBJECTIVE_INSTRUCTION_CHAIN <opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_CHAIN>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_CHAIN
          :summary:
   * - :py:obj:`CONVERSATION_START_INSTRUCTION_BASE <opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_BASE>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_BASE
          :summary:
   * - :py:obj:`OBJECTIVE_INSTRUCTION_BASE <opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_BASE>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_BASE
          :summary:
   * - :py:obj:`EVALUATE_VARIABLE_INSTRUCTION <opto.optimizers.textgrad.EVALUATE_VARIABLE_INSTRUCTION>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.EVALUATE_VARIABLE_INSTRUCTION
          :summary:
   * - :py:obj:`SEARCH_QUERY_BACKWARD_INSTRUCTION <opto.optimizers.textgrad.SEARCH_QUERY_BACKWARD_INSTRUCTION>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.SEARCH_QUERY_BACKWARD_INSTRUCTION
          :summary:
   * - :py:obj:`GRADIENT_OF_RESULTS_INSTRUCTION <opto.optimizers.textgrad.GRADIENT_OF_RESULTS_INSTRUCTION>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.GRADIENT_OF_RESULTS_INSTRUCTION
          :summary:
   * - :py:obj:`REDUCE_MEAN_SYSTEM_PROMPT <opto.optimizers.textgrad.REDUCE_MEAN_SYSTEM_PROMPT>`
     - .. autodoc2-docstring:: opto.optimizers.textgrad.REDUCE_MEAN_SYSTEM_PROMPT
          :summary:

API
~~~

.. py:data:: GLOSSARY_TEXT
   :canonical: opto.optimizers.textgrad.GLOSSARY_TEXT
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.GLOSSARY_TEXT

.. py:data:: OPTIMIZER_SYSTEM_PROMPT
   :canonical: opto.optimizers.textgrad.OPTIMIZER_SYSTEM_PROMPT
   :value: None

   .. autodoc2-docstring:: opto.optimizers.textgrad.OPTIMIZER_SYSTEM_PROMPT

.. py:data:: TGD_PROMPT_PREFIX
   :canonical: opto.optimizers.textgrad.TGD_PROMPT_PREFIX
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_PROMPT_PREFIX

.. py:data:: TGD_MULTIPART_PROMPT_INIT
   :canonical: opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_INIT
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_INIT

.. py:data:: TGD_MULTIPART_PROMPT_PREFIX
   :canonical: opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_PREFIX
   :value: 'Improve the variable ({variable_desc}) using the feedback provided in <FEEDBACK> tags.\n'

   .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_MULTIPART_PROMPT_PREFIX

.. py:data:: TGD_PROMPT_SUFFIX
   :canonical: opto.optimizers.textgrad.TGD_PROMPT_SUFFIX
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.TGD_PROMPT_SUFFIX

.. py:data:: MOMENTUM_PROMPT_ADDITION
   :canonical: opto.optimizers.textgrad.MOMENTUM_PROMPT_ADDITION
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.MOMENTUM_PROMPT_ADDITION

.. py:data:: CONSTRAINT_PROMPT_ADDITION
   :canonical: opto.optimizers.textgrad.CONSTRAINT_PROMPT_ADDITION
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.CONSTRAINT_PROMPT_ADDITION

.. py:data:: IN_CONTEXT_EXAMPLE_PROMPT_ADDITION
   :canonical: opto.optimizers.textgrad.IN_CONTEXT_EXAMPLE_PROMPT_ADDITION
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.IN_CONTEXT_EXAMPLE_PROMPT_ADDITION

.. py:function:: construct_tgd_prompt(do_momentum: bool = False, do_constrained: bool = False, do_in_context_examples: bool = False, **optimizer_kwargs)
   :canonical: opto.optimizers.textgrad.construct_tgd_prompt

   .. autodoc2-docstring:: opto.optimizers.textgrad.construct_tgd_prompt

.. py:data:: GRADIENT_TEMPLATE
   :canonical: opto.optimizers.textgrad.GRADIENT_TEMPLATE
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.GRADIENT_TEMPLATE

.. py:data:: GRADIENT_MULTIPART_TEMPLATE
   :canonical: opto.optimizers.textgrad.GRADIENT_MULTIPART_TEMPLATE
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.GRADIENT_MULTIPART_TEMPLATE

.. py:data:: GLOSSARY_TEXT_BACKWARD
   :canonical: opto.optimizers.textgrad.GLOSSARY_TEXT_BACKWARD
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.GLOSSARY_TEXT_BACKWARD

.. py:data:: BACKWARD_SYSTEM_PROMPT
   :canonical: opto.optimizers.textgrad.BACKWARD_SYSTEM_PROMPT
   :value: None

   .. autodoc2-docstring:: opto.optimizers.textgrad.BACKWARD_SYSTEM_PROMPT

.. py:data:: CONVERSATION_TEMPLATE
   :canonical: opto.optimizers.textgrad.CONVERSATION_TEMPLATE
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.CONVERSATION_TEMPLATE

.. py:data:: CONVERSATION_START_INSTRUCTION_CHAIN
   :canonical: opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_CHAIN
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_CHAIN

.. py:data:: OBJECTIVE_INSTRUCTION_CHAIN
   :canonical: opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_CHAIN
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_CHAIN

.. py:data:: CONVERSATION_START_INSTRUCTION_BASE
   :canonical: opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_BASE
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.CONVERSATION_START_INSTRUCTION_BASE

.. py:data:: OBJECTIVE_INSTRUCTION_BASE
   :canonical: opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_BASE
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.OBJECTIVE_INSTRUCTION_BASE

.. py:data:: EVALUATE_VARIABLE_INSTRUCTION
   :canonical: opto.optimizers.textgrad.EVALUATE_VARIABLE_INSTRUCTION
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.EVALUATE_VARIABLE_INSTRUCTION

.. py:data:: SEARCH_QUERY_BACKWARD_INSTRUCTION
   :canonical: opto.optimizers.textgrad.SEARCH_QUERY_BACKWARD_INSTRUCTION
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.SEARCH_QUERY_BACKWARD_INSTRUCTION

.. py:data:: GRADIENT_OF_RESULTS_INSTRUCTION
   :canonical: opto.optimizers.textgrad.GRADIENT_OF_RESULTS_INSTRUCTION
   :value: <Multiline-String>

   .. autodoc2-docstring:: opto.optimizers.textgrad.GRADIENT_OF_RESULTS_INSTRUCTION

.. py:data:: REDUCE_MEAN_SYSTEM_PROMPT
   :canonical: opto.optimizers.textgrad.REDUCE_MEAN_SYSTEM_PROMPT
   :value: 'You are part of an optimization system that improves a given text (i.e. the variable). Your only res...'

   .. autodoc2-docstring:: opto.optimizers.textgrad.REDUCE_MEAN_SYSTEM_PROMPT

.. py:class:: GradientInfo
   :canonical: opto.optimizers.textgrad.GradientInfo

   .. autodoc2-docstring:: opto.optimizers.textgrad.GradientInfo

   .. py:attribute:: gradient
      :canonical: opto.optimizers.textgrad.GradientInfo.gradient
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.textgrad.GradientInfo.gradient

   .. py:attribute:: gradient_context
      :canonical: opto.optimizers.textgrad.GradientInfo.gradient_context
      :type: typing.Optional[typing.Dict[str, str]]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.textgrad.GradientInfo.gradient_context

.. py:function:: construct_reduce_prompt(gradients: typing.List[opto.optimizers.textgrad.GradientInfo])
   :canonical: opto.optimizers.textgrad.construct_reduce_prompt

   .. autodoc2-docstring:: opto.optimizers.textgrad.construct_reduce_prompt

.. py:function:: rm_node_attrs(text: str) -> str
   :canonical: opto.optimizers.textgrad.rm_node_attrs

   .. autodoc2-docstring:: opto.optimizers.textgrad.rm_node_attrs

.. py:function:: get_short_value(text, n_words_offset: int = 10) -> str
   :canonical: opto.optimizers.textgrad.get_short_value

   .. autodoc2-docstring:: opto.optimizers.textgrad.get_short_value

.. py:class:: TextGrad(parameters: typing.List[opto.trace.nodes.ParameterNode], llm: opto.utils.llm.AutoGenLLM = None, *args, propagator: opto.trace.propagators.Propagator = None, objective: typing.Union[None, str] = None, max_tokens=4096, log=False, **kwargs)
   :canonical: opto.optimizers.textgrad.TextGrad

   Bases: :py:obj:`opto.optimizers.optimizer.Optimizer`

   .. py:method:: call_llm(system_prompt: str, user_prompt: str, verbose: typing.Union[bool, str] = False)
      :canonical: opto.optimizers.textgrad.TextGrad.call_llm

      .. autodoc2-docstring:: opto.optimizers.textgrad.TextGrad.call_llm
