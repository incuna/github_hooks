#!/usr/bin/env python

import json
import sys

import requests
import yaml


def trim(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxint
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxint:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


class GithubApi(object):
    """Github api.

    Available methods: ls
    """
    url_base = 'https://api.github.com/repos/'
    _writer = None

    def __init__(self):
        self.get_config()

    class APIError(Exception):
        pass

    def get_config_file_path(self):
        return 'config.yaml'

    def get_config(self):
        with open(self.get_config_file_path()) as f:
            self.config = yaml.load(f.read())

    def get_auth(self):
        return (self.config['auth']['user'], self.config['auth']['password'])

    def get_user_url(self):
        return self.url_base + self.config['github']['user'] + '/'

    def run(self, *args):
        self.args = args
        if not args:
            return self.usage()
        try:
            if args[0] == 'ls':
                self.ls()
        except self.APIError as e:
            self.write(e.message)
            self.write('\n')

    def ls(self):
        """List the hooks on a repository.

        USAGE: ls REPONAME
        """
        ls_args = self.args[1:]
        if not ls_args:
            self.usage('ls')
            return
        repo_url = self.get_user_url() + ls_args[0] + '/hooks'
        r = self.get_response(repo_url, 'get')
        hooks = json.loads(r.content)
        output = ['%d: %s (%s)' % (hook['id'], hook['name'], ','.join(sorted(hook['events']))) for hook in hooks]
        self.write(' '.join(output))
        self.write('\n')

    def get_response(self, url, method):
        r = getattr(requests, method)(url, auth=self.get_auth())
        if not r.status_code == 200:
            raise self.APIError('APIError: %d\n%s' % (r.status_code, r.content))
        return r

    def usage(self, method=None):
        if not method:
            self.write('USAGE:\n')
            self.write(trim(self.__doc__))
        else:
            self.write(trim(getattr(self, method).__doc__))
        self.write('\n')

    def write(self, data):
        self._writer(data)

    def set_writer(self, writer):
        self._writer = writer

api = GithubApi()


if __name__ == '__main__':
    api.set_writer(sys.stdout.write)
    api.run(*sys.argv[1:])
