:py:mod:`opto.trace.bundle`
===========================

.. py:module:: opto.trace.bundle

.. autodoc2-docstring:: opto.trace.bundle
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`trace_nodes <opto.trace.bundle.trace_nodes>`
     - .. autodoc2-docstring:: opto.trace.bundle.trace_nodes
          :summary:
   * - :py:obj:`FunModule <opto.trace.bundle.FunModule>`
     - .. autodoc2-docstring:: opto.trace.bundle.FunModule
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`bundle <opto.trace.bundle.bundle>`
     - .. autodoc2-docstring:: opto.trace.bundle.bundle
          :summary:
   * - :py:obj:`to_data <opto.trace.bundle.to_data>`
     - .. autodoc2-docstring:: opto.trace.bundle.to_data
          :summary:
   * - :py:obj:`wrap_node <opto.trace.bundle.wrap_node>`
     - .. autodoc2-docstring:: opto.trace.bundle.wrap_node
          :summary:
   * - :py:obj:`detach_inputs <opto.trace.bundle.detach_inputs>`
     - .. autodoc2-docstring:: opto.trace.bundle.detach_inputs
          :summary:
   * - :py:obj:`update_local <opto.trace.bundle.update_local>`
     - .. autodoc2-docstring:: opto.trace.bundle.update_local
          :summary:

API
~~~

.. py:function:: bundle(description=None, traceable_code=False, _process_inputs=True, trainable=False, catch_execution_error=True, allow_external_dependencies=False, overwrite_python_recursion=True)
   :canonical: opto.trace.bundle.bundle

   .. autodoc2-docstring:: opto.trace.bundle.bundle

.. py:class:: trace_nodes
   :canonical: opto.trace.bundle.trace_nodes

   .. autodoc2-docstring:: opto.trace.bundle.trace_nodes

.. py:class:: FunModule(fun: typing.Callable, description: str = None, traceable_code: bool = False, _process_inputs: bool = True, trainable=False, catch_execution_error=True, allow_external_dependencies=False, overwrite_python_recursion=True, _ldict=None)
   :canonical: opto.trace.bundle.FunModule

   Bases: :py:obj:`opto.trace.modules.Module`

   .. autodoc2-docstring:: opto.trace.bundle.FunModule

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.bundle.FunModule.__init__

   .. py:property:: trainable
      :canonical: opto.trace.bundle.FunModule.trainable

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.trainable

   .. py:property:: fun
      :canonical: opto.trace.bundle.FunModule.fun

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.fun

   .. py:property:: name
      :canonical: opto.trace.bundle.FunModule.name

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.name

   .. py:method:: forward(*args, **kwargs)
      :canonical: opto.trace.bundle.FunModule.forward

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.forward

   .. py:method:: wrap(output: typing.Any, inputs: typing.Union[typing.List[opto.trace.nodes.Node], typing.Dict[str, opto.trace.nodes.Node]], external_dependencies: typing.List[opto.trace.nodes.Node])
      :canonical: opto.trace.bundle.FunModule.wrap

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.wrap

   .. py:method:: is_valid_output(output)
      :canonical: opto.trace.bundle.FunModule.is_valid_output
      :staticmethod:

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.is_valid_output

   .. py:method:: detach()
      :canonical: opto.trace.bundle.FunModule.detach

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.detach

   .. py:method:: generate_comment(code: str, comment: str, comment_line_number: int, base_line_number: int = 0)
      :canonical: opto.trace.bundle.FunModule.generate_comment

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.generate_comment

   .. py:method:: get_source(obj: typing.Any)
      :canonical: opto.trace.bundle.FunModule.get_source

      .. autodoc2-docstring:: opto.trace.bundle.FunModule.get_source

.. py:function:: to_data(obj)
   :canonical: opto.trace.bundle.to_data

   .. autodoc2-docstring:: opto.trace.bundle.to_data

.. py:function:: wrap_node(obj)
   :canonical: opto.trace.bundle.wrap_node

   .. autodoc2-docstring:: opto.trace.bundle.wrap_node

.. py:function:: detach_inputs(obj)
   :canonical: opto.trace.bundle.detach_inputs

   .. autodoc2-docstring:: opto.trace.bundle.detach_inputs

.. py:function:: update_local(frame, name, value)
   :canonical: opto.trace.bundle.update_local

   .. autodoc2-docstring:: opto.trace.bundle.update_local
