:py:mod:`opto.trace.modules`
============================

.. py:module:: opto.trace.modules

.. autodoc2-docstring:: opto.trace.modules
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Module <opto.trace.modules.Module>`
     - .. autodoc2-docstring:: opto.trace.modules.Module
          :summary:

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`model <opto.trace.modules.model>`
     - .. autodoc2-docstring:: opto.trace.modules.model
          :summary:

API
~~~

.. py:function:: model(cls)
   :canonical: opto.trace.modules.model

   .. autodoc2-docstring:: opto.trace.modules.model

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
