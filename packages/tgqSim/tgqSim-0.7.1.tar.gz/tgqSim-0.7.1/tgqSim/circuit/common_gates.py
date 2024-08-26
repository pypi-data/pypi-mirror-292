"""
-*- coding: utf-8 -*-
@Author : Cui Jinghao
@Time : 2024/6/28 15:49
@Function: common_gates
@Contact: cuijinghao@tgqs.net
"""
from typing import Union
from abc import abstractmethod

# global parameters
BASE_SINGLE_GATE = ['h', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'u3', 's', 'sdg', 't', 'tdg', "damp_I", "pd", "ad"]
BASE_DOUBLE_GATE = ['cx', 'swap', 'iswap', 'cz', 'cp', 'rxx', 'ryy', 'rzz', 'syc']
BASE_TRIPLE_GATE = ['ccx', 'cswap']
CONTROLLED_GATE = ['cx', 'cz', 'cp', 'ccx', 'cswap']
ROTATION_GATE = ['rxx', 'ryy', 'rzz']
MEASURE = ['measure']
BASE_SINGLE_GATE_MAP = {'h': '_H', 'x': '_X', 'y': '_Y', 'z': '_Z',
                        'rx': '_RX', 'ry': '_RY', 'rz': '_RZ',
                        'u3': '_U3',
                        's': '_S', 'sdg': '_SDG', 't': '_T', 'tdg': '_TDG'}
BASE_DOUBLE_GATE_MAP = {'cx': '_CX', 'swap': '_SWAP', 'iswap': '_ISWAP',
                        'cz': '_CZ', 'cp': '_CP', 'rxx': '_RXX', 'ryy': '_RYY', 'rzz': '_RZZ', 'syc': '_SYC'}

BASE_TRIPLE_GATE_MAP = {'cswap': '_CSWAP', 'ccx': '_CCX'}

MEASURE_MAP = {'measure': '_Measure'}


# will implement more gates classes later
# will further abstract classes
class _CommonGate:
    @abstractmethod
    def gate(self, *args, **kwargs):
        pass


CommonGate = _CommonGate()


class _Measure(_CommonGate):
    def __init__(self, qbit: Union[list, int] = None, name: str = 'measure', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ('Measure-z',)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        self.display_name = tuple(['Measure-z']*len(self.qbit))
        return self


measure = _Measure()


class _I(_CommonGate):
    """
    eye matrix
    """
    def __init__(self, qbit: int = 0, name='I', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("I", )

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


I = _I()


class _Pauli(_CommonGate):
    def __init__(self):
        pass

    def __call__(self):
        return

    def gate(self):
        pass


class _X(_Pauli):
    # todo: add attribute noise
    def __init__(self, qbit: int = 0, name='x', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("X", )


    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


x = _X()


class _Y(_Pauli):
    def __init__(self, qbit=0, name='y', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("Y",)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


y = _Y()


class _Z(_Pauli):
    def __init__(self, qbit=0, name='z', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("Z",)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


z = _Z()


class _RX(_CommonGate):
    def __init__(self, qbit=0, name='rx', theta=0):
        self.qbit = qbit
        self.name = name
        self.theta = float(theta)
        self.display_name = (f"Ry({round(self.theta, 2)})",)

    def __call__(self, qbit, theta):
        return self.gate(qbit, theta)

    def gate(self, qbit, theta):
        self.qbit = qbit
        self.theta = float(theta)
        self.display_name = (f"Ry({round(self.theta, 2)})",)
        return self


rx = _RX()


class _RY(_CommonGate):
    def __init__(self, qbit=0, name='ry', theta=0):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.theta = float(theta)
        self.display_name = (f"Ry({round(self.theta, 2)})",)

    def __call__(self, qbit, theta):
        return self.gate(qbit, theta)

    def gate(self, qbit, theta):
        self.qbit = qbit
        self.theta = float(theta)
        self.display_name = (f"Ry({round(self.theta, 2)})",)
        return self


ry = _RY()


class _RZ(_CommonGate):
    def __init__(self, qbit=0, name='rz', theta=0):
        self.qbit = qbit
        self.name = name
        self.theta = float(theta)
        self.display_name = (f"Rz({round(self.theta, 2)})",)

    def __call__(self, qbit, theta):
        return self.gate(qbit, theta)

    def gate(self, qbit, theta):
        self.qbit = qbit
        self.theta = float(theta)
        self.display_name = (f"Rz({round(self.theta, 2)})",)
        return self


rz = _RZ()


class _U3(_CommonGate):
    def __init__(self, qbit=0, name='u3', *theta):
        self.qbit = qbit
        self.name = name
        self.theta = theta

    def __call__(self, qbit, *theta):

        # print('len of theta tuple is {}, tuple is {}'.format(len(theta), theta))
        if not theta or (theta and len(theta) != 3):
            raise Exception('U3 gate requires 3 parameters, please check!')
        # print('theta before calling gate is {}'.format(theta))
        return self.gate(qbit, theta[0], theta[1], theta[2])

    def gate(self, qbit, *theta):
        # print('theta after initialization is {}'.format(theta))
        self.qbit = qbit
        self.theta = theta
        return self


u3 = _U3()


# class

class _H(_CommonGate):
    def __init__(self, qbit=0, name='h', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ('H',)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


h = _H()


class _S(_CommonGate):
    def __init__(self, qbit=0, name='s', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("S",)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


s = _S()


class _SDG(_CommonGate):
    def __init__(self, qbit=0, name='sdg', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("SDG",)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


sdg = _SDG()


class _T(_CommonGate):
    def __init__(self, qbit=0, name='t', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("T",)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


t = _T()


class _TDG(_CommonGate):
    def __init__(self, qbit=0, name='tdg', theta=None):
        self.qbit = qbit
        self.name = name
        self.theta = theta
        self.display_name = ("TDG",)

    def __call__(self, qbit):
        return self.gate(qbit)

    def gate(self, qbit):
        self.qbit = qbit
        return self


tdg = _TDG()


# double gates ['cx', 'swap', 'iswap', 'cz', 'cp', 'rxx', 'ryy', 'rzz', 'syc']
class _CX(_CommonGate):
    """
    @explain: CNOT gate
    @params: by default, qbit0 is the controll bit
    @return: CNOT gate
    """
    # by default, qbit0 is the controll bit
    def __init__(self, qbit0=0, qbit1=1, name='cx', theta=None):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ("@", "X")

    def __call__(self, qbit0, qbit1):
        return self.gate(qbit0, qbit1)

    def gate(self, qbit0, qbit1):
        self.qbit = [qbit0, qbit1]
        return self


cx = _CX()


class _CZ(_CommonGate):
    def __init__(self, qbit0=0, qbit1=1, name='cz', theta=None):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ("@", "@")

    def __call__(self, qbit0, qbit1, theta=None):
        return self.gate(qbit0, qbit1, theta)

    def gate(self, qbit0, qbit1, theta=None):
        self.qbit = [qbit0, qbit1]
        return self


cz = _CZ()


class _CP(_CommonGate):
    """
    @params: first control, second target, third theta
    @returns: cphase gate
    @explanation: cphase gate

    """
    def __init__(self, qbit0=0, qbit1=1, name='cp', theta=0):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = float(theta)
        self.display_name = ("@", f"@^{round(self.theta, 2)}")

    def __call__(self, qbit0, qbit1, theta):
        return self.gate(qbit0, qbit1, theta)

    def gate(self, qbit0, qbit1, theta):
        self.qbit = [qbit0, qbit1]
        self.theta = float(theta)
        self.display_name = ("@", f"@^{round(self.theta, 2)}")
        return self


cp = _CP()


class _SWAP(_CommonGate):
    def __init__(self, qbit0=0, qbit1=1, name='swap', theta=None):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ("x", "x")

    def __call__(self, qbit0, qbit1):
        return self.gate(qbit0, qbit1)

    def gate(self, qbit0, qbit1):
        self.qbit = [qbit0, qbit1]
        return self


swap = _SWAP()


class _ISWAP(_CommonGate):
    def __init__(self, qbit0: int = 0, qbit1: int = 1, name='iswap', theta=None):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ("iSwap", "iSwap")

    def __call__(self, qbit0, qbit1):
        return self.gate(qbit0, qbit1)

    def gate(self, qbit0, qbit1):
        self.qbit = [qbit0, qbit1]
        return self


iswap = _ISWAP()


class _RXX(_CommonGate):
    def __init__(self, qbit0=0, qbit1=1, name='rxx', theta=0):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = float(theta)
        self.display_name = (f"Rxx({round(self.theta, 2)})", f"Rxx({round(self.theta, 2)})")

    def __call__(self, qbit0, qbit1):
        return self.gate(qbit0, qbit1)

    def gate(self, qbit0, qbit1):
        self.qbit = [qbit0, qbit1]
        self.display_name = (f"Rxx({round(self.theta, 2)})", f"Rxx({round(self.theta, 2)})")
        return self


rxx = _RXX()


class _RYY(_CommonGate):
    def __init__(self, qbit0=0, qbit1=1, name='ryy', theta=0):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = float(theta)
        self.display_name = (f"Ryy({round(theta, 2)})", f"Ryy({round(theta, 2)})")

    def __call__(self, qbit0, qbit1, theta):
        return self.gate(qbit0, qbit1, theta)

    def gate(self, qbit0, qbit1, theta):
        self.qbit = [qbit0, qbit1]
        self.theta = float(theta)
        self.display_name = (f"Ryy({round(self.theta, 2)})", f"Ryy({round(self.theta, 2)})")
        return self


ryy = _RYY()


class _RZZ(_CommonGate):
    """
    @params: first two params are qbit positions, third param is theta;
    @return: rzz gate
    """
    def __init__(self, qbit0=0, qbit1=1, name='rzz', theta=0):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = float(theta)
        self.display_name = (f"Rzz({round(self.theta, 2)})", f"Rzz({round(self.theta, 2)})")

    def __call__(self, qbit0, qbit1, theta):
        return self.gate(qbit0, qbit1, theta)

    def gate(self, qbit0, qbit1, theta):
        self.qbit = [qbit0, qbit1]
        self.theta = float(theta)
        self.display_name = (f"Rzz({round(self.theta, 2)})", f"Rzz({round(self.theta, 2)})")
        return self


rzz = _RZZ()


class _SYC(_CommonGate):
    def __init__(self, qbit0: int = 0, qbit1: int = 1, name='syc', theta=None):
        self.qbit0 = qbit0
        self.qbit1 = qbit1
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ('SYC',)

    def __call__(self, qbit0, qbit1):
        return self.gate(qbit0, qbit1)

    def gate(self, qbit0, qbit1):
        self.qbit = [qbit0, qbit1]
        return self


syc = _SYC()


class _CCX(_CommonGate):
    def __init__(self, control_qbit: list = None, target_qbit: Union[list, int] = None, name='ccx', theta=None):
        self.control_qbit = control_qbit
        self.target_qbit = [target_qbit]
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ("@", "@", "X")

    def __call__(self, control_qbit, target_qbit):
        return self.gate(control_qbit, target_qbit)

    def gate(self, control_qbit, target_qbit):
        control = control_qbit if isinstance(control_qbit, list) else [control_qbit]
        target = target_qbit if isinstance(target_qbit, list) else [target_qbit]
        self.qbit = control + target
        return self


ccx = _CCX()


class _CSWAP(_CommonGate):
    def __init__(self, control_qbit: list = None, target_qbit: Union[list, int] = None, name='cswap', theta=None):
        self.control_qbit = [control_qbit]
        self.target_qbit = target_qbit
        self.qbit = None
        self.name = name
        self.theta = theta
        self.display_name = ("@", "x", "x")

    def __call__(self, control_qbit, target_qbit):
        return self.gate(control_qbit, target_qbit)

    def gate(self, control_qbit, target_qbit):
        control = control_qbit if isinstance(control_qbit, list) else [control_qbit]
        target = target_qbit if isinstance(target_qbit, list) else [target_qbit]
        self.qbit = control + target
        return self


cswap = _CSWAP()



