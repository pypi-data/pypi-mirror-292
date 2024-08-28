import logging
import os
import inotify.adapters
import subprocess
import time
import configparser
from tempuscator.exceptions import MissingConfigSection
import json

_logger = logging.getLogger("Notifier")


class IWatcher():

    def __init__(self, watch_directory: str, action: str, config: str):
        self.watch_directory = watch_directory
        self.action = action
        if os.path.isfile(config):
            self.config = self.__parse_config(file=config)
        if not os.path.exists(self.watch_directory):
            _logger.debug(f"Creating watching directory: {self.watch_directory}")
            os.mkdir(path=self.watch_directory, mode=0o750)

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=2)

    def __parse_config(self, file) -> dict:
        _logger.info(f"Parsing config file: {file}")
        config = configparser.RawConfigParser()
        with open(file, 'r') as f:
            config.read_file(f)
        if not config.has_section("obfuscator"):
            raise MissingConfigSection("No such section: obfuscator")
        return config._sections["obfuscator"]

    def watch(self) -> None:
        _logger.info(f"Watching directory: {self.watch_directory}")
        notify = inotify.adapters.InotifyTree(path=self.watch_directory)
        for e in notify.event_gen(yield_nones=False):
            (_, event, path, file) = e
            if "IN_MODIFY" in event:
                time.sleep(1)
                continue
            _logger.debug(f"InotifyEvent: {e}")
            if "IN_CLOSE_WRITE" in event:
                _logger.debug(f"New file created: {os.path.join(path, file)}")
                backup_file = os.path.join(path, file)
                if self.action == "obfuscate":
                    self.__action_obfuscate(backup=backup_file)

    def __action_obfuscate(self, backup) -> None:
        _logger.info("Starting obfuscation from IWatcher")
        cli = [self.config["executable"]]
        cli.append("--backup")
        cli.append(backup)
        cli.append("--sql-file")
        cli.append("/tmp/scrub.sql")
        cli.append("--save-archive")
        cli.append(self.config["save_path"])
        cli.append("--parallel")
        cli.append(self.config["parallel"])
        cli.append("--host")
        cli.append(self.config["scp_host"])
        cli.append("--ssh-user")
        cli.append(self.config["ssh_user"])
        cli.append("--scp-dst")
        cli.append(self.config["save_path"])
        cli.append("--log-level")
        cli.append("debug")
        _logger.debug(f"Executing: {' '.join(cli)}")
        obfuscate = subprocess.Popen(cli)
        obfuscate.communicate()
        _logger.info("Obfuscation finished")
