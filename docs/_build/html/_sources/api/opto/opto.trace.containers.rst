:py:mod:`opto.trace.containers`
===============================

.. py:module:: opto.trace.containers

.. autodoc2-docstring:: opto.trace.containers
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`NodeContainer <opto.trace.containers.NodeContainer>`
     - .. autodoc2-docstring:: opto.trace.containers.NodeContainer
          :summary:
   * - :py:obj:`ParameterContainer <opto.trace.containers.ParameterContainer>`
     - .. autodoc2-docstring:: opto.trace.containers.ParameterContainer
          :summary:
   * - :py:obj:`Seq <opto.trace.containers.Seq>`
     - .. autodoc2-docstring:: opto.trace.containers.Seq
          :summary:
   * - :py:obj:`Map <opto.trace.containers.Map>`
     - .. autodoc2-docstring:: opto.trace.containers.Map
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`trainable_method <opto.trace.containers.trainable_method>`
     - .. autodoc2-docstring:: opto.trace.containers.trainable_method
          :summary:

API
~~~

.. py:class:: NodeContainer
   :canonical: opto.trace.containers.NodeContainer

   .. autodoc2-docstring:: opto.trace.containers.NodeContainer

.. py:function:: trainable_method(method)
   :canonical: opto.trace.containers.trainable_method

   .. autodoc2-docstring:: opto.trace.containers.trainable_method

.. py:class:: ParameterContainer
   :canonical: opto.trace.containers.ParameterContainer

   Bases: :py:obj:`opto.trace.containers.NodeContainer`

   .. autodoc2-docstring:: opto.trace.containers.ParameterContainer

   .. py:method:: parameters()
      :canonical: opto.trace.containers.ParameterContainer.parameters

      .. autodoc2-docstring:: opto.trace.containers.ParameterContainer.parameters

   .. py:method:: parameters_dict()
      :canonical: opto.trace.containers.ParameterContainer.parameters_dict

      .. autodoc2-docstring:: opto.trace.containers.ParameterContainer.parameters_dict

.. py:class:: Seq(*args)
   :canonical: opto.trace.containers.Seq

   Bases: :py:obj:`collections.UserList`, :py:obj:`opto.trace.containers.ParameterContainer`

   .. autodoc2-docstring:: opto.trace.containers.Seq

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.containers.Seq.__init__

   .. py:method:: parameters_dict()
      :canonical: opto.trace.containers.Seq.parameters_dict

      .. autodoc2-docstring:: opto.trace.containers.Seq.parameters_dict

.. py:class:: Map(mapping)
   :canonical: opto.trace.containers.Map

   Bases: :py:obj:`collections.UserDict`, :py:obj:`opto.trace.containers.ParameterContainer`

   .. autodoc2-docstring:: opto.trace.containers.Map

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.trace.containers.Map.__init__

   .. py:method:: parameters_dict()
      :canonical: opto.trace.containers.Map.parameters_dict

      .. autodoc2-docstring:: opto.trace.containers.Map.parameters_dict
