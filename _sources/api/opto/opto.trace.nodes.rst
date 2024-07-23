:py:mod:`opto.trace.nodes`
==========================

.. py:module:: opto.trace.nodes

.. autodoc2-docstring:: opto.trace.nodes
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Graph <opto.trace.nodes.Graph>`
     - .. autodoc2-docstring:: opto.trace.nodes.Graph
          :summary:
   * - :py:obj:`AbstractNode <opto.trace.nodes.AbstractNode>`
     - .. autodoc2-docstring:: opto.trace.nodes.AbstractNode
          :summary:
   * - :py:obj:`NodeVizStyleGuide <opto.trace.nodes.NodeVizStyleGuide>`
     - .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide
          :summary:
   * - :py:obj:`NodeVizStyleGuideColorful <opto.trace.nodes.NodeVizStyleGuideColorful>`
     - .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful
          :summary:
   * - :py:obj:`Node <opto.trace.nodes.Node>`
     - .. autodoc2-docstring:: opto.trace.nodes.Node
          :summary:
   * - :py:obj:`ParameterNode <opto.trace.nodes.ParameterNode>`
     -
   * - :py:obj:`MessageNode <opto.trace.nodes.MessageNode>`
     - .. autodoc2-docstring:: opto.trace.nodes.MessageNode
          :summary:
   * - :py:obj:`ExceptionNode <opto.trace.nodes.ExceptionNode>`
     - .. autodoc2-docstring:: opto.trace.nodes.ExceptionNode
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`node <opto.trace.nodes.node>`
     - .. autodoc2-docstring:: opto.trace.nodes.node
          :summary:
   * - :py:obj:`get_op_name <opto.trace.nodes.get_op_name>`
     - .. autodoc2-docstring:: opto.trace.nodes.get_op_name
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`NAME_SCOPES <opto.trace.nodes.NAME_SCOPES>`
     - .. autodoc2-docstring:: opto.trace.nodes.NAME_SCOPES
          :summary:
   * - :py:obj:`GRAPH <opto.trace.nodes.GRAPH>`
     - .. autodoc2-docstring:: opto.trace.nodes.GRAPH
          :summary:
   * - :py:obj:`USED_NODES <opto.trace.nodes.USED_NODES>`
     - .. autodoc2-docstring:: opto.trace.nodes.USED_NODES
          :summary:
   * - :py:obj:`T <opto.trace.nodes.T>`
     - .. autodoc2-docstring:: opto.trace.nodes.T
          :summary:
   * - :py:obj:`IDENTITY_OPERATORS <opto.trace.nodes.IDENTITY_OPERATORS>`
     - .. autodoc2-docstring:: opto.trace.nodes.IDENTITY_OPERATORS
          :summary:

API
~~~

.. py:function:: node(data, name=None, trainable=False, constraint=None)
   :canonical: opto.trace.nodes.node

   .. autodoc2-docstring:: opto.trace.nodes.node

.. py:data:: NAME_SCOPES
   :canonical: opto.trace.nodes.NAME_SCOPES
   :value: []

   .. autodoc2-docstring:: opto.trace.nodes.NAME_SCOPES

.. py:class:: Graph()
   :canonical: opto.trace.nodes.Graph

   .. autodoc2-docstring:: opto.trace.nodes.Graph

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.Graph.__init__

   .. py:attribute:: TRACE
      :canonical: opto.trace.nodes.Graph.TRACE
      :value: True

      .. autodoc2-docstring:: opto.trace.nodes.Graph.TRACE

   .. py:method:: clear()
      :canonical: opto.trace.nodes.Graph.clear

      .. autodoc2-docstring:: opto.trace.nodes.Graph.clear

   .. py:method:: register(node)
      :canonical: opto.trace.nodes.Graph.register

      .. autodoc2-docstring:: opto.trace.nodes.Graph.register

   .. py:method:: get(name)
      :canonical: opto.trace.nodes.Graph.get

      .. autodoc2-docstring:: opto.trace.nodes.Graph.get

   .. py:property:: roots
      :canonical: opto.trace.nodes.Graph.roots

      .. autodoc2-docstring:: opto.trace.nodes.Graph.roots

.. py:data:: GRAPH
   :canonical: opto.trace.nodes.GRAPH
   :value: 'Graph(...)'

   .. autodoc2-docstring:: opto.trace.nodes.GRAPH

.. py:data:: USED_NODES
   :canonical: opto.trace.nodes.USED_NODES
   :value: 'list(...)'

   .. autodoc2-docstring:: opto.trace.nodes.USED_NODES

.. py:data:: T
   :canonical: opto.trace.nodes.T
   :value: 'TypeVar(...)'

   .. autodoc2-docstring:: opto.trace.nodes.T

.. py:class:: AbstractNode(value, *, name=None, trainable=False)
   :canonical: opto.trace.nodes.AbstractNode

   Bases: :py:obj:`typing.Generic`\ [\ :py:obj:`opto.trace.nodes.T`\ ]

   .. autodoc2-docstring:: opto.trace.nodes.AbstractNode

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.__init__

   .. py:property:: data
      :canonical: opto.trace.nodes.AbstractNode.data

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.data

   .. py:property:: parents
      :canonical: opto.trace.nodes.AbstractNode.parents

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.parents

   .. py:property:: children
      :canonical: opto.trace.nodes.AbstractNode.children

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.children

   .. py:property:: name
      :canonical: opto.trace.nodes.AbstractNode.name

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.name

   .. py:property:: py_name
      :canonical: opto.trace.nodes.AbstractNode.py_name

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.py_name

   .. py:property:: id
      :canonical: opto.trace.nodes.AbstractNode.id

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.id

   .. py:property:: level
      :canonical: opto.trace.nodes.AbstractNode.level

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.level

   .. py:property:: is_root
      :canonical: opto.trace.nodes.AbstractNode.is_root

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.is_root

   .. py:property:: is_leaf
      :canonical: opto.trace.nodes.AbstractNode.is_leaf

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.is_leaf

   .. py:method:: lt(other)
      :canonical: opto.trace.nodes.AbstractNode.lt

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.lt

   .. py:method:: gt(other)
      :canonical: opto.trace.nodes.AbstractNode.gt

      .. autodoc2-docstring:: opto.trace.nodes.AbstractNode.gt

.. py:data:: IDENTITY_OPERATORS
   :canonical: opto.trace.nodes.IDENTITY_OPERATORS
   :value: ('identity', 'clone')

   .. autodoc2-docstring:: opto.trace.nodes.IDENTITY_OPERATORS

.. py:function:: get_op_name(description)
   :canonical: opto.trace.nodes.get_op_name

   .. autodoc2-docstring:: opto.trace.nodes.get_op_name

.. py:class:: NodeVizStyleGuide(style='default', print_limit=100)
   :canonical: opto.trace.nodes.NodeVizStyleGuide

   .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide.__init__

   .. py:method:: get_attrs(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuide.get_attrs

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide.get_attrs

   .. py:method:: get_label(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuide.get_label

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide.get_label

   .. py:method:: get_node_shape(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuide.get_node_shape

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide.get_node_shape

   .. py:method:: get_color(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuide.get_color

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide.get_color

   .. py:method:: get_style(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuide.get_style

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuide.get_style

.. py:class:: NodeVizStyleGuideColorful(style='default', print_limit=100)
   :canonical: opto.trace.nodes.NodeVizStyleGuideColorful

   Bases: :py:obj:`opto.trace.nodes.NodeVizStyleGuide`

   .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful.__init__

   .. py:method:: get_attrs(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuideColorful.get_attrs

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful.get_attrs

   .. py:method:: get_border_color(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuideColorful.get_border_color

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful.get_border_color

   .. py:method:: get_color(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuideColorful.get_color

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful.get_color

   .. py:method:: get_style(x)
      :canonical: opto.trace.nodes.NodeVizStyleGuideColorful.get_style

      .. autodoc2-docstring:: opto.trace.nodes.NodeVizStyleGuideColorful.get_style

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

.. py:class:: ParameterNode(value, *, name=None, trainable=True, description='[ParameterNode] This is a ParameterNode in a computational graph.', constraint=None, info=None)
   :canonical: opto.trace.nodes.ParameterNode

   Bases: :py:obj:`opto.trace.nodes.Node`\ [\ :py:obj:`opto.trace.nodes.T`\ ]

.. py:class:: MessageNode(value, *, inputs: typing.Union[typing.List[opto.trace.nodes.Node], typing.Dict[str, opto.trace.nodes.Node]], description: str, constraint=None, name=None, info=None)
   :canonical: opto.trace.nodes.MessageNode

   Bases: :py:obj:`opto.trace.nodes.Node`\ [\ :py:obj:`opto.trace.nodes.T`\ ]

   .. autodoc2-docstring:: opto.trace.nodes.MessageNode

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.MessageNode.__init__

   .. py:property:: inputs
      :canonical: opto.trace.nodes.MessageNode.inputs

      .. autodoc2-docstring:: opto.trace.nodes.MessageNode.inputs

   .. py:property:: external_dependencies
      :canonical: opto.trace.nodes.MessageNode.external_dependencies

      .. autodoc2-docstring:: opto.trace.nodes.MessageNode.external_dependencies

.. py:class:: ExceptionNode(value: Exception, *, inputs: typing.Union[typing.List[opto.trace.nodes.Node], typing.Dict[str, opto.trace.nodes.Node]], description: str = '[ExceptionNode] This is node containing the error of execution.', constraint=None, name=None, info=None)
   :canonical: opto.trace.nodes.ExceptionNode

   Bases: :py:obj:`opto.trace.nodes.MessageNode`\ [\ :py:obj:`opto.trace.nodes.T`\ ]

   .. autodoc2-docstring:: opto.trace.nodes.ExceptionNode

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.nodes.ExceptionNode.__init__
