from typing import Callable
from mypy.nodes import ArgKind
from mypy.plugin import FunctionContext, Plugin
from mypy.types import AnyType, CallableType, Type, TypeOfAny
from mypy.errorcodes import VALID_TYPE


class AllowExtraKwargsPlugin(Plugin):
    FUNCTION_NAME = "allow_extra_kwargs"

    def get_function_hook(
        self, fullname: str
    ) -> Callable[[FunctionContext], Type] | None:
        if fullname.endswith(self.FUNCTION_NAME):
            return self.allow_extra_kwargs_callback
        return None

    def allow_extra_kwargs_callback(self, context: FunctionContext) -> Type:
        if isinstance(context.default_return_type, CallableType):
            func_type = context.default_return_type

            new_arg_kinds = list(func_type.arg_kinds)
            new_arg_names = list(func_type.arg_names)
            new_arg_types = list(func_type.arg_types)

            kwargs_index = next(
                (
                    i
                    for i, kind in enumerate(new_arg_kinds)
                    if kind == ArgKind.ARG_STAR2
                ),
                None,
            )

            if kwargs_index is not None:
                kwargs_type = new_arg_types[kwargs_index]

                if not isinstance(kwargs_type, AnyType):
                    context.api.fail(
                        f"Cannot use {self.FUNCTION_NAME} with a function that already has a typed **kwargs parameter "
                        "which is not an unpacked TypedDict",
                        context.context,
                        code=VALID_TYPE,
                    )
                    return context.default_return_type

                new_arg_types[kwargs_index] = AnyType(TypeOfAny.explicit)
            else:
                new_arg_kinds.append(ArgKind.ARG_STAR2)
                new_arg_names.append("kwargs")
                new_arg_types.append(AnyType(TypeOfAny.explicit))

            return func_type.copy_modified(
                arg_kinds=new_arg_kinds,
                arg_names=new_arg_names,
                arg_types=new_arg_types,
            )
        return context.default_return_type


def plugin(version: str) -> type[Plugin]:
    return AllowExtraKwargsPlugin
