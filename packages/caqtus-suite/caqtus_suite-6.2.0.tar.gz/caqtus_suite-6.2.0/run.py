from caqtus.extension import Experiment
from caqtus.session.sql import PostgreSQLConfig

exp = Experiment()

exp.configure_storage(PostgreSQLConfig.from_file("config.yaml"))

exp.setup_default_extensions()

if __name__ == "__main__":

    exp.launch_condetrol()
