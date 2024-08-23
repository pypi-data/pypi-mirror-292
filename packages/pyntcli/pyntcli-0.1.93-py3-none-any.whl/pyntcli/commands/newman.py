import argparse
import time
import os
from functools import partial

from pyntcli.pynt_docker import pynt_container
from pyntcli.commands import sub_command, util
from pyntcli.ui import ui_thread
from pyntcli.ui.progress import PyntProgress

PYNT_CONTAINER_INTERNAL_PORT = "5001"


def newman_usage():
    return (
        ui_thread.PrinterText(
            "Integration with newman, run scan using postman collection from the CLI"
        )
        .with_line("")
        .with_line("Usage:", style=ui_thread.PrinterText.HEADER)
        .with_line("\tpynt newman [OPTIONS]")
        .with_line("")
        .with_line("Options:", style=ui_thread.PrinterText.HEADER)
        .with_line("\t--collection - Postman collection file name")
        .with_line("\t--environment - Postman environment file name")
        .with_line("\t--reporters Output results to json")
        .with_line(
            "\t--host-ca - Path to the CA file in PEM format to enable SSL certificate verification for pynt when running through a VPN."
        )
        .with_line(
            "\t--application-id - Attach the scan to an application, you can find the ID in your applications area at app.pynt.io"
        )
        .with_line("\t--severity-level - 'all', 'medium', 'high', 'critical', 'none' (default) ")
        .with_line("\t--verbose - Use to get more detailed information about the run")
    )


class NewmanSubCommand(sub_command.PyntSubCommand):
    def __init__(self, name) -> None:
        super().__init__(name)

    def usage(self, *args):
        ui_thread.print(newman_usage())

    def add_cmd(self, parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
        newman_cmd = parent.add_parser(self.name)
        newman_cmd.add_argument("--collection", type=str, required=True)
        newman_cmd.add_argument("--environment", nargs="+", required=False)
        newman_cmd.add_argument(
            "--reporters", action="store_true", default=False, required=False
        )
        newman_cmd.add_argument("--severity-level", choices=["all", "medium", "high", "critical", "none"], default="none")
        newman_cmd.print_usage = self.usage
        newman_cmd.print_help = self.usage
        return newman_cmd

    def run_cmd(self, args: argparse.Namespace):

        port = util.find_open_port()
        container = pynt_container.get_container_with_arguments(
            args, pynt_container.PyntDockerPort(src=PYNT_CONTAINER_INTERNAL_PORT, dest=port, name="--port")
        )

        if not os.path.isfile(args.collection):
            ui_thread.print(
                ui_thread.PrinterText(
                    "Could not find the provided collection path, please provide with a valid collection path",
                    ui_thread.PrinterText.WARNING,
                )
            )
            return

        collection_name = os.path.basename(args.collection)
        container.docker_arguments += ["-c", collection_name]
        container.mounts.append(
            pynt_container.create_mount(
                os.path.abspath(args.collection), "/etc/pynt/{}".format(collection_name)
            )
        )

        if "environment" in args and args.environment:
            env_names = []
            for environ in args.environment:
                if not os.path.isfile(environ):
                    ui_thread.print(
                        ui_thread.PrinterText(
                            f"Could not find the provided environment path: {environ}, please provide with a valid environment path",
                            ui_thread.PrinterText.WARNING,
                        )
                    )
                    return
                env_name = os.path.basename(environ)
                env_names.append(env_name)
                container.mounts.append(
                    pynt_container.create_mount(
                        os.path.abspath(environ), "/etc/pynt/{}".format(env_name)
                    )
                )
            container.docker_arguments += ["-e", ",".join(env_names)]

        with util.create_default_file_mounts(args) as m:
            container.mounts += m
            newman_docker = pynt_container.PyntContainer(
                image_name=pynt_container.PYNT_DOCKER_IMAGE,
                tag="newman-latest",
                detach=True,
                base_container=container,
                use_native=args.use_docker_native)

            newman_docker.prepare_client()
            newman_docker.pre_run_validation(port)
            newman_docker.run()

            healthcheck = partial(
                util.wait_for_healthcheck, "http://localhost:{}".format(port)
            )

            healthcheck()
            ui_thread.print_verbose(util.GOT_INITIAL_HEALTHCHECK_MESSAGE)
            ui_thread.print(ui_thread.PrinterText(
                "Pynt docker is ready",
                ui_thread.PrinterText.INFO,
            ))

            ui_thread.print_generator(ui_thread.AnsiText.wrap_gen(newman_docker.stdout))

            with ui_thread.progress(
                    "ws://localhost:{}/progress".format(port),
                    healthcheck,
                    "scan in progress...",
                    100,
            ):
                while newman_docker.is_alive():
                    time.sleep(1)
