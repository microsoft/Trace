:py:mod:`opto.trace`
====================

.. py:module:: opto.trace

.. autodoc2-docstring:: opto.trace
   :allowtitles:

Subpackages
-----------

.. toctree::
   :titlesonly:
   :maxdepth: 3

   opto.trace.propagators

Package Contents
----------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`stop_tracing <opto.trace.stop_tracing>`
     - .. autodoc2-docstring:: opto.trace.stop_tracing
          :summary:
   * - :py:obj:`Node <opto.trace.nodes.Node>`
     - .. autodoc2-docstring:: opto.trace.nodes.Node
          :summary:
   * - :py:obj:`Module <opto.trace.modules.Module>`
     - .. autodoc2-docstring:: opto.trace.modules.Module
          :summary:
   * - :py:obj:`NodeContainer <opto.trace.containers.NodeContainer>`
     - .. autodoc2-docstring:: opto.trace.containers.NodeContainer
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`node <opto.trace.nodes.node>`
     - .. autodoc2-docstring:: opto.trace.nodes.node
          :summary:
   * - :py:obj:`model <opto.trace.modules.model>`
     - .. autodoc2-docstring:: opto.trace.modules.model
          :summary:
   * - :py:obj:`apply_op <opto.trace.broadcast.apply_op>`
     - .. autodoc2-docstring:: opto.trace.broadcast.apply_op
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`GRAPH <opto.trace.nodes.GRAPH>`
     - .. autodoc2-docstring:: opto.trace.nodes.GRAPH
          :summary:

API
~~~

.. py:function:: node(data, name=None, trainable=False, description=None, constraint=None)
   :canonical: opto.trace.nodes.node

   .. autodoc2-docstring:: opto.trace.nodes.node

.. py:class:: stop_tracing
   :canonical: opto.trace.stop_tracing

   .. autodoc2-docstring:: opto.trace.stop_tracing

.. py:data:: GRAPH
   :canonical: opto.trace.nodes.GRAPH
   :value: 'Graph(...)'

   .. autodoc2-docstring:: opto.trace.nodes.GRAPH

.. py:class:: Node(value: typing.Any, *, name: str = None, trainable: bool = False, description: str = '[Node] This is a node in a computational graph.', constraint: typing.Union[None, str] = None, info: typing.Union[None, typing.Dict] = None)
   :canonical: opto.trace.nodes.Node

   Bases: :py:obj:`opto.trace.nodes.AbstractNode`\ [\ :py:obj:`opto.trace.nodes.T`\ ]

   .. autodoc2-docstring:: opto.trace.nodes.Node

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.Node.__init__

   .. py:method:: zero_feedback()
      :canonical: opto.trace.nodes.Node.zero_feedback

      .. autodoc2-docstring:: opto.trace.nodes.Node.zero_feedback

   .. py:property:: feedback
      :canonical: opto.trace.nodes.Node.feedback

      .. autodoc2-docstring:: opto.trace.nodes.Node.feedback

   .. py:property:: description
      :canonical: opto.trace.nodes.Node.description

      .. autodoc2-docstring:: opto.trace.nodes.Node.description

   .. py:property:: info
      :canonical: opto.trace.nodes.Node.info

      .. autodoc2-docstring:: opto.trace.nodes.Node.info

   .. py:property:: type
      :canonical: opto.trace.nodes.Node.type

      .. autodoc2-docstring:: opto.trace.nodes.Node.type

   .. py:property:: parameter_dependencies
      :canonical: opto.trace.nodes.Node.parameter_dependencies

      .. autodoc2-docstring:: opto.trace.nodes.Node.parameter_dependencies

   .. py:property:: expandable_dependencies
      :canonical: opto.trace.nodes.Node.expandable_dependencies

      .. autodoc2-docstring:: opto.trace.nodes.Node.expandable_dependencies

   .. py:method:: backward(feedback: typing.Any = '', propagator=None, retain_graph=False, visualize=False, simple_visualization=True, reverse_plot=False, print_limit=100)
      :canonical: opto.trace.nodes.Node.backward

      .. autodoc2-docstring:: opto.trace.nodes.Node.backward

   .. py:method:: clone()
      :canonical: opto.trace.nodes.Node.clone

      .. autodoc2-docstring:: opto.trace.nodes.Node.clone

   .. py:method:: detach()
      :canonical: opto.trace.nodes.Node.detach

      .. autodoc2-docstring:: opto.trace.nodes.Node.detach

   .. py:method:: getattr(key)
      :canonical: opto.trace.nodes.Node.getattr

      .. autodoc2-docstring:: opto.trace.nodes.Node.getattr

   .. py:method:: call(fun: str, *args, **kwargs)
      :canonical: opto.trace.nodes.Node.call

      .. autodoc2-docstring:: opto.trace.nodes.Node.call

   .. py:method:: len()
      :canonical: opto.trace.nodes.Node.len

      .. autodoc2-docstring:: opto.trace.nodes.Node.len

   .. py:method:: eq(other)
      :canonical: opto.trace.nodes.Node.eq

      .. autodoc2-docstring:: opto.trace.nodes.Node.eq

   .. py:method:: neq(other)
      :canonical: opto.trace.nodes.Node.neq

      .. autodoc2-docstring:: opto.trace.nodes.Node.neq

   .. py:method:: format(*args, **kwargs)
      :canonical: opto.trace.nodes.Node.format

      .. autodoc2-docstring:: opto.trace.nodes.Node.format

   .. py:method:: capitalize()
      :canonical: opto.trace.nodes.Node.capitalize

      .. autodoc2-docstring:: opto.trace.nodes.Node.capitalize

   .. py:method:: lower()
      :canonical: opto.trace.nodes.Node.lower

      .. autodoc2-docstring:: opto.trace.nodes.Node.lower

   .. py:method:: upper()
      :canonical: opto.trace.nodes.Node.upper

      .. autodoc2-docstring:: opto.trace.nodes.Node.upper

   .. py:method:: swapcase()
      :canonical: opto.trace.nodes.Node.swapcase

      .. autodoc2-docstring:: opto.trace.nodes.Node.swapcase

   .. py:method:: title()
      :canonical: opto.trace.nodes.Node.title

      .. autodoc2-docstring:: opto.trace.nodes.Node.title

   .. py:method:: split(sep=None, maxsplit=-1)
      :canonical: opto.trace.nodes.Node.split

      .. autodoc2-docstring:: opto.trace.nodes.Node.split

   .. py:method:: strip(chars=None)
      :canonical: opto.trace.nodes.Node.strip

      .. autodoc2-docstring:: opto.trace.nodes.Node.strip

   .. py:method:: replace(old, new, count=-1)
      :canonical: opto.trace.nodes.Node.replace

      .. autodoc2-docstring:: opto.trace.nodes.Node.replace

   .. py:method:: items()
      :canonical: opto.trace.nodes.Node.items

      .. autodoc2-docstring:: opto.trace.nodes.Node.items

   .. py:method:: values()
      :canonical: opto.trace.nodes.Node.values

      .. autodoc2-docstring:: opto.trace.nodes.Node.values

   .. py:method:: keys()
      :canonical: opto.trace.nodes.Node.keys

      .. autodoc2-docstring:: opto.trace.nodes.Node.keys

   .. py:method:: pop(__index=-1)
      :canonical: opto.trace.nodes.Node.pop

      .. autodoc2-docstring:: opto.trace.nodes.Node.pop

   .. py:method:: append(*args, **kwargs)
      :canonical: opto.trace.nodes.Node.append

      .. autodoc2-docstring:: opto.trace.nodes.Node.append

.. py:class:: Module
   :canonical: opto.trace.modules.Module

   Bases: :py:obj:`opto.trace.containers.ParameterContainer`

   .. autodoc2-docstring:: opto.trace.modules.Module

   .. py:method:: forward(*args, **kwargs)
      :canonical: opto.trace.modules.Module.forward
      :abstractmethod:

      .. autodoc2-docstring:: opto.trace.modules.Module.forward

   .. py:method:: save(file_name)
      :canonical: opto.trace.modules.Module.save

      .. autodoc2-docstring:: opto.trace.modules.Module.save

   .. py:method:: load(file_name)
      :canonical: opto.trace.modules.Module.load

      .. autodoc2-docstring:: opto.trace.modules.Module.load

.. py:class:: NodeContainer
   :canonical: opto.trace.containers.NodeContainer

   .. autodoc2-docstring:: opto.trace.containers.NodeContainer

.. py:function:: model(cls)
   :canonical: opto.trace.modules.model

   .. autodoc2-docstring:: opto.trace.modules.model

.. py:function:: apply_op(op, output, *args, **kwargs)
   :canonical: opto.trace.broadcast.apply_op

   .. autodoc2-docstring:: opto.trace.broadcast.apply_op
