"""lbkit命令行入口"""
import inspect
import os
import signal
import sys
import shutil
import argparse
import traceback
from lbkit import __version__ as client_version
from lbkit.codegen.codegen import CodeGen
from lbkit.component.build import BuildComponent
from lbkit.component.test import TestComponent
from lbkit.integration.build_manifest import BuildManifest
from lbkit.integration.build_rootfs import BuildRootfs
from lbkit.integration.build_prepare import BuildPrepare
from lbkit.integration.build_image import BuildImage
from lbkit.component.arg_parser import ArgParser
from lbkit.integration.config import Config
from lbkit.ci_robot.gitee import Gitee
from lbkit.log import Logger
from lbkit import misc
from lbkit import errors

log = Logger("cli")


class Command(object):
    """A single command of the lbkit application, with all the first level commands. Manages the
    parsing of parameters and delegates functionality in collaborators. It can also show the
    help of the tool.
    """
    def __init__(self):
        pass
    def help(self, *args):
        """
        Shows help for a specific command.
        """

        parser = argparse.ArgumentParser(description=self.help.__doc__,
                                         prog="lbkit help")
        parser.add_argument("command", help='command', nargs="?")
        args = parser.parse_args(*args)
        if not args.command:
            self._show_help()
            return
        try:
            commands = self._commands()
            method = commands[args.command]
            self._warn_python_version()
            method(["--help"])
        except KeyError:
            raise errors.LiteBmcException("Unknown command '%s'" % args.command)

    def gen(self, *args):
        """
        代码自动生成.

        支持自动生成服务端和客户端C代码
        """
        gen = CodeGen(sys.argv[2:])
        gen.run("./metadata/package.yml")

    # new package
    def new(self, *args):
        """
        按LiteBmc最佳实践创建一个新的组件.

        你需要指定你需要使用的编程语言，当前仅支持C(基于litebmc框架)和C++(基于openbmc的sdbusplus)
        """
        log.info("new package")

    # build package
    def build(self, *args):
        """
        构建组件.

            组件需要支持多种跨平台构建场景，典型的包括DT（X86-64）、交叉编译（arm64）
        """
        arg_parser = ArgParser.new()
        build = BuildComponent(arg_parser, sys.argv[2:])
        build.run()

    # create product package
    def create(self, *args):
        """
        构建组件.

            组件需要支持多种跨平台构建场景，典型的包括DT（X86-64）、交叉编译（arm64）
        """
        cfg = Config(sys.argv[2:])
        build = BuildPrepare(cfg, "create_pre")
        build.run()
        build = BuildManifest(cfg, "create_run")
        build.run()
        build = BuildRootfs(cfg, "create_rootfs")
        build.run()
        build = BuildImage(cfg, "create_image")
        build.run()

    def gitee(self, *args):
        """
        Call gitee api.

            CI场景调用gitee的API完成像标签、评论等基本操作
        """
        _ = Gitee(sys.argv[2:])

    # test package
    def test(self, *args):
        """
        构建DT.

        组件DT用例执行
        """
        argv = sys.argv[2:]
        build = TestComponent(argv)
        build.run()

    def _show_help(self):
        """
        Prints a summary of all commands.
        """
        grps = [("Code Generate commands", ["gen"]),
                ("Build Component commands", ["new", "build", "test"]),
                ("Build Product commands", ["create"]),
                ("Misc commands", ["help"]),
                ("CI Robot commands", ["gitee"])
               ]

        def check_all_commands_listed():
            """Keep updated the main directory, raise if don't"""
            all_commands = self._commands()
            all_in_grps = [command for _, command_list in grps for command in command_list]
            if set(all_in_grps) != set(all_commands):
                diff = set(all_commands) - set(all_in_grps)
                raise Exception("Some command is missing in the main help: %s" % ",".join(diff))
            return all_commands

        commands = check_all_commands_listed()
        max_len = max((len(c) for c in commands)) + 1
        fmt = '  %-{}s'.format(max_len)

        for group_name, comm_names in grps:
            print(group_name + ":")
            for name in comm_names:
                # future-proof way to ensure tabular formatting
                output = (fmt % (misc.Color.GREEN + name + misc.Color.RESET_ALL))
                if len(output) < 32:
                    space = " "*(32 - len(output))
                    output += space

                # Help will be all the lines up to the first empty one
                docstring_lines = commands[name].__doc__.split('\n')
                start = False
                data = []
                for line in docstring_lines:
                    line = line.strip()
                    if not line:
                        if start:
                            break
                        start = True
                        continue
                    data.append(line)

                import textwrap
                output += textwrap.fill(' '.join(data), 80, subsequent_indent=" "*(max_len+2))
                print(output)

        print("")
        print('LiteBmcKit commands. Type "litebmc <command> -h" for help')

    def _commands(self):
        """ Returns a list of available commands.
        """
        result = {}
        for m in inspect.getmembers(self, predicate=inspect.ismethod):
            method_name = m[0]
            if not method_name.startswith('_'):
                method = m[1]
                if method.__doc__ and not method.__doc__.startswith('HIDDEN'):
                    result[method_name] = method
        return result

    def _warn_python_version(self):
        import textwrap

        width = 70
        version = sys.version_info
        if version.major < 3:
            log.info("*"*width + "\nPython 2 support has been dropped. It is strongly "
                                            "recommended to use Python >= 3.0\n" + "*"*width)

    def run(self, *args):
        """HIDDEN: entry point for executing commands, dispatcher to class
        methods
        """
        ret_code = 0
        try:
            try:
                command = args[0][0]
            except IndexError:  # No parameters
                self._show_help()
                return False
            try:
                commands = self._commands()
                method = commands[command]
            except KeyError as exc:
                if command in ["-v", "--version"]:
                    log.info("LiteBmc version %s" % client_version)
                    return False

                self._warn_python_version()

                if command in ["-h", "--help"]:
                    self._show_help()
                    return False

                log.error("'%s' is not a LiteBmc command. See 'lbkit --help'." % command)
                raise errors.LiteBmcException("Unknown command %s" % str(exc))

            method(args[0][1:])
        except KeyboardInterrupt as exc:
            log.error(exc)
            ret_code = 0
        except SystemExit as exc:
            if exc.code != 0:
                log.error("Exiting with code: %d" % exc.code)
            ret_code = exc.code
        except (errors.LiteBmcException, errors.RunCommandException, errors.ArgException, errors.PackageConfigException, Exception, errors.OdfValidateException) as exc:
            if os.environ.get("LOG"):
                print(traceback.format_exc())
            ret_code = -1
            msg = str(exc)
            log.error(misc.Color.RED + msg + misc.Color.RESET_ALL)

        return ret_code


def main(args):
    # 使能revision功能
    os.environ["CONAN_REVISIONS_ENABLED"] = "1"
    # 创建并清空日志目录
    shutil.rmtree(misc.LOG_DIR, ignore_errors=True)
    os.makedirs(misc.LOG_DIR, exist_ok=True)
    def ctrl_c_handler(_, __):
        print('You pressed Ctrl+C!')
        sys.exit(-3)

    def sigterm_handler(_, __):
        print('Received SIGTERM!')
        sys.exit(-4)

    signal.signal(signal.SIGINT, ctrl_c_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    command = Command()
    error = command.run(args)
    sys.exit(error)

