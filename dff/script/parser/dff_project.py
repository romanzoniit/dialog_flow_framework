import typing as tp
from pathlib import Path
import logging

from .base_parser_object import BaseParserObject, cached_property, Expression, Assignment, Call
from .namespace import Namespace
from .exceptions import ScriptValidationError
from dff.core.engine.core.actor import Actor


logger = logging.getLogger(__name__)


ScriptInitializers = {
    "dff.core.engine.core.Actor": Actor.__init__.__wrapped__.__code__.co_varnames[1:],
    "dff.core.engine.core.actor.Actor": Actor.__init__.__wrapped__.__code__.co_varnames[1:],
}


class DFFProject(BaseParserObject):
    def __init__(self, namespaces: tp.List['Namespace']):
        super().__init__()
        for namespace in namespaces:
            self.add_child(namespace, namespace.name)

    @cached_property
    def actor_call(self) -> Call:
        call = None
        for namespace in self.children.values():
            for statement in namespace.children.values():
                if isinstance(statement, Assignment):
                    value = statement.children["value"]
                    if isinstance(value, Call):
                        func = value.resolve_path(("func", ))
                        func_name = str(func.resolve_name)
                        if func_name in ScriptInitializers.keys():
                            if call is None:
                                call = value
                            else:
                                raise ScriptValidationError(f"Found two Actor calls\nFirst: {str(call)}\nSecond:{str(value)}")
        if call is not None:
            return call
        raise ScriptValidationError("Actor call is not found")

    @cached_property
    def script(self) -> tp.Tuple[Expression, Expression, tp.Optional[Expression]]:
        call = self.actor_call
        args = {}
        func = call.resolve_path(("func", ))
        func_name = str(func.resolve_name)
        for index, arg in enumerate(ScriptInitializers[func_name]):
            args[arg] = call.children.get("arg_" + str(index)) or call.children.get("keyword_" + arg)
        if args["script"] is None:
            raise ScriptValidationError(f"Actor argument `script` is not found: {str(call)}")
        if args["start_label"] is None:
            raise ScriptValidationError(f"Actor argument `start_label` is not found: {str(call)}")
        return args["script"], args["start_label"], args["fallback_label"]

    # @cached_property
    # def resolve_script -> tp.Tuple[dict, tp.List[BaseParserObject]]:
    #     """
    #
    #     :return: Resolved script and a list of all the objects necessary to resolve the script
    #     """
    #     for

    def __getitem__(self, item: tp.Union[tp.List[str], str]):
        if isinstance(item, str):
            return self.children[item]
        elif isinstance(item, list):
            if item[-1] == "__init__":
                return self.children[".".join(item)]
            namespace = self.children.get(".".join(item))
            if namespace is None:
                return self.children[".".join(item) + ".__init__"]
            return namespace
        raise TypeError(f"{type(item)}")

    @cached_property
    def path(self) -> tp.Tuple[str, ...]:
        return ()

    @cached_property
    def namespace(self) -> 'Namespace':
        raise RuntimeError(f"DFFProject does not have a `namespace` attribute\n{repr(self)}")

    @cached_property
    def dff_project(self) -> 'DFFProject':
        return self

    def __str__(self) -> str:
        return "\n".join(map(str, self.children.values()))

    def __repr__(self) -> str:
        return f"DFFProject({'; '.join(map(repr, self.children.values()))})"

    @classmethod
    def from_ast(cls, node, **kwargs):
        raise NotImplementedError()

    @classmethod
    def from_python(cls, project_root_dir: Path, entry_point: Path):
        namespaces = {}
        if not project_root_dir.exists():
            raise RuntimeError(f"Path does not exist: {project_root_dir}")

        def _process_file(file: Path):
            if not file.exists():
                raise RuntimeError(f"File {file} does not exist in {project_root_dir}")
            namespace = Namespace.from_file(project_root_dir, file)
            namespaces[namespace.name] = namespace

            for imported_file in namespace.get_imports():
                if ".".join(imported_file) not in namespaces.keys():
                    path = project_root_dir.joinpath(*imported_file).with_suffix(".py")
                    if path.exists():
                        _process_file(path)

        _process_file(entry_point)
        return cls(list(namespaces.values()))
