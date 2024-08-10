from distutils.command.bdist import bdist
import sys

if 'egg' not in bdist.format_commands:
    try:
        # For backward compatibility with older distutils (stdlib)
        bdist.format_commands['egg'] = ('bdist_egg', "Python .egg file")  # type: ignore[call-overload]
    except TypeError:
        bdist.format_command['egg'] = ('bdist_egg', "Python .egg file")
        bdist.format_commands.append('egg')

del bdist, sys
