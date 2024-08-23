.. _method-characterization:

Characterizing quadrature methods
---------------------------------

Various approaches exist to assess the mathematical and numerical properties of quadrature methods. For example, a priori estimates, such as the Euler-MacLaurin formula :cite:`Stoer2002`, help determine how the quadrature error scales with the number of sample points. Another figure of merit is the distribution of the sample points over the domain of integration, measured by the covering radius and related metrics from the theory of covering codes :cite:`Hifi2009,Conway2010`.
Some quadrature methods exactly integrate polynomials up to a certain degree. This is refereed to as the *degree of exactness*, sometimes simply called the "order" of the method, and has been used to define a measure of efficiency :cite:`McLaren1963,Blech2024`.

Below, a small selection of these concepts is described in more detail.


.. _degree:

Degree of exactness
^^^^^^^^^^^^^^^^^^^

Consider a quadrature method on the domain :math:`\mathcal{D}`.
Let :math:`{p_l(x)}_{l=0}^{\infty}` be an orthogonal basis

.. math::

   f(x) = \sum_{l} f_l \, p_l(x)

A quadrature's *degree of exactness* is the maximum :math:`l`, for which quadrature yields the e

.. todo: finish


.. _efficiency:

McLaren efficiency
^^^^^^^^^^^^^^^^^^
