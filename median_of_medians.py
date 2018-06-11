#!/usr/bin/env python

from random import shuffle
from functools import partial
from math import ceil, floor
from datetime import datetime

# Simple O(n) algorithm for determining the median of an unsorted list


# Calculate median index by performing a full sort of data[start:end].
# Changes data
# Returns index of median
def median(data, start, end):
	data[start:end] = sorted(data[start:end])
	return floor((start + end) / 2)

# Reorder data[start:end] to have structure [<pivot|pivot|>pivot]
# Returns new index of pivot element
def partition(data, pivot, start, end):
	assert(start < end)
	assert(pivot >= start)
	assert(pivot < end)
	pivotval = data[pivot]
	while start < end:
		if pivotval > data[start]:
			# Order is ok, inspect next element
			start += 1
		elif pivotval < data[start]:
			# Element is larger than pivot, move to end
			end -= 1
			data[start], data[end] = data[end], data[start]
		else:
			# Element matches pivot, process remaining data from end
			while end > start + 1:
				end -= 1
				if data[end] <= pivotval:
					# Element is smaller than pivot, move it in front of pivot
					data[start], data[start + 1] = data[start + 1], data[start]
					if start + 1 == end:
						# Special case: If there is only one processable items after the pivot we are done
						# since we just swapped them
						start += 1
						break

					data[start], data[end] = data[end], data[start]
					start += 1
					end += 1
			break

	assert(data[start] == pivotval)
	return start

# Actual median of medians implementation
# group_size: Size of median subgroups
# min_size: Size below which median of group is determined by sorting
# Returns index of median
def fast_median_(data, group_size, min_size, start, end, order):
	assert(start < end)
	assert(start + order < end)
	assert(order >= 0)

	n = end - start
	# Bind function arguments used all the time
	bound_median = partial(fast_median_, data, group_size, min_size)
	if(n < min_size):
		# Calculate median directly if list is very short
		median(data, start, end)
		return start + order

	ngroups = ceil(n / group_size)
	# Split data into groups
	for i in range(ngroups):
		substart = start + i * group_size
		subend = min(end, substart + group_size)
		# Calculate median of groups directly because they are very small
		m = median(data, substart, subend)
		# Save medians to beginning of current data
		data[m], data[start + i] = data[start + i], data[m]

	# Calculate median of group medians
	pivotpos = bound_median(start, start + ngroups, floor(ngroups / 2))
	# Reorder elements such that data[start:end] has structure [<pivot|pivot|>pivot]
	pivotpos = partition(data, pivotpos, start, end)

	# Select area containing median
	if pivotpos > start + order:
		return fast_median_(data, group_size, min_size, start, pivotpos, order)
	elif pivotpos < start + order:
		return fast_median_(data, group_size, min_size, pivotpos + 1, end, order - (pivotpos - start) - 1)

	return pivotpos

# Wrapper for calling median of medians algorithm
# Returns index of median
def fast_median(data, group_size=5, min_size=10):
	return data[fast_median_(data, group_size, min_size, 0, len(data), floor(len(data) / 2))]



# Usage example and performance verification

sizes = [10, 100, 1000, 10000, 100000]
samples = 100

for size in sizes:
	runtime = 0
	last_res = None
	for _ in range(samples):
		data = list(range(0, size))
		shuffle(data)

		before = datetime.now()
		res = fast_median(data)
		after = datetime.now()

		delta = after - before

		runtime += (delta.total_seconds() * 1000000 + delta.microseconds / 1000) / samples

		if last_res != None:
			assert(res == last_res)
		last_res = res

	print("{: 7} runs: {} ms, result: {}".format(size, runtime / 1000, last_res))
