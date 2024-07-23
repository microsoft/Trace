:py:mod:`opto.optimizers.optimizer`
===================================

.. py:module:: opto.optimizers.optimizer

.. autodoc2-docstring:: opto.optimizers.optimizer
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`AbstractOptimizer <opto.optimizers.optimizer.AbstractOptimizer>`
     - .. autodoc2-docstring:: opto.optimizers.optimizer.AbstractOptimizer
          :summary:
   * - :py:obj:`Optimizer <opto.optimizers.optimizer.Optimizer>`
     -

API
~~~

.. py:class:: AbstractOptimizer(parameters: typing.List[opto.trace.nodes.ParameterNode], *args, **kwargs)
   :canonical: opto.optimizers.optimizer.AbstractOptimizer

   .. autodoc2-docstring:: opto.optimizers.optimizer.AbstractOptimizer

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.optimizers.optimizer.AbstractOptimizer.__init__

   .. py:method:: step()
      :canonical: opto.optimizers.optimizer.AbstractOptimizer.step
      :abstractmethod:

      .. autodoc2-docstring:: opto.optimizers.optimizer.AbstractOptimizer.step

   .. py:method:: zero_feedback()
      :canonical: opto.optimizers.optimizer.AbstractOptimizer.zero_feedback
      :abstractmethod:

      .. autodoc2-docstring:: opto.optimizers.optimizer.AbstractOptimizer.zero_feedback

   .. py:property:: propagator
      :canonical: opto.optimizers.optimizer.AbstractOptimizer.propagator
      :abstractmethod:

      .. autodoc2-docstring:: opto.optimizers.optimizer.AbstractOptimizer.propagator

.. py:class:: Optimizer(parameters: typing.List[opto.trace.nodes.ParameterNode], *args, propagator: opto.trace.propagators.propagators.Propagator = None, **kwargs)
   :canonical: opto.optimizers.optimizer.Optimizer

   Bases: :py:obj:`opto.optimizers.optimizer.AbstractOptimizer`

   .. py:property:: propagator
      :canonical: opto.optimizers.optimizer.Optimizer.propagator

   .. py:method:: step(*args, **kwargs)
      :canonical: opto.optimizers.optimizer.Optimizer.step

   .. py:method:: propose(*args, **kwargs)
      :canonical: opto.optimizers.optimizer.Optimizer.propose

      .. autodoc2-docstring:: opto.optimizers.optimizer.Optimizer.propose

   .. py:method:: update(update_dict: typing.Dict[opto.trace.nodes.ParameterNode, typing.Any])
      :canonical: opto.optimizers.optimizer.Optimizer.update

      .. autodoc2-docstring:: opto.optimizers.optimizer.Optimizer.update

   .. py:method:: zero_feedback()
      :canonical: opto.optimizers.optimizer.Optimizer.zero_feedback

   .. py:method:: default_propagator()
      :canonical: opto.optimizers.optimizer.Optimizer.default_propagator
      :abstractmethod:

      .. autodoc2-docstring:: opto.optimizers.optimizer.Optimizer.default_propagator

   .. py:method:: backward(node: opto.trace.nodes.Node, *args, **kwargs)
      :canonical: opto.optimizers.optimizer.Optimizer.backward

      .. autodoc2-docstring:: opto.optimizers.optimizer.Optimizer.backward
