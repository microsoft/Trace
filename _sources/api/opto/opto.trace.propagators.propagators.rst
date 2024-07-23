:py:mod:`opto.trace.propagators.propagators`
============================================

.. py:module:: opto.trace.propagators.propagators

.. autodoc2-docstring:: opto.trace.propagators.propagators
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`AbstractPropagator <opto.trace.propagators.propagators.AbstractPropagator>`
     - .. autodoc2-docstring:: opto.trace.propagators.propagators.AbstractPropagator
          :summary:
   * - :py:obj:`AbstractFeedback <opto.trace.propagators.propagators.AbstractFeedback>`
     - .. autodoc2-docstring:: opto.trace.propagators.propagators.AbstractFeedback
          :summary:
   * - :py:obj:`Propagator <opto.trace.propagators.propagators.Propagator>`
     - .. autodoc2-docstring:: opto.trace.propagators.propagators.Propagator
          :summary:
   * - :py:obj:`SumPropagator <opto.trace.propagators.propagators.SumPropagator>`
     - .. autodoc2-docstring:: opto.trace.propagators.propagators.SumPropagator
          :summary:

API
~~~

.. py:class:: AbstractPropagator
   :canonical: opto.trace.propagators.propagators.AbstractPropagator

   .. autodoc2-docstring:: opto.trace.propagators.propagators.AbstractPropagator

   .. py:method:: propagate(child: opto.trace.nodes.MessageNode) -> typing.Dict[opto.trace.nodes.Node, typing.Any]
      :canonical: opto.trace.propagators.propagators.AbstractPropagator.propagate
      :abstractmethod:

      .. autodoc2-docstring:: opto.trace.propagators.propagators.AbstractPropagator.propagate

.. py:class:: AbstractFeedback
   :canonical: opto.trace.propagators.propagators.AbstractFeedback

   .. autodoc2-docstring:: opto.trace.propagators.propagators.AbstractFeedback

.. py:class:: Propagator()
   :canonical: opto.trace.propagators.propagators.Propagator

   Bases: :py:obj:`opto.trace.propagators.propagators.AbstractPropagator`

   .. autodoc2-docstring:: opto.trace.propagators.propagators.Propagator

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.propagators.propagators.Propagator.__init__

   .. py:method:: register(operator_name, propagate_function)
      :canonical: opto.trace.propagators.propagators.Propagator.register

      .. autodoc2-docstring:: opto.trace.propagators.propagators.Propagator.register

   .. py:method:: propagate(child: opto.trace.nodes.MessageNode) -> typing.Dict[opto.trace.nodes.Node, typing.Any]
      :canonical: opto.trace.propagators.propagators.Propagator.propagate

   .. py:method:: init_feedback(feedback: typing.Any)
      :canonical: opto.trace.propagators.propagators.Propagator.init_feedback
      :abstractmethod:

      .. autodoc2-docstring:: opto.trace.propagators.propagators.Propagator.init_feedback

.. py:class:: SumPropagator()
   :canonical: opto.trace.propagators.propagators.SumPropagator

   Bases: :py:obj:`opto.trace.propagators.propagators.Propagator`

   .. autodoc2-docstring:: opto.trace.propagators.propagators.SumPropagator

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.propagators.propagators.SumPropagator.__init__

   .. py:method:: init_feedback(feedback: typing.Any)
      :canonical: opto.trace.propagators.propagators.SumPropagator.init_feedback
