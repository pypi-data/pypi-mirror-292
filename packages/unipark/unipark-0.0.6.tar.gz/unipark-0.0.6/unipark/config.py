#!/usr/bin/env python3
# coding: utf-8
'''
Author: Park Lam <lqmonline@gmail.com>
'''
__all__ = [ 'settings' ]

import decouple

class Settings(object):
    auto_cast = True

    def __getattr__(self, item):
        if item in dir(self):
            return super().__getattr__(item)
        else:
            try:
                return self._retrieve_option_from_config(item)
            except decouple.UndefinedValueError as e:
                raise AttributeError(str(e))

    def _retrieve_option_from_config(self, *args, **kwargs):
        option = decouple.config(*args, **kwargs)
        if self.auto_cast and \
                isinstance(option, str):
            if kwargs.get('cast', None) is str: 
                return option
            elif option.upper() in ( 'TRUE', 'FALSE', ):
                return option.upper() == 'TRUE'
            else:
                try:
                    return int(option)
                except ValueError as e:
                    pass
                try:
                    return float(option)
                except ValueError as e:
                    pass
        return option


    def __call__(self, *args, **kwargs):
        if kwargs.get('force_reload', False):
            self.reload()
        return self._retrieve_option_from_config(*args, **kwargs)

    def reload(self):
        decouple.config.config = None

settings = Settings()
del Settings
