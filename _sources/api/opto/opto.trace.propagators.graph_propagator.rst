:py:mod:`opto.trace.propagators.graph_propagator`
=================================================

.. py:module:: opto.trace.propagators.graph_propagator

.. autodoc2-docstring:: opto.trace.propagators.graph_propagator
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`TraceGraph <opto.trace.propagators.graph_propagator.TraceGraph>`
     - .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph
          :summary:
   * - :py:obj:`GraphPropagator <opto.trace.propagators.graph_propagator.GraphPropagator>`
     - .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.GraphPropagator
          :summary:

API
~~~

.. py:class:: TraceGraph
   :canonical: opto.trace.propagators.graph_propagator.TraceGraph

   Bases: :py:obj:`opto.trace.propagators.propagators.AbstractFeedback`

   .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph

   .. py:attribute:: graph
      :canonical: opto.trace.propagators.graph_propagator.TraceGraph.graph
      :type: typing.List[typing.Tuple[int, opto.trace.nodes.Node]]
      :value: None

      .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph.graph

   .. py:attribute:: user_feedback
      :canonical: opto.trace.propagators.graph_propagator.TraceGraph.user_feedback
      :type: typing.Any
      :value: None

      .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph.user_feedback

   .. py:method:: empty()
      :canonical: opto.trace.propagators.graph_propagator.TraceGraph.empty

      .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph.empty

   .. py:method:: expand(node: opto.trace.nodes.MessageNode)
      :canonical: opto.trace.propagators.graph_propagator.TraceGraph.expand
      :classmethod:

      .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph.expand

   .. py:method:: visualize(simple_visualization=True, reverse_plot=False, print_limit=100)
      :canonical: opto.trace.propagators.graph_propagator.TraceGraph.visualize

      .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.TraceGraph.visualize

.. py:class:: GraphPropagator()
   :canonical: opto.trace.propagators.graph_propagator.GraphPropagator

   Bases: :py:obj:`opto.trace.propagators.propagators.Propagator`

   .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.GraphPropagator

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.GraphPropagator.__init__

   .. py:method:: init_feedback(node, feedback: typing.Any)
      :canonical: opto.trace.propagators.graph_propagator.GraphPropagator.init_feedback

   .. py:method:: aggregate(feedback: typing.Dict[opto.trace.nodes.Node, typing.List[opto.trace.propagators.graph_propagator.TraceGraph]])
      :canonical: opto.trace.propagators.graph_propagator.GraphPropagator.aggregate

      .. autodoc2-docstring:: opto.trace.propagators.graph_propagator.GraphPropagator.aggregate
