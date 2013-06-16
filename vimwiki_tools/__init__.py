"""vimwiki

Usage:
  vimwiki gen-index <wiki-folder> [--output-type=<type>] [--extension=<extension>] [--write] [--bulk]
  vimwiki 2markdown <wiki-folder> --output-extension=<extension>
  vimwiki stats <wiki-foler>

Options:
  -h --help                show this screen
  --version                show version
  -w --write               write to index.wiki
  -b --bulk                update all wikis
  -o --output-type=<type>  html or wiki [default: wiki]
  --extension=<ext>        extension of wiki files [default: wiki]

Example:
  vimwiki gen-index -w ~/wiki/linux
  vimwiki gen-index ~/wiki/linux --output-type html
  vimwiki 2markdown ~/wiki/programming --output-extension wiki
  vimwiki stats ~/wiki
"""

import sys
import os
from collections import defaultdict
import re
import operator
from docopt import docopt


def get_files(wiki_dir):
	walker = os.walk(wiki_dir, followlinks=True)
	_, _, filenames = walker.next()
	return [f for f in filenames if os.path.splitext(f)[0] != 'index']


def get_links(wiki_dir):
	walker = os.walk(wiki_dir, followlinks=True)
	_, _, filenames = walker.next()
	return [os.path.splitext(f)[0] for f in filenames if os.path.splitext(f)[0] != 'index']


def get_all_references(wiki_dir, files):
	# link_pattern = re.compile(r"\[\[(?:\w+:)?(\w+)(?:\|\w+)?\]\]")
	link_pattern = re.compile(r"\[\[([a-zA-Z0-9]+)(?:\|\w+)?\]\]")
	counts = defaultdict(int)
	for wiki in files:
		with open(os.path.join(wiki_dir, wiki)) as f:
			refs = link_pattern.findall(f.read())
			for ref in refs:
				counts[ref] += 1
	return counts


def output_as_html(links):
	min_font_size = 12
	max_font_size = 70
	sorted_links = sorted(links, key=operator.itemgetter(1))
	min_reference = sorted_links[0][1]
	max_reference = sorted_links[-1][1]

	def get_anchor((link, count)):
		font_size = min_font_size + (max_font_size - min_font_size) / (max_reference - min_reference) * (count - min_reference)
		return "<a href=\"%s.html\" style=\"font-size:%dpx\">%s</a>" % (link, round(font_size), link)

	return "\n".join([get_anchor(link) for link in links])

def output_as_wiki(links):
	sorted_links = sorted(links, key=operator.itemgetter(1), reverse=True)
	ret = ''
	current_line = ''
	links = (["[[%s]]" % link for link, _ in sorted_links])
	for link in links:
		if len(link) >= 80:
			if current_line != '':
				ret += current_line + "\n"
				current_line = ''
			ret += link + "\n"
		else:
			if len(current_line + link) >= 80:
				ret += current_line + "\n"
				current_line = link + ' '
			else:
				current_line += link + ' '
	if current_line != '':
		ret += current_line + "\n"
	return ret


def get_options():
	argv = sys.argv[1:]
	options = {
		"output": "wiki",
		"extension": "wiki",
	}
	switches = ''
	for idx, arg in enumerate(argv[:-1]):
		if arg[:2] == '--':
			if argv[idx + 1][:1] == '-':
				options[arg[2:]] = True
			else:
				options[arg[2:]] = argv[idx + 1]
		elif arg[:1] == '-':
			switches += arg[1:]
	args = argv[-1:]
	return switches, options, args


def single_wiki(wiki_dir, opts):
	files = get_files(wiki_dir)
	links = get_links(wiki_dir)
	references = get_all_references(wiki_dir, files)
	links = [(l, references[l]) for l in links]

	if opts['output_type'] == 'wiki':
		output_buffer = output_as_wiki(links)
	elif opts['output_type'] == 'html':
		output_buffer = output_as_html(links)

	if opts['write_tofile']:
		index_path = os.path.join(wiki_dir, 'index.' + opts['extension'])
		with open(index_path, 'w') as index:
			index.write(output_buffer)
			print("wrote %s" % index_path)
	else:
		print(output_buffer)


def multiple_wiki(root_dir, options):
	wikis = os.listdir(os.path.expanduser(root_dir))
	for wiki in wikis:
		wiki_path = os.path.join(root_dir, wiki)
		if os.path.isdir(wiki_path):
			single_wiki(wiki_path, options)


def getsub(m):
	if m.group() in ['{{{', '}}}']:
		return '```'
	_, level, title = m.groups()
	return "%s %s" % ("#" * len(level), title)


def convert2markdown(content):
	return re.sub(r"((={1,}) (.*) \2|\{{3}|\}{3})", getsub, content)


def markdown(wiki_dir, extension):
	files = get_files(wiki_dir)
	for f in files:
		name,ext = os.path.splitext(f)
		src = os.path.join(wiki_dir, f)
		dest = os.path.join(wiki_dir, name + os.path.extsep + extension)
		original = file(src).read()
		content = convert2markdown(original)
		if content != original:
			with open(dest,'w') as fp:
				fp.write(content)


def stats(root_dir):
	wikis = os.listdir(os.path.expanduser(root_dir))
	output = []
	for wiki in wikis:
		wiki_path = os.path.join(root_dir, wiki)
		if os.path.isdir(wiki_path):
			output.append((wiki,len(get_files(wiki_path))))

	pad = max([len(wiki) for (wiki,_) in output]) + 1

	for wiki,count in sorted(output, key=operator.itemgetter(1), reverse=True):
		print(('{0: >%d} {1}' % pad).format(wiki, count))


def main():
	args = docopt(__doc__, version='vimwiki 0.0.2')

	if args['gen-index']:

		opts = {
			"write_tofile": args['--write'],
			"extension": args['--extension'],
			"output_type": args['--output-type'],
		}

		if args['--bulk']:
			multiple_wiki(args['<wiki-folder>'], opts)
		else:
			single_wiki(args['<wiki-folder>'], opts)

	if args['2markdown']:
		markdown(args['<wiki-folder>'], args['--output-extension'])

	if args['stats']:
		stats(args['<wiki-foler>'])

if __name__ == '__main__':
	main()
