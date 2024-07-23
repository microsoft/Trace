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
   * - :py:obj:`FunctionOptimizerV2Memory <opto.optimizers.function_optimizer.FunctionOptimizerV2Memory>`
     -

API
~~~

.. py:class:: OPRO(*args, **kwargs)
   :canonical: opto.optimizers.opro.OPRO

   Bases: :py:obj:`opto.optimizers.function_optimizer.FunctionOptimizer`

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

.. py:class:: FunctionOptimizerV2Memory(*args, memory_size=0, **kwargs)
   :canonical: opto.optimizers.function_optimizer.FunctionOptimizerV2Memory

   Bases: :py:obj:`opto.optimizers.function_optimizer.FunctionOptimizerV2`

   .. py:method:: construct_prompt(summary, mask=None, *args, **kwargs)
      :canonical: opto.optimizers.function_optimizer.FunctionOptimizerV2Memory.construct_prompt

      .. autodoc2-docstring:: opto.optimizers.function_optimizer.FunctionOptimizerV2Memory.construct_prompt
