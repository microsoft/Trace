:py:mod:`opto.utils.llm`
========================

.. py:module:: opto.utils.llm

.. autodoc2-docstring:: opto.utils.llm
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`AbstractModel <opto.utils.llm.AbstractModel>`
     - .. autodoc2-docstring:: opto.utils.llm.AbstractModel
          :summary:
   * - :py:obj:`AutoGenLLM <opto.utils.llm.AutoGenLLM>`
     - .. autodoc2-docstring:: opto.utils.llm.AutoGenLLM
          :summary:

API
~~~

.. py:class:: AbstractModel(factory: typing.Callable, reset_freq: typing.Union[int, None] = None)
   :canonical: opto.utils.llm.AbstractModel

   .. autodoc2-docstring:: opto.utils.llm.AbstractModel

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.utils.llm.AbstractModel.__init__

   .. py:property:: model
      :canonical: opto.utils.llm.AbstractModel.model

      .. autodoc2-docstring:: opto.utils.llm.AbstractModel.model

.. py:class:: AutoGenLLM(config_list: typing.List = None, filter_dict: typing.Dict = None, reset_freq: typing.Union[int, None] = None)
   :canonical: opto.utils.llm.AutoGenLLM

   Bases: :py:obj:`opto.utils.llm.AbstractModel`

   .. autodoc2-docstring:: opto.utils.llm.AutoGenLLM

   .. rubric:: Initialization

   .. autodoc2-docstring:: opto.utils.llm.AutoGenLLM.__init__

   .. py:property:: model
      :canonical: opto.utils.llm.AutoGenLLM.model

      .. autodoc2-docstring:: opto.utils.llm.AutoGenLLM.model

   .. py:method:: create(**config: typing.Any) -> autogen.ModelClient.ModelClientResponseProtocol
      :canonical: opto.utils.llm.AutoGenLLM.create

      .. autodoc2-docstring:: opto.utils.llm.AutoGenLLM.create
