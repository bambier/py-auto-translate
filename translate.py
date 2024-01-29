#! /usr/bin/env python3
import argparse
import logging
import subprocess
import sys
import typing
from os import mkdir, path, walk
from pathlib import Path

# Codes


BASE_DIR = Path().parent


class Transtalor:

    def __init__(self, languages: typing.Iterable[str] = ["fa", "en"], compile: bool = False, translate: bool = False, log_level=logging.NOTSET, domain: str = "base", path: str = BASE_DIR) -> None:
        self.logger = logging.Logger("Translator", level=log_level)
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info("Initilizing translator")
        self.languages = sorted(languages)
        self.do_compile = compile
        self.do_translate = translate
        self.domain = domain
        self.path = path

    def run(self):
        try:
            if self.do_translate:
                self.translate()
            if self.do_compile:
                self.compile()

            self.logger.info("Translation completed successfuly")

        except Exception as e:
            self.logger.critical(f'Error while running command.')
            self.logger.error(e)
            sys.exit(1)

    def get_python_files(self, directory: str) -> typing.List[str]:
        self.logger.info(
            f'Getting python files in `{str(directory)}` directory')
        python_files = []
        for root, dirs, files in walk(directory):
            files = [f for f in files if not f[0] == '.']
            dirs[:] = [d for d in dirs if not d[0] == '.']
            for file in files:
                if file.endswith(".py"):
                    python_files.append(path.join(root, file))
        return python_files

    def translate(self) -> None:
        self.logger.info(
            f'Translating python files with `gettext` and `xgettext`')

        for lang in self.languages:
            self.logger.info(
                f'Creating translation `.po` file for language `{lang}`')

            if not path.exists(f'{self.path}/locales'):
                self.logger.info(
                    f'Locales dir not found. Creating locales dir')
                mkdir(f'{self.path}/locales/')
            if not path.exists(f'{self.path}/locales/{lang}'):
                self.logger.info(
                    f'{lang} language dir not found. Creating {lang} dir')
                mkdir(f'{self.path}/locales/{lang}/')
            if not path.exists(f'{self.path}/locales/{lang}/LC_MESSAGES/'):
                self.logger.info(
                    f'LC_MESSAGES dir not found. Creating LC_MESSAGES dir')
                mkdir(f'{self.path}/locales/{lang}/LC_MESSAGES/')

            command = ['xgettext', '--language=Python', '-d', self.domain, '-o',
                       f'{self.path}/locales/{lang}/LC_MESSAGES/{self.domain}.po', *self.get_python_files(self.path)]

            if path.exists(f'{self.path}/locales/{lang}/LC_MESSAGES/{self.domain}.po'):
                self.logger.info(
                    f'Previues `.po` file found. Adding `-j` to options.')
                command.append('-j')

            subprocess.run(command)

            with open(f'{self.path}/locales/{lang}/LC_MESSAGES/{self.domain}.po', 'r+') as file:
                text = file.read()
                file.seek(0)
                text = text.replace("CHARSET", "UTF-8")
                file.write(text)
                file.truncate()

    def compile(self) -> None:
        self.logger.info(f'Translating python files with `msgfmt`')
        for lang in self.languages:
            self.logger.info(f'Translating python files for language {lang}')
            command = ['msgfmt', '-o',
                       f'{self.path}/locales/{lang}/LC_MESSAGES/{self.domain}.mo', f'{self.path}/locales/{lang}/LC_MESSAGES/{self.domain}.po']
            subprocess.run(command)

    def __repr__(self) -> str:
        self.logger.info(f'Printing Translator')
        return f"<Translator compile={self.compile} translate={self.translate} log level={self.logger.level}>"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Translate or compile translation po/pot files to mo',
        epilog='Version 1.0\n\a')

    LOG_LEVELS = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,

        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
        'notset': logging.NOTSET,

        'C': logging.CRITICAL,
        'E': logging.ERROR,
        'W': logging.WARNING,
        'I': logging.INFO,
        'D': logging.DEBUG,
        'N': logging.NOTSET,

        'c': logging.CRITICAL,
        'e': logging.ERROR,
        'w': logging.WARNING,
        'i': logging.INFO,
        'd': logging.DEBUG,
        'n': logging.NOTSET,
    }

    parser.add_argument('-c', '--compile',
                        action='store_true', default=False, help="compile created translation files")
    parser.add_argument('-t', '--translate',
                        action='store_true', default=False, help="create translation files")
    parser.add_argument('-l', '--languages',
                        help="Language codes", nargs='+', default=["fa", "en"])
    parser.add_argument(
        '-ll', '--log-level', choices=LOG_LEVELS.keys(), default='NOTSET', help="Loging level")
    parser.add_argument(
        '-d', '--domain', required=False, default="base", help="Domain of apllication")
    parser.add_argument('-p', '--path', default=BASE_DIR,
                        help="path to scan")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif not (args.compile or args.translate):
        parser.error('No action requested.')
    else:
        args.log_level = LOG_LEVELS[args.log_level]
        translator = Transtalor(**vars(args))
        translator.run()
