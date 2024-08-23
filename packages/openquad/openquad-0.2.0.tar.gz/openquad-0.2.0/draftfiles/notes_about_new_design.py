

class AtomicS2Quadrature(AtomicQuadrature):

    def __init__(self, method, options):
        method_id = self.get_method_id(method, options)
        x, w = self.points_weights(method_id)

    def points_weights(self, method_id):
        points, weights = self.load_points_weights(method_id)
        #weights = weights * self.volume # No: weights are normalized already
        return points, weights

    method_id = type, source, size, [degree, suffix]



S2([
    ('gauss', degree=5),
])
S2([
    ('gauss-LebedevLaikov', degree=5),
])
S2([
    ('gauss', degree=5, options={'source':'lebedevlaikov'}),
])
S2([
    ('gauss', degree=5, source='lebedevlaikov'),
])
S2([
    ('design-womersley', degree=5, options={"symmetric":True}),
])
S2([
    ('design', degree=5, options={"symmetric":True}),
])
S2([
    ('design', degree=5, options={"source":"womersley", "symmetric":True}),
])
S2([
    ('design', degree=5, source="womersley", symmetric=True),
])

AtomicS2Quadrature('gauss', degree=5, source='lebedevlaikov')
