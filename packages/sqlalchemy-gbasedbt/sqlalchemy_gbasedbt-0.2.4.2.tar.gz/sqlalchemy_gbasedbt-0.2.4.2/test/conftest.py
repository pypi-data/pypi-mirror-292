from sqlalchemy.dialects import registry

registry.register("gbasedbt", "sqlalchemy_gbasedbt.dbtdb", "GBasedbtDialect")

from sqlalchemy.testing.plugin.pytestplugin import *
