import os
import argparse
import textwrap
import json
import yaml
import re
import requests
from colorama import Fore, Style
from jsonschema import validate, ValidationError
from lbkit.errors import PackageConfigException, HttpRequestException

LOG_DIR = "/tmp/lbkit/log"


class Color(object):
    """ Wrapper around colorama colors that are undefined in importing
    """
    RED = Fore.RED  # @UndefinedVariable
    WHITE = Fore.WHITE  # @UndefinedVariable
    CYAN = Fore.CYAN  # @UndefinedVariable
    GREEN = Fore.GREEN  # @UndefinedVariable
    MAGENTA = Fore.MAGENTA  # @UndefinedVariable
    BLUE = Fore.BLUE  # @UndefinedVariable
    YELLOW = Fore.YELLOW  # @UndefinedVariable
    BLACK = Fore.BLACK  # @UndefinedVariable
    RESET_ALL = Style.RESET_ALL

    BRIGHT_RED = Style.BRIGHT + Fore.RED  # @UndefinedVariable
    BRIGHT_BLUE = Style.BRIGHT + Fore.BLUE  # @UndefinedVariable
    BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW  # @UndefinedVariable
    BRIGHT_GREEN = Style.BRIGHT + Fore.GREEN  # @UndefinedVariable
    BRIGHT_CYAN = Style.BRIGHT + Fore.CYAN   # @UndefinedVariable
    BRIGHT_WHITE = Style.BRIGHT + Fore.WHITE   # @UndefinedVariable
    BRIGHT_MAGENTA = Style.BRIGHT + Fore.MAGENTA   # @UndefinedVariable


if os.environ.get("COLOR_DARK", 0):
    Color.WHITE = Fore.BLACK
    Color.CYAN = Fore.BLUE
    Color.YELLOW = Fore.MAGENTA
    Color.BRIGHT_WHITE = Fore.BLACK
    Color.BRIGHT_CYAN = Fore.BLUE
    Color.BRIGHT_YELLOW = Fore.MAGENTA
    Color.BRIGHT_GREEN = Fore.GREEN

class SmartFormatter(argparse.HelpFormatter):
    """重写HelpFormatter"""
    def _fill_text(self, text, width, indent):
        """重写HelpFormatter"""
        text = textwrap.dedent(text)
        return ''.join(indent + line for line in text.splitlines(True))

def get_json_schema_file(yml_file, default_json_schema_file):
    """使用json schema文件校验yml_file配置文件"""
    with open(yml_file, "r") as fp:
        for line in fp:
            match = re.search(r"#[ ]*yaml-language-server:[ ]*\$schema=(.*)\n", line)
            if match is not None:
                return match.group(1)
    return default_json_schema_file

def load_json_schema(schema_file):
    """使用json schema文件校验yml_file配置文件"""
    if schema_file.startswith("https://litebmc.com/"):
        resp = requests.get(schema_file)
        if resp.status_code != 200:
            raise HttpRequestException(f"Get {schema_file} failed, status code: {resp.status_code}")
        return json.loads(resp.content)
    elif not os.path.isfile(schema_file):
        raise FileNotFoundError(f"schemafile {schema_file} not exist")
    else:
        with open(schema_file, "r") as fp:
            tmp = fp.read()
            return json.loads(tmp)

def load_yml_with_json_schema_validate(yml_file, default_json_schema_file):
    """使用json schema文件校验yml_file配置文件"""
    schema_file = get_json_schema_file(yml_file, default_json_schema_file)
    if schema_file is None:
        raise FileNotFoundError(f"Can't found invalid schema file in {yml_file}")

    schema = load_json_schema(schema_file)
    try:
        fp = open(yml_file, "r")
        data = yaml.safe_load(fp)
        fp.close()
        validate(data, schema)
        return data
    except ValidationError as exc:
        raise PackageConfigException(f"validate {yml_file} failed, schema file is {schema_file}, "
                                     f"message: {exc.message}\n"
                                     "installing redhat.vscode-yaml plugin in vscode will help you write odf files")
