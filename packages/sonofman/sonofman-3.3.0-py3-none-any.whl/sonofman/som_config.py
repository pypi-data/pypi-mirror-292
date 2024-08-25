#!/usr/bin/env python3
from configparser import ConfigParser
import os
import sys
from importlib.resources import files
from shutil import copy
import sonofman.som_util as som_util

"""
VAR USED: 
* ALL SYSTEMS: HOME
* LINUX: 
    FLATPAK: XDG_DATA_HOME
    ELSE SNAP, GIT, PYPI.

Snap:
* System info orig:  /snap/bible-multi-the-son-of-man/x1/lib/python3.8/site-packages/sonofman/data/sonofman.ini
* System info used:  /home/<user>/snap/bible-multi-the-son-of-man/x1/.local/share/bible-multi-the-son-of-man/sonofman.ini

Flatpak:
* System info orig:  /app/lib/python3.9/site-packages/sonofman/data/sonofman.ini
* System info used:  /home/<user>/.var/app/org.hlwd.sonofman/data/sonofman.ini

Others (PyCharm/Git/PYPI/MacOS):
* System info orig:  /home/<user>/Git/BibleMultiTheSonOfMan/sonofman/data/sonofman.ini
* System info used:  /home/<user>/.local/share/bible-multi-the-son-of-man/sonofman.ini
"""


class SomConfig:
    def __init__(self):
        self.somutil = som_util.SomUtil
        self.is_flatpak = False
        self.dest_path = ""     # path of user data

        self.platform = sys.platform.upper()
        self.somutil.print("* Platform: {0}".format(self.platform))

        self.home = os.environ.get("HOME")
        self.somutil.print("* Home: {0}".format(self.home))

        try:
            self.somutil.print("* System Path: {0}".format(sys.path))
        finally:
            pass

        # som_path_ini = pkg_resources.resource_filename('sonofman.data', 'sonofman.ini')
        # som_path_db = pkg_resources.resource_filename('sonofman.data', 'bible.db')
        #
        som_path_ini = files('sonofman.data') / 'sonofman.ini'
        som_path_db = files('sonofman.data') / 'bible.db'

        self.pkg_path_db = som_path_db  # path of PKG

        # Create config if not exists.
        # Dependant of system: linux, mac...
        # If error => don't try to create config, but use the read only version
        if self.platform in ("DARWIN", "CYGWIN", "LINUX"):
            if self.platform in ("DARWIN", "CYGWIN"):
                self.is_flatpak = False
            elif self.platform == "LINUX":
                xdg_data_home = os.environ.get("XDG_DATA_HOME")
                self.somutil.print("* XDG_DATA_HOME: {0}".format(xdg_data_home))
                if xdg_data_home is None:
                    self.is_flatpak = False
                else:
                    self.is_flatpak = True if xdg_data_home.find("/.var/app/org.hlwd.sonofman/data") >= 0 else False

            self.dest_path = "{0}/.var/app/org.hlwd.sonofman/data".format(self.home) if self.is_flatpak else "{0}/.local/share/bible-multi-the-son-of-man".format(self.home)
            dest_ini_fullpath = "{0}/sonofman.ini".format(self.dest_path)
            dest_db_fullpath = "{0}/bible.db".format(self.dest_path)

            # ! We set path to destination ini file here and reuse the var !
            som_path_ini = dest_ini_fullpath

            # Create files
            try:
                is_db_file_exists = os.path.exists(dest_db_fullpath)
                if not is_db_file_exists:
                    os.makedirs(self.dest_path, mode=0o777, exist_ok=True)
                    copy(som_path_db, dest_db_fullpath)
            except Exception as ex:
                self.somutil.print("! Error: {0}".format(ex))

            try:
                is_ini_file_exists = os.path.exists(dest_ini_fullpath)
                if not is_ini_file_exists:
                    os.makedirs(self.dest_path, mode=0o777, exist_ok=True)
                    configfile = open(dest_ini_fullpath, 'x')
                    configfile.write(self.get_content_file())
                    configfile.close()
            except Exception as ex:
                self.somutil.print("! Error: {0}".format(ex))

        # General: after creation of file or not
        self.som_path_ini = som_path_ini
        self.somutil.print("* System (User) Ini: {0}".format(self.som_path_ini))

        self.config = ConfigParser()
        self.config.read(som_path_ini)

    def get_option(self, section, option, lst_valid_values, default_value):
        # noinspection PyBroadException
        try:
            value = self.config[section][option]
            value = value.replace("\"", "")
            if lst_valid_values is not None and value not in lst_valid_values:
                value = default_value
        except Exception as ex:
            self.somutil.print("! Unable to load parameter ({1}): {0}".format(ex, option))
            return default_value
        return value

    @staticmethod
    def get_content_file():
        return """[PREFERENCES]
    locale = "en"
    alt_locale = "en"
    use_colors = "0"
    bible_prefered = "k"
    history_current = "0"
    bible_multi = "k"
    color_k = "A_NORMAL#COLOR1"
    color_v = "A_NORMAL#COLOR1"
    color_l = "A_NORMAL#COLOR1"
    color_d = "A_NORMAL#COLOR1"
    color_a = "A_NORMAL#COLOR1"
    color_o = "A_NORMAL#COLOR1"
    color_s = "A_NORMAL#COLOR1"
    color_2 = "A_NORMAL#COLOR1"
    color_9 = "A_NORMAL#COLOR1"
    color_1 = "A_NORMAL#COLOR1"
    color_i = "A_NORMAL#COLOR1"
    color_y = "A_NORMAL#COLOR1"
    color_c = "A_NORMAL#COLOR1"
    color_j = "A_NORMAL#COLOR1"        
    color_r = "A_NORMAL#COLOR1"
    color_t = "A_NORMAL#COLOR1"
    color_b = "A_NORMAL#COLOR1"
    color_h = "A_NORMAL#COLOR1"
    color_e = "A_NORMAL#COLOR1"
    color_u = "A_NORMAL#COLOR1"
    color_z = "A_NORMAL#COLOR1"
    color_highlight_search = "A_REVERSE#"
    no_color_k = "A_NORMAL#"
    no_color_v = "A_NORMAL#"
    no_color_l = "A_NORMAL#"
    no_color_d = "A_NORMAL#"
    no_color_a = "A_NORMAL#"
    no_color_o = "A_NORMAL#"
    no_color_s = "A_NORMAL#"
    no_color_2 = "A_NORMAL#"
    no_color_9 = "A_NORMAL#"
    no_color_1 = "A_NORMAL#"
    no_color_i = "A_NORMAL#"
    no_color_y = "A_NORMAL#"
    no_color_c = "A_NORMAL#"
    no_color_j = "A_NORMAL#"        
    no_color_r = "A_NORMAL#"    
    no_color_t = "A_NORMAL#"    
    no_color_b = "A_NORMAL#"
    no_color_h = "A_NORMAL#"
    no_color_e = "A_NORMAL#"
    no_color_u = "A_NORMAL#"
    no_color_z = "A_NORMAL#"    
    no_color_highlight_search = "A_REVERSE#"

    [HISTORY]
    0 = "k#ART_APP_HELP_BEGINNING"
    """

    def set_option(self, section, option, value):
        try:
            self.config[section][option] = '"{0}"'.format(value)
        except Exception as ex:
            self.somutil.print("! Unable to set parameter ({1}): {0}".format(ex, option))

    def save_config(self):
        try:
            configfile = open(self.som_path_ini, 'w')
            self.config.write(configfile)
            configfile.close()
        except Exception as ex:
            self.somutil.print("! Unable to save config: {0}".format(ex))
