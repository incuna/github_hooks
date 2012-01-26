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

    def get_repo_url(self, repo_name):
        return self.get_user_url() + repo_name + '/hooks'

    def get_hook_url(self, repo_name, hook_id):
        return self.get_repo_url(repo_name) + '/' + hook_id

    def run(self, *args):
        self.args = list(args)
        if not args:
            return self.usage()
        try:
            action = self.args.pop(0)
            if action == 'ls':
                self.ls()
            elif action == 'add':
                self.add()
            elif action == 'rm':
                self.rm()
            else:
                self.write('UNKNOWN ACTION %s' % action)
        except self.APIError as e:
            self.write(e.message)
            self.write('\n')

    def ls(self):
        """List the hooks on a repository.

        USAGE: ls REPONAME
        """
        if not self.args:
            self.usage('ls')
            return
        repo_url = self.get_repo_url(self.args[0])
        r = self.get_response(repo_url, 'get')
        hooks = json.loads(r.content)
        output = ['%d: %s (%s)' % (hook['id'], hook['name'], ','.join(sorted(hook['events']))) for hook in hooks]
        self.write(' '.join(output) if output else 'No hooks found.')
        self.write('\n')

    def add(self):
        """Add a hook.

        USAGE: add REPONAME TYPE EVENT[,EVENT...] [OPTION:VALUE[,OPTION:VALUE...]]
        """
        repo_name = self.args.pop(0)
        hook_type = self.args.pop(0)
        events = self.args.pop(0).split(',')
        options = self.args.pop(0).split(',') if self.args else []
        options = dict([opt.split(':', 1) for opt in options])

        repo_url = self.get_repo_url(repo_name)
        options = {
            'name': hook_type,
            'events': events,
            'config': options,
        }
        r = self.get_response(repo_url, 'post', data=json.dumps(options))
        hook = json.loads(r.content)
        output = 'New hook of with id %s created.\n' % hook['id']
        self.write(output)

    def rm(self):
        """Remove a hook.

        USAGE: rm REPONAME ID
        """
        repo_name = self.args.pop(0)
        hook_id = self.args.pop(0)

        hook_url = self.get_hook_url(repo_name, hook_id)
        r = self.get_response(hook_url, 'delete')
        self.write('Hook with id %s deleted.\n' % hook_id)

    def get_response(self, url, method, **kwargs):
        r = getattr(requests, method)(url, auth=self.get_auth(), **kwargs)
        if r.status_code not in [200, 201, 204]:
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
