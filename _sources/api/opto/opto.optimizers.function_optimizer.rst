:py:mod:`opto.optimizers.function_optimizer`
============================================

.. py:module:: opto.optimizers.function_optimizer

.. autodoc2-docstring:: opto.optimizers.function_optimizer
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`FunctionFeedback <opto.optimizers.function_optimizer.FunctionFeedback>`
     - .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback
          :summary:
   * - :py:obj:`ProblemInstance <opto.optimizers.function_optimizer.ProblemInstance>`
     - .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance
          :summary:
   * - :py:obj:`OptoPrime <opto.optimizers.function_optimizer.OptoPrime>`
     -

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`get_fun_name <opto.optimizers.function_optimizer.get_fun_name>`
     - .. autodoc2-docstring:: opto.optimizers.function_optimizer.get_fun_name
          :summary:
   * - :py:obj:`repr_function_call <opto.optimizers.function_optimizer.repr_function_call>`
     - .. autodoc2-docstring:: opto.optimizers.function_optimizer.repr_function_call
          :summary:
   * - :py:obj:`node_to_function_feedback <opto.optimizers.function_optimizer.node_to_function_feedback>`
     - .. autodoc2-docstring:: opto.optimizers.function_optimizer.node_to_function_feedback
          :summary:

API
~~~

.. py:function:: get_fun_name(node: opto.trace.nodes.MessageNode)
   :canonical: opto.optimizers.function_optimizer.get_fun_name

   .. autodoc2-docstring:: opto.optimizers.function_optimizer.get_fun_name

.. py:function:: repr_function_call(child: opto.trace.nodes.MessageNode)
   :canonical: opto.optimizers.function_optimizer.repr_function_call

   .. autodoc2-docstring:: opto.optimizers.function_optimizer.repr_function_call

.. py:function:: node_to_function_feedback(node_feedback: opto.trace.propagators.TraceGraph)
   :canonical: opto.optimizers.function_optimizer.node_to_function_feedback

   .. autodoc2-docstring:: opto.optimizers.function_optimizer.node_to_function_feedback

.. py:class:: FunctionFeedback
   :canonical: opto.optimizers.function_optimizer.FunctionFeedback

   .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback

   .. py:attribute:: graph
      :canonical: opto.optimizers.function_optimizer.FunctionFeedback.graph
      :type: typing.List[typing.Tuple[int, str]]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback.graph

   .. py:attribute:: documentation
      :canonical: opto.optimizers.function_optimizer.FunctionFeedback.documentation
      :type: typing.Dict[str, str]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback.documentation

   .. py:attribute:: others
      :canonical: opto.optimizers.function_optimizer.FunctionFeedback.others
      :type: typing.Dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback.others

   .. py:attribute:: roots
      :canonical: opto.optimizers.function_optimizer.FunctionFeedback.roots
      :type: typing.Dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback.roots

   .. py:attribute:: output
      :canonical: opto.optimizers.function_optimizer.FunctionFeedback.output
      :type: typing.Dict[str, typing.Any]
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback.output

   .. py:attribute:: user_feedback
      :canonical: opto.optimizers.function_optimizer.FunctionFeedback.user_feedback
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionFeedback.user_feedback

.. py:class:: ProblemInstance
   :canonical: opto.optimizers.function_optimizer.ProblemInstance

   .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance

   .. py:attribute:: instruction
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.instruction
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.instruction

   .. py:attribute:: code
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.code
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.code

   .. py:attribute:: documentation
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.documentation
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.documentation

   .. py:attribute:: variables
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.variables
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.variables

   .. py:attribute:: inputs
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.inputs
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.inputs

   .. py:attribute:: others
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.others
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.others

   .. py:attribute:: outputs
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.outputs
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.outputs

   .. py:attribute:: feedback
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.feedback
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.feedback

   .. py:attribute:: constraints
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.constraints
      :type: str
      :value: None

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.constraints

   .. py:attribute:: problem_template
      :canonical: opto.optimizers.function_optimizer.ProblemInstance.problem_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.ProblemInstance.problem_template

.. py:class:: OptoPrime(parameters: typing.List[opto.trace.nodes.ParameterNode], config_list: typing.List = None, *args, propagator: opto.trace.propagators.propagators.Propagator = None, objective: typing.Union[None, str] = None, ignore_extraction_error: bool = True, include_example=False, memory_size=0, max_tokens=4096, log=True, **kwargs)
   :canonical: opto.optimizers.function_optimizer.OptoPrime

   Bases: :py:obj:`opto.optimizers.optimizer.Optimizer`

   .. py:attribute:: representation_prompt
      :canonical: opto.optimizers.function_optimizer.OptoPrime.representation_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.representation_prompt

   .. py:attribute:: default_objective
      :canonical: opto.optimizers.function_optimizer.OptoPrime.default_objective
      :value: 'You need to change the <value> of the variables in #Variables to improve the output in accordance to...'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.default_objective

   .. py:attribute:: output_format_prompt
      :canonical: opto.optimizers.function_optimizer.OptoPrime.output_format_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.output_format_prompt

   .. py:attribute:: example_problem_template
      :canonical: opto.optimizers.function_optimizer.OptoPrime.example_problem_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.example_problem_template

   .. py:attribute:: user_prompt_template
      :canonical: opto.optimizers.function_optimizer.OptoPrime.user_prompt_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.user_prompt_template

   .. py:attribute:: example_prompt
      :canonical: opto.optimizers.function_optimizer.OptoPrime.example_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.example_prompt

   .. py:attribute:: final_prompt
      :canonical: opto.optimizers.function_optimizer.OptoPrime.final_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.final_prompt

   .. py:method:: default_propagator()
      :canonical: opto.optimizers.function_optimizer.OptoPrime.default_propagator

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.default_propagator

   .. py:method:: summarize()
      :canonical: opto.optimizers.function_optimizer.OptoPrime.summarize

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.summarize

   .. py:method:: repr_node_value(node_dict)
      :canonical: opto.optimizers.function_optimizer.OptoPrime.repr_node_value
      :staticmethod:

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.repr_node_value

   .. py:method:: repr_node_constraint(node_dict)
      :canonical: opto.optimizers.function_optimizer.OptoPrime.repr_node_constraint
      :staticmethod:

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.repr_node_constraint

   .. py:method:: probelm_instance(summary, mask=None)
      :canonical: opto.optimizers.function_optimizer.OptoPrime.probelm_instance

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.probelm_instance

   .. py:method:: construct_prompt(summary, mask=None, *args, **kwargs)
      :canonical: opto.optimizers.function_optimizer.OptoPrime.construct_prompt

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.construct_prompt

   .. py:method:: construct_update_dict(suggestion: typing.Dict[str, typing.Any]) -> typing.Dict[opto.trace.nodes.ParameterNode, typing.Any]
      :canonical: opto.optimizers.function_optimizer.OptoPrime.construct_update_dict

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.construct_update_dict

   .. py:method:: extract_llm_suggestion(response: str)
      :canonical: opto.optimizers.function_optimizer.OptoPrime.extract_llm_suggestion

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.extract_llm_suggestion

   .. py:method:: call_llm(system_prompt: str, user_prompt: str, verbose: typing.Union[bool, str] = False, max_tokens: int = 4096)
      :canonical: opto.optimizers.function_optimizer.OptoPrime.call_llm

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.OptoPrime.call_llm
