import os
from importlib import resources

from pkgs.argument_parser import CachedParser
from uncountable.integration.db.connect import create_db_engine
from uncountable.integration.server import IntegrationServer
from uncountable.types.job_definition_t import ProfileDefinition

profile_parser = CachedParser(ProfileDefinition)


def main(blocking: bool) -> None:
    profiles_module = os.environ["UNC_PROFILES_MODULE"]
    with IntegrationServer(create_db_engine()) as server:
        profiles = [
            entry
            for entry in resources.files(profiles_module).iterdir()
            if entry.is_dir()
        ]
        for profile_file in profiles:
            profile_name = profile_file.name
            try:
                profile = profile_parser.parse_yaml_resource(
                    package=".".join([profiles_module, profile_name]),
                    resource="profile.yaml",
                )
            except FileNotFoundError as e:
                print(f"WARN: profile.yaml not found for {profile_name}", e)
                continue
            server.register_profile(
                profile_name=profile_name,
                base_url=profile.base_url,
                auth_retrieval=profile.auth_retrieval,
                jobs=profile.jobs,
                client_options=profile.client_options,
            )

        if blocking:
            server.serve_forever()


main(__name__ == "__main__")
