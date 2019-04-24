# The MIT License (MIT)
# Copyright (c) 2018 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import click

from xcube_server import __version__, __description__
from xcube_server.defaults import DEFAULT_PORT, DEFAULT_NAME, DEFAULT_ADDRESS, DEFAULT_UPDATE_PERIOD, \
    DEFAULT_CONFIG_FILE, DEFAULT_TILE_CACHE_SIZE

__author__ = "Norman Fomferra (Brockmann Consult GmbH)"


@click.command(name='server')
@click.version_option(__version__)
@click.option('--name', '-n', metavar='NAME', default=DEFAULT_NAME,
              help=f'Service name. Defaults to {DEFAULT_NAME!r}.')
@click.option('--address', '-a', metavar='ADDRESS', default=DEFAULT_ADDRESS,
              help=f'Service address. Defaults to {DEFAULT_ADDRESS!r}.')
@click.option('--port', '-p', metavar='PORT', default=DEFAULT_PORT, type=int,
              help=f'Port number where the service will listen on. Defaults to {DEFAULT_PORT}.')
@click.option('--update', '-u', metavar='UPDATE_PERIOD', type=float,
              default=DEFAULT_UPDATE_PERIOD,
              help='Service will update after given seconds of inactivity. Zero or a negative value will '
                   'disable update checks. '
                   f'Defaults to {DEFAULT_UPDATE_PERIOD!r}.')
@click.option('--config', '-c', metavar='CONFIG_FILE', default=None,
              help='Datasets configuration file. '
                   f'Defaults to {DEFAULT_CONFIG_FILE!r}.')
@click.option('--tilecache', '-t', metavar='TILE_CACHE', default=DEFAULT_TILE_CACHE_SIZE,
              help=f'In-memory tile cache size in bytes. '
                   f'Unit suffixes {"K"!r}, {"M"!r}, {"G"!r} may be used. '
                   f'Defaults to {DEFAULT_TILE_CACHE_SIZE!r}. '
                   f'The special value {"OFF"!r} disables tile caching.')
@click.option('--verbose', '-v', is_flag=True,
              help="Delegate logging to the console (stderr).")
@click.option('--traceperf', is_flag=True,
              help="Print performance diagnostics (stdout).")
def run_server(name: str,
               address: str,
               port: int,
               update: float,
               config: str,
               tilecache: str,
               verbose: bool,
               traceperf: bool):
    """
    Run an Xcube server.
    """

    from xcube_server.app import new_application
    from xcube_server.service import Service

    try:
        print(f'{__description__}, version {__version__}')
        service = Service(new_application(name),
                          name=name,
                          port=port,
                          address=address,
                          config_file=config,
                          tile_cache_size=tilecache,
                          update_period=update,
                          log_to_stderr=verbose,
                          trace_perf=traceperf)
        service.start()
        return 0
    except Exception as e:
        print('error: %s' % e)
        return 1


def main(args=None):
    run_server.main(args=args)


if __name__ == '__main__':
    main()
