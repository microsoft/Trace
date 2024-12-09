:py:mod:`opto.optimizers.optoprime`
===================================

.. py:module:: opto.optimizers.optoprime

.. autodoc2-docstring:: opto.optimizers.optoprime
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`FunctionFeedback <opto.optimizers.optoprime.FunctionFeedback>`
     - .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback
          :summary:
   * - :py:obj:`ProblemInstance <opto.optimizers.optoprime.ProblemInstance>`
     - .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance
          :summary:
   * - :py:obj:`OptoPrime <opto.optimizers.optoprime.OptoPrime>`
     -

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`get_fun_name <opto.optimizers.optoprime.get_fun_name>`
     - .. autodoc2-docstring:: opto.optimizers.optoprime.get_fun_name
          :summary:
   * - :py:obj:`repr_function_call <opto.optimizers.optoprime.repr_function_call>`
     - .. autodoc2-docstring:: opto.optimizers.optoprime.repr_function_call
          :summary:
   * - :py:obj:`node_to_function_feedback <opto.optimizers.optoprime.node_to_function_feedback>`
     - .. autodoc2-docstring:: opto.optimizers.optoprime.node_to_function_feedback
          :summary:

API
~~~

.. py:function:: get_fun_name(node: opto.trace.nodes.MessageNode)
   :canonical: opto.optimizers.optoprime.get_fun_name

   .. autodoc2-docstring:: opto.optimizers.optoprime.get_fun_name

.. py:function:: repr_function_call(child: opto.trace.nodes.MessageNode)
   :canonical: opto.optimizers.optoprime.repr_function_call

   .. autodoc2-docstring:: opto.optimizers.optoprime.repr_function_call

.. py:function:: node_to_function_feedback(node_feedback: opto.trace.propagators.TraceGraph)
   :canonical: opto.optimizers.optoprime.node_to_function_feedback

   .. autodoc2-docstring:: opto.optimizers.optoprime.node_to_function_feedback

.. py:class:: FunctionFeedback
   :canonical: opto.optimizers.optoprime.FunctionFeedback

   .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback

   .. py:attribute:: graph
      :canonical: opto.optimizers.optoprime.FunctionFeedback.graph
      :type: typing.List[typing.Tuple[int, str]]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback.graph

   .. py:attribute:: documentation
      :canonical: opto.optimizers.optoprime.FunctionFeedback.documentation
      :type: typing.Dict[str, str]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback.documentation

   .. py:attribute:: others
      :canonical: opto.optimizers.optoprime.FunctionFeedback.others
      :type: typing.Dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback.others

   .. py:attribute:: roots
      :canonical: opto.optimizers.optoprime.FunctionFeedback.roots
      :type: typing.Dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback.roots

   .. py:attribute:: output
      :canonical: opto.optimizers.optoprime.FunctionFeedback.output
      :type: typing.Dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback.output

   .. py:attribute:: user_feedback
      :canonical: opto.optimizers.optoprime.FunctionFeedback.user_feedback
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.FunctionFeedback.user_feedback

.. py:class:: ProblemInstance
   :canonical: opto.optimizers.optoprime.ProblemInstance

   .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance

   .. py:attribute:: instruction
      :canonical: opto.optimizers.optoprime.ProblemInstance.instruction
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.instruction

   .. py:attribute:: code
      :canonical: opto.optimizers.optoprime.ProblemInstance.code
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.code

   .. py:attribute:: documentation
      :canonical: opto.optimizers.optoprime.ProblemInstance.documentation
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.documentation

   .. py:attribute:: variables
      :canonical: opto.optimizers.optoprime.ProblemInstance.variables
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.variables

   .. py:attribute:: inputs
      :canonical: opto.optimizers.optoprime.ProblemInstance.inputs
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.inputs

   .. py:attribute:: others
      :canonical: opto.optimizers.optoprime.ProblemInstance.others
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.others

   .. py:attribute:: outputs
      :canonical: opto.optimizers.optoprime.ProblemInstance.outputs
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.outputs

   .. py:attribute:: feedback
      :canonical: opto.optimizers.optoprime.ProblemInstance.feedback
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.feedback

   .. py:attribute:: constraints
      :canonical: opto.optimizers.optoprime.ProblemInstance.constraints
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.constraints

   .. py:attribute:: problem_template
      :canonical: opto.optimizers.optoprime.ProblemInstance.problem_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.ProblemInstance.problem_template

.. py:class:: OptoPrime(parameters: typing.List[opto.trace.nodes.ParameterNode], llm: opto.utils.llm.AutoGenLLM = None, *args, propagator: opto.trace.propagators.propagators.Propagator = None, objective: typing.Union[None, str] = None, ignore_extraction_error: bool = True, include_example=False, memory_size=0, max_tokens=4096, log=True, prompt_symbols=None, filter_dict: typing.Dict = None, **kwargs)
   :canonical: opto.optimizers.optoprime.OptoPrime

   Bases: :py:obj:`opto.optimizers.optimizer.Optimizer`

   .. py:attribute:: representation_prompt
      :canonical: opto.optimizers.optoprime.OptoPrime.representation_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.representation_prompt

   .. py:attribute:: default_objective
      :canonical: opto.optimizers.optoprime.OptoPrime.default_objective
      :value: 'You need to change the <value> of the variables in #Variables to improve the output in accordance to...'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.default_objective

   .. py:attribute:: output_format_prompt
      :canonical: opto.optimizers.optoprime.OptoPrime.output_format_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.output_format_prompt

   .. py:attribute:: example_problem_template
      :canonical: opto.optimizers.optoprime.OptoPrime.example_problem_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.example_problem_template

   .. py:attribute:: user_prompt_template
      :canonical: opto.optimizers.optoprime.OptoPrime.user_prompt_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.user_prompt_template

   .. py:attribute:: example_prompt
      :canonical: opto.optimizers.optoprime.OptoPrime.example_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.example_prompt

   .. py:attribute:: final_prompt
      :canonical: opto.optimizers.optoprime.OptoPrime.final_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.final_prompt

   .. py:attribute:: default_prompt_symbols
      :canonical: opto.optimizers.optoprime.OptoPrime.default_prompt_symbols
      :value: None

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.default_prompt_symbols

   .. py:method:: default_propagator()
      :canonical: opto.optimizers.optoprime.OptoPrime.default_propagator

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.default_propagator

   .. py:method:: summarize()
      :canonical: opto.optimizers.optoprime.OptoPrime.summarize

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.summarize

   .. py:method:: repr_node_value(node_dict)
      :canonical: opto.optimizers.optoprime.OptoPrime.repr_node_value
      :staticmethod:

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.repr_node_value

   .. py:method:: repr_node_constraint(node_dict)
      :canonical: opto.optimizers.optoprime.OptoPrime.repr_node_constraint
      :staticmethod:

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.repr_node_constraint

   .. py:method:: problem_instance(summary, mask=None)
      :canonical: opto.optimizers.optoprime.OptoPrime.problem_instance

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.problem_instance

   .. py:method:: construct_prompt(summary, mask=None, *args, **kwargs)
      :canonical: opto.optimizers.optoprime.OptoPrime.construct_prompt

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.construct_prompt

   .. py:method:: replace_symbols(text: str, symbols: typing.Dict[str, str]) -> str
      :canonical: opto.optimizers.optoprime.OptoPrime.replace_symbols

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.replace_symbols

   .. py:method:: construct_update_dict(suggestion: typing.Dict[str, typing.Any]) -> typing.Dict[opto.trace.nodes.ParameterNode, typing.Any]
      :canonical: opto.optimizers.optoprime.OptoPrime.construct_update_dict

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.construct_update_dict

   .. py:method:: extract_llm_suggestion(response: str)
      :canonical: opto.optimizers.optoprime.OptoPrime.extract_llm_suggestion

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.extract_llm_suggestion

   .. py:method:: call_llm(system_prompt: str, user_prompt: str, verbose: typing.Union[bool, str] = False, max_tokens: int = 4096)
      :canonical: opto.optimizers.optoprime.OptoPrime.call_llm

      .. autodoc2-docstring:: opto.optimizers.optoprime.OptoPrime.call_llm
