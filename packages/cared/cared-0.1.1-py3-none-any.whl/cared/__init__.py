try:
    import cared_cli  # noqa: F401

    cared_cli_installed = True
except ImportError:
    cared_cli_installed = False


def main() -> None:
    print("\nHello from CaReD!\n")
    if cared_cli_installed:
        print(
            'It looks like you installed the Python package "cared" in addition to "cared-cli"\n'
            'The package "cared" has no functionality.'
        )
    else:
        print(
            'It looks like you installed the Python package "cared" which has no functionality.\n'
            'You most likely want "cared-cli" instead available at https://pypi.org/project/cared-cli/'
        )
    print(
        '\nYou can safely uninstall the "cared" package by running: "pip uninstall cared"'
    )
