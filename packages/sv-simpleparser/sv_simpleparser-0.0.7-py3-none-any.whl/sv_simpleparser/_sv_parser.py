import pathlib
from ._hdl import SystemVerilogLexer
from dataclasses import dataclass
from ._lexer_tokens import Module

__all__ = ['parse_sv']


@dataclass
class Port:
    '''Class used to store data about a port'''
    direction: str
    ptype: str = None
    name: str = None
    width: str = None
    comment: list = None


@dataclass
class Param:
    '''Class used to store data about a port'''
    ptype: str = None
    name: str = None
    width: str = None
    comment: list = None


@dataclass
class PortDeclaration:
    '''Class used to store data about a port'''
    direction: str
    ptype: str = None
    name: list = None
    width: str = None
    comment: list = None

    def proc_tokens(self, token, string):
        '''Processes Module.Port tokens and extract data'''
        if token is Module.Port.PortDirection:
            self.direction = string
        elif token is Module.Port.PortType:
            self.ptype = string
        elif token is Module.Port.PortName:
            if self.name is None:
                self.name = [string]
            else:
                self.name.append(string)
        elif token is Module.Port.PortWidth:
            self.width = string
        elif token is Module.Port.Comment:
            if self.comment is None:
                self.comment = [string]
            else:
                self.comment.append(string)


@dataclass
class ParamDeclaration:
    ptype: str = None
    name: list = None
    width: str = None
    comment: list = None

    def proc_tokens(self, token, string):
        '''Processes Module.Param tokens and extract data'''
        if token is Module.Param.ParamType:
            self.ptype = string
        elif token is Module.Param.ParamName:
            if self.name is None:
                self.name = [string]
            else:
                self.name.append(string)
        elif token is Module.Param.ParamWidth:
            self.width = string
        elif token is Module.Param.Comment:
            if self.comment is None:
                self.comment = [string]
            else:
                self.comment.append(string)


class SvModule:
    def __init__(self):
        self.port_decl = []
        self.param_decl = []
        self.instances = []
        self.name = None
        self.port_lst = []
        self.param_lst = []

    def _gen_port_lst(self):
        for decl in self.port_decl:
            for name in decl.name:
                port = Port(name=name, direction=decl.direction, ptype=decl.ptype,
                            width=decl.width, comment=decl.comment)
                self.port_lst.append(port)

    def _gen_param_lst(self):
        for decl in self.param_decl:
            for name in decl.name:
                param = Param(name=name, ptype=decl.ptype, width=decl.width,
                              comment=decl.comment)
                self.param_lst.append(param)

    def proc_tokens(self, token, string):
        # create a new port declaration object if input/output keywords are found
        if token[:2] == ('Module', 'Port'):
            if token is Module.Port.PortDirection:
                self.port_decl.append(PortDeclaration(direction=string))
            else:
                self.port_decl[-1].proc_tokens(token, string)
        # create a new parameter declaration object if parameter keywords are found
        elif token[:2] == ('Module', 'Param'):
            if token is Module.Param:
                self.param_decl.append(ParamDeclaration())
            else:
                self.param_decl[-1].proc_tokens(token, string)
        elif token[:2] == ('Module', 'ModuleName'):
            self.name = string


def compare_tuples(x, token, strings=None):
    """
    Compares a tuple `x` with a given token and an optional list or tuple of strings.

    Parameters:
    - x: tuple to compare (expected to be of the form (Token, string)).
    - token: token to compare against the first element of the tuple.
    - strings: (optional) list or tuple of strings to compare against the second element of the tuple.

    Returns:
    - True if both token and any of the strings match when strings are provided.
    - True if only the token matches when strings are not provided.
    - False otherwise.
    """
    if strings is None:
        # Check only token
        return x[0] == token
    else:
        # Check both token and any of the strings
        return x[0] == token and x[1] in strings


def parse_sv(file_path: pathlib.Path):
    '''Parse SystemVerilog

    Parses a SystemVerilog file and returns a list of objects of SvModule class

    Parameters
    ----------

    file_path: Union[str, pathlib.Path]
        Path to the SystemVerilog file.
    '''

    if not isinstance(file_path, pathlib.Path):
        file_path = pathlib.Path(file_path)

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file at {file_path} does not exist.")

    with file_path.open(mode='r') as fid:
        file_content = fid.read()

    lexer = SystemVerilogLexer()
    module_lst = []
    for token, string in lexer.get_tokens(file_content):

        # New module was found
        if token == Module.ModuleStart:
            module_lst.append(SvModule())
        elif 'Module' in token[:]:
            module_lst[-1].proc_tokens(token, string)

    for mod in module_lst:
        mod._gen_port_lst()
        mod._gen_param_lst()

    return module_lst


if __name__ == '__main__':
    import pprint

    file_path = pathlib.Path('../tests/svfiles_examples/adder.sv')

    mod_lst = parse_sv(file_path)

    for mod in mod_lst:
        print(f'Module name: {mod.name}')
        pprint.pprint(mod.port_lst)
        pprint.pprint(mod.param_lst)
