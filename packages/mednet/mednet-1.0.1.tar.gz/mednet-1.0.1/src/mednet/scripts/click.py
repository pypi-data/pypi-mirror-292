# Copyright © 2022 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import click
from clapper.click import ConfigCommand as _BaseConfigCommand


class ConfigCommand(_BaseConfigCommand):
    """A click command-class that has the properties of :py:class:`clapper.click.ConfigCommand` and adds verbatim epilog formatting."""

    def format_epilog(
        self,
        _: click.core.Context,
        formatter: click.formatting.HelpFormatter,
    ) -> None:
        """Format the command epilog during --help.

        Parameters
        ----------
        _
            The current parsing context.
        formatter
            The formatter to use for printing text.
        """

        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split("\n"):
                formatter.write(line + "\n")
