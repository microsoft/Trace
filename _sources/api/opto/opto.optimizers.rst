:py:mod:`opto.optimizers`
=========================

.. py:module:: opto.optimizers

.. autodoc2-docstring:: opto.optimizers
   :allowtitles:

Package Contents
----------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`OPRO <opto.optimizers.opro.OPRO>`
     -
   * - :py:obj:`OptoPrime <opto.optimizers.function_optimizer.OptoPrime>`
     -

API
~~~

.. py:class:: OPRO(*args, **kwargs)
   :canonical: opto.optimizers.opro.OPRO

   Bases: :py:obj:`opto.optimizers.function_optimizer.OptoPrime`

   .. py:attribute:: user_prompt_template
      :canonical: opto.optimizers.opro.OPRO.user_prompt_template
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.opro.OPRO.user_prompt_template

   .. py:attribute:: output_format_prompt
      :canonical: opto.optimizers.opro.OPRO.output_format_prompt
      :value: 'dedent(...)'

      .. autodoc2-docstring:: opto.optimizers.opro.OPRO.output_format_prompt

   .. py:attribute:: default_objective
      :canonical: opto.optimizers.opro.OPRO.default_objective
      :value: 'Come up with a new variable in accordance to feedback.'

      .. autodoc2-docstring:: opto.optimizers.opro.OPRO.default_objective

   .. py:method:: construct_prompt(summary, mask=None, *args, **kwargs)
      :canonical: opto.optimizers.opro.OPRO.construct_prompt

      .. autodoc2-docstring:: opto.optimizers.opro.OPRO.construct_prompt

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
