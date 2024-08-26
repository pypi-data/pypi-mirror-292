from dataclasses import dataclass

import yaml
import yaml.nodes

@dataclass
class Reference:
    path: list

class GitLabYamlLoader(yaml.SafeLoader):
    def reference(self, node):
        path = self.construct_sequence(node)
        return Reference(path)

GitLabYamlLoader.add_constructor(None, GitLabYamlLoader.reference)
