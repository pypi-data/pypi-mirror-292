"""
Entry point for the interface. Used to automatically take measurements of spectral data.

09-08-2024
Hugo Gomes
"""

from automatic_spectral_acquisition.cli import create_app


def main() -> None:
    # Launch the CLI
    app = create_app()
    app()


if __name__ == "__main__":
    main()
