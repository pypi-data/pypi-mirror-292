#!/usr/bin/python

"""
Copyright (C) 2014 DK

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import print_function
import sys
import os
import time
import argparse
import hashlib
import shutil
import pipes
try:
	import version
except:
	version = None

def parse_args(argv):
	parser = argparse.ArgumentParser(description="pmcc - poor man's change control")
	if version:
		parser.add_argument('--version', action='version', version='%%(prog)s %s' % version.VERSION )
	parser.add_argument('-u', '--unidiff', action='store_true', dest='unidiff', help='diff output in unidiff format')
	parser.add_argument('-U', '--unidiff-lines', dest='unidiff_lines', type=int, metavar='CONTEXT_LINES', help='diff output in unidiff format with given number of context lines')
	parser.add_argument('-b', '--ignore-space-change', action='store_true', dest='ignore_space', help='diff should ignore space mode')
	parser.add_argument('--color', action='store_true', dest='colordiff', help='use colordiff')
	parser.add_argument('-c', '--change-rev', dest='change_rev', type=int, help='revision to display the diff for')
	parser.add_argument('-f', '--from', dest='from_filename', type=str, help='filename to use as a source of snapshot, e.g. an ad-hoc copy .bak')
	parser.add_argument('-t', '--to', dest='new_name', type=str,help='new filename')
	parser.add_argument('--di', '--diff', dest='action', action='store_const', const='di', help='display diff')
	parser.add_argument('--ci', '--commit', dest='action', action='store_const', const='ci', help='commit the current state as a new revision')
	parser.add_argument('--log', dest='action', action='store_const', const='log', help='display the list of revisions')
	parser.add_argument('--format', dest='format', choices=['revid'], help='log format')
	parser.add_argument('--restore', dest='action', action='store_const', const='restore', help='restore the given revision')
	parser.add_argument('--cat', dest='action', action='store_const', const='cat', help='cat the given revision')
	parser.add_argument('--name', dest='action', action='store_const', const='name', help='display the filename corresponding to the given revision')
	parser.add_argument('--vim', dest='action', action='store_const', const='vim', help="invoke vim on the file, after verifying that it's clean, or fail if it's not")
	parser.add_argument('--emacs', dest='action', action='store_const', const='emacs', help="invoke emacs on the file, after verifying that it's clean, or fail if it's not")
	parser.add_argument('--edit', dest='action', action='store_const', const='edit', help="invoke EDITOR on the file, after verifying that it's clean, or fail if it's not")
	parser.add_argument('--drop', '--delete', dest='action', action='store_const', const='drop', help="drop (delete) given revision's snapshot")
	parser.add_argument('--mv', '--move', dest='action', action='store_const', const='move', help='move file and all snapshots to the given new name')
	parser.add_argument('filename', nargs='+', type=str, default=None, help='filename(s) to handle')
	args = parser.parse_args(argv)
	args.action = args.action or 'di'
	return args

def find_version_list(target_filename):
	target_dir = os.path.dirname(target_filename) or '.'
	target_nameonly = os.path.basename(target_filename)
	for sibling_nameonly in os.listdir(target_dir):
		if len(sibling_nameonly) > len(target_nameonly)+2 \
			and sibling_nameonly[:1]=='.' \
			and sibling_nameonly[1:len(target_nameonly)+1]==target_nameonly \
			and sibling_nameonly[1+len(target_nameonly)]=='.' \
			and sibling_nameonly[2+len(target_nameonly):].isdigit() \
			:
			yield os.path.join(target_dir, sibling_nameonly)

def process_target(target_filename, args):
	action_silent = args.action in ('cat', 'name')
	if not action_silent and args.format != 'revid':
		print()
		print('#', repr(target_filename))
	# assert os.path.exists(target_filename), "ERROR: target doesn't exist: %s" % repr(target_filename)
	source_filename = args.from_filename or target_filename
	if os.path.exists(target_filename):
		target_exists = True
		target_ts = int(os.path.getmtime(source_filename))
		target_md5 = hashlib.md5(open(source_filename,'rb').read()).hexdigest()
		snapshot_filename = os.path.join( os.path.dirname(target_filename),  '.%s.%s' % (os.path.basename(target_filename), target_ts) )
	else:
		target_exists = False
		target_ts = None
		target_md5 = None
		snapshot_filename = None
	snapshot_is_current = False
	if snapshot_filename and os.path.exists(snapshot_filename) and not action_silent and args.format != 'revid':
		snapshot_md5 = hashlib.md5(open(snapshot_filename,'rb').read()).hexdigest()
		assert snapshot_md5==target_md5, "ERROR: snapshot exists but MD5 doesn't match"
		snapshot_is_current = True
		if not action_silent:
			print("# OK", repr(source_filename), "<-", repr(snapshot_filename))
	if False:
		pass
	elif args.action=='ci' and not snapshot_is_current:
		print("# ci", repr(source_filename), "->", repr(snapshot_filename))
		print("cp -vp", repr(source_filename), repr(snapshot_filename))
		shutil.copy2(source_filename, snapshot_filename)
	elif args.action=='ci':
		print('# ==', repr(source_filename), '<-', repr(snapshot_filename))
	elif args.action=='di' and (args.change_rev or not snapshot_is_current):
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		if args.change_rev:
			assert args.change_rev-1 in range(len(version_list_ext))
			rev_filename = version_list_ext[args.change_rev-1]
			if args.change_rev > 1:
				last_filename = version_list_ext[args.change_rev-2]
			else:
				last_filename = '/dev/null'
		else:
			rev_filename = source_filename
			if version_list:
				last_filename = version_list[-1]
			else:
				last_filename = '/dev/null'
		print('# MM', repr(source_filename))
		if version_list:
			print('# diff', pipes.quote(last_filename), pipes.quote(rev_filename))
			sys.stdout.flush()
			diffcmd = 'diff'
			if args.colordiff:
				diffcmd = 'colordiff'
			if args.unidiff_lines is not None:
				diffcmd += ' -U%s' % args.unidiff_lines
			elif args.unidiff:
				diffcmd += ' -u'
			if args.ignore_space:
				diffcmd += ' -b'
			ret = os.system('%s %s %s' % (diffcmd, pipes.quote(last_filename), pipes.quote(rev_filename)))
			sys.exit(ret)
		else:
			print('# ++', repr(source_filename))
	elif args.action=='di':
		print('# ==', repr(source_filename), '<-', repr(snapshot_filename))
	elif args.action=='restore':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		print('# restore %s <= %s' % (pipes.quote(target_filename), pipes.quote(rev_filename)))
		ret = os.system('cp -vp %s %s' % (pipes.quote(rev_filename), pipes.quote(target_filename)))
		sys.exit(ret)
	elif args.action=='cat':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		ret = os.system('cat %s' % pipes.quote(rev_filename))
		sys.exit(ret)
	elif args.action=='name':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		print(rev_filename)
		sys.exit(0)
	elif args.action=='log':
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		if not target_exists:
			version_list_ext.pop()
		for version_index in range(len(version_list_ext)):
			version_rev = version_index+1
			version_filename = version_list_ext[version_index]
			version_ts = int(os.path.getmtime(version_filename))
			version_tm = time.localtime(version_ts)
			version_time_str = time.strftime('%Y-%m-%d %H:%M:%S', version_tm)
			if args.format == 'revid':
				print(version_rev)
			else:
				print('# [r%d] [%s] %s' % (version_rev, version_time_str, version_filename))
	elif args.action in ('vim', 'emacs', 'edit'):
		if not snapshot_is_current:
			print("ERROR: file is not checked in: %s" % repr(target_filename),file=sys.stderr)
			sys.exit(1)
		# cheating - using args.action as the literal command
		editor = args.action
		if args.action=='edit':
			editor = os.getenv('EDITOR')
			if not editor:
				print("ERROR: EDITOR variable not defined - don't know what to invoke",file=sys.stderr)
				sys.exit(1)
		ret = os.system('%s %s' % (args.action, pipes.quote(target_filename)))
		sys.exit(ret)
	elif args.action=='drop':
		if not args.change_rev:
			print("ERROR: droping requires change revision argument",file=sys.stderr)
			sys.exit(1)
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		version_list_ext = version_list + [ target_filename ]
		assert args.change_rev and args.change_rev-1 in range(len(version_list_ext))
		rev_filename = version_list_ext[args.change_rev-1]
		rm_cmd = 'rm %s' % pipes.quote(rev_filename)
		print(rm_cmd)
		ret = os.system(rm_cmd)
		sys.exit(ret)
	elif args.action in ('mv','move'):
		if not args.new_name:
			print("ERROR: moving requires new name",file=sys.stderr)
			sys.exit(1)
		target_dir = os.path.dirname(target_filename)
		target_nameonly = os.path.basename(target_filename)
		new_dir = os.path.dirname(args.new_name)
		new_nameonly = os.path.basename(args.new_name)
		version_list = list(find_version_list(target_filename))
		version_list.sort()
		mv_tuples = [ (target_filename, args.new_name) ]
		for version in version_list:
			ver_target_dir = os.path.dirname(version) or '.'
			ver_target_nameonly = os.path.basename(version)
			ver_target_newname = ver_target_nameonly.replace('.%s.' % target_nameonly, '.%s.' % new_nameonly)
			ver_new_full = os.path.join(ver_target_dir, ver_target_newname)
			assert not os.path.exists(ver_new_full)
			mv_tuples.append( (version, ver_new_full) )
		print('moving..')
		for (old_name, new_name) in mv_tuples:
			assert not os.path.exists(new_name)
			mv_ver_cmd = 'mv -v %s %s' % (pipes.quote(old_name), pipes.quote(new_name) )
			print(mv_ver_cmd)
			os.system(mv_ver_cmd)
		print('done')
	else:
		raise Exception("ERROR: unexpected action - %s" % repr(args.action))

def main():
	args = parse_args(sys.argv[1:])
	for filename in args.filename:
		process_target(target_filename=filename, args=args)

if __name__ == '__main__':
	main()
