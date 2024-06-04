class DummyFemtet:

    def __init__(self):
        self.hWnd = 12345
        self._parameters = dict(
            pi=3.141592,
            c_pi=3.141592,
            prm1=1,
            prm2=2,
            prm3='prm1 + prm2',
            prm4=4,
        )

    def GetVariableNames(self) -> 'List[str]':
        return list(self._parameters.keys())

    def GetVariableExpression(self, var_name) -> 'str or int':
        return self._parameters[var_name]

    def GetVariableValue(self, var_name) -> 'float':
        if var_name == 'prm3':
            return 3
        else:
            return float(self._parameters[var_name])
