from yaml import Node, SafeLoader
import re
import os

ENV_TAG = '!ENV'
ENV_PATTERN = re.compile(
    '\$([^\{\}]+|\{[^\{\}]+\})'
)  # accept either $VAR or ${VAR}


class EnvLoader(SafeLoader):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # consider each ENV_PATTERN match to be tagged with ENV_TAG
        self.add_implicit_resolver(ENV_TAG, ENV_PATTERN, None)

        # construct each node with ENV_TAG according to env_constructor
        self.add_constructor(ENV_TAG, self.env_constructor)

    # clumsy definition but I wanted to avoid calling `add_constructor` outside of __init__
    def env_constructor(self, loader, node: Node):
        return os.path.expandvars(node.value)
