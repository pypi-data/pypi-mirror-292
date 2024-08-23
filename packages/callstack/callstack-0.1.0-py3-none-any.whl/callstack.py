import sys

class Frame:
	"""
		Because we want dot.notation, an official Frame class was necessary.
		Dot.notation is a common, default feature on generic objects in other languages, by the way.
	"""

	def __init__(self, path="", package="", module="", line=0, cls="", function=""):
		self.path = path
		self.package = package
		self.module = module
		self.line = line
		self.cls = cls
		self.function = function


_classMapping = {}

def get():
	""" Returns the callstack as a list of Frames """
	stack = []
	frame = sys._getframe(1)
	while frame:
		stack.append(Frame(
			path=frame.f_code.co_filename,
			package=frame.f_globals['__package__'],
			module=frame.f_globals['__name__'],
			line=frame.f_lineno,
			cls=getClassName(frame.f_code.co_filename, frame.f_lineno),
			function=frame.f_code.co_name
		))
		frame = frame.f_back
	return stack

def getOrigin():
	""" Returns a Frame object representing the origin of the call, one level up the stack from where getOrigin() is called. """
	frame = sys._getframe(2)
	return Frame(
		path=frame.f_code.co_filename,
		package=frame.f_globals['__package__'],
		module=frame.f_globals['__name__'],
		line=frame.f_lineno,
		cls=getClassName(frame.f_code.co_filename, frame.f_lineno),
		function=frame.f_code.co_name
	)


def parseFile(filepath):
	""" Parses Python modules as text files, and stores their matchup of line ranges to class names in our internal cache """
	print(f"parseClasses({filepath})")

	# classMap is the mapping for this file. Each entry is a tuple of (start, end) line numbers, paired to the string name of the class. Module code is provided as an empty string ""
	classMap = {}

	try:
		with open(filepath, 'r') as file:
			lines = file.readlines()

		stack = []  # Each new class definition is pushed/popped here
		current = {
			"class": "",	# The current class context, empty string for module-level code
			"line": 1, 		# The first line of the current context
			"indent": 0
		}
		indentMultiple = 0	# Each file can have its own indentation metric.  Tabs, spaces, 2/3/4 characters?  We assume the multiple based on the first instance.
		openDoubleComment = False
		openSingleComment = False

		for i, fullLine in enumerate(lines, start=1):
			line = fullLine.strip()

			if line == "":
				continue

			indent = max(0, len(fullLine) - len(line) - 1)

			if indentMultiple == 0 and indent > 0:
				# Once the multiple is identified, we need to correct the previous use of it.
				indentMultiple = indent
				stack[-1]["indent"] = indent

			if openDoubleComment and '"""' in line:
				openDoubleComment = False
			elif line.startswith('"""'):
				openDoubleComment = True

			if openSingleComment and "'''" in line:
				openSingleComment = False
			elif line.startswith("'''"):
				openSingleComment = True

			if not openDoubleComment and not openSingleComment:
				if line.startswith("class "):
					# Close the last entry
					if current["line"] < (i - 1):
						classMap[(current["line"], i - 1)] = current["class"]

					# Open the new entry
					current["class"] = line.split()[1].split('(')[0].strip(':')
					current["line"] = i
					stack.append({
						"class":current["class"],
						"line":current["line"],
						"indent": indent + indentMultiple
					})

				elif len(stack) == 0:
					stack.append({
						"class": "",
						"line": current["line"],
						"indent": indent
					})

				elif indent < stack[-1]["indent"]:
					# Handle exiting class scope based on indentation
					# Save the last class as the next entry in the classMap
					classMap[(stack[-1]["line"], i - 1)] = stack[-1]["class"]

					# Working from the end of our array, we'll cleanup until we match the same indentation.
					for j in range(len(stack) - 1, -1, -1):
						entry = stack[j]

						if indent < entry["indent"]:
							stack.pop()
						elif indent == entry["indent"]:
							current["class"] = entry["class"]
							current["line"] = i
							entry["line"] = i
							break

		# Close any remaining open classes
		classMap[(current["line"], len(lines))] = current["class"]
		_classMapping[filepath] = classMap
	except IOError:
		print(f"Error reading file: {filepath}")
	except SyntaxError:
		print(f"Syntax error in file: {filepath}")


def getClassName(path, linenumber):
	""" Returns the class name for a given line number in the specified file using pre-sorted class line ranges. """
	print(f"getClassName({path}, {linenumber})")

	# Ensure the class map is parsed and available
	if path not in _classMapping:
		parseFile(path)

	classMap = _classMapping.get(path, {})
	sortedKeys = list(classMap.keys())
	left, right = 0, len(sortedKeys) - 1

	while left <= right:
		mid = (left + right) // 2
		start, end = sortedKeys[mid]
		if start <= linenumber <= end:
			return classMap[(start, end)]
		elif linenumber < start:
			right = mid - 1
		else:
			left = mid + 1

	return None

