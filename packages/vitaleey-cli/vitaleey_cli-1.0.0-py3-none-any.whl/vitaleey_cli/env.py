class EnvironmentNames:
    """
    Environment names and groups for the CLI
    """

    DEVELOPMENT = ["dev", "development"]
    ACCEPTANCE = ["acc", "acceptance"]
    PRODUCTION = ["prd", "prod", "production"]

    def groups(self):
        return {
            "development": self.DEVELOPMENT,
            "acceptance": self.ACCEPTANCE,
            "production": self.PRODUCTION,
        }

    def get_group(self, name):
        for group, names in self.groups().items():
            if name in names:
                return group

    def get_group_options(self, name):
        """
        Get the group options for a given environment name.
        The option name will be used to select the environment.

        Group: development
            Options: ['dev', 'development']

        Group: acceptance
            Options: ['acc', 'acceptance']

        Group: production
            Options: ['prd', 'prod', 'production']
        """

        for group, names in self.groups().items():
            if name in names:
                return names

    def names(self):
        names = []
        for group in self.groups().values():
            names.extend(group)
        return names


environment_names = EnvironmentNames()

ENVIRONMENTS = environment_names.names()
