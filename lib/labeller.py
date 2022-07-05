__all__ = [
    'LabelClass',
]

class LabelClass:
    def __init__(self, df):
        self.labels = (df['label']
                       .dropna()
                       .unique())

    def __iter__(self):
        yield from enumerate(sorted(self.labels))

    def c2l(self):
        yield from self

    def l2c(self):
        yield from map(reversed, self)
