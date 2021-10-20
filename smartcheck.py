
"""
Reads SMART results (--all) from `stdin`

Checks a number of SMART attributes for bad values and errors

Exits with code equal to number of errors
"""

import io
import pandas as pd
import sys

"""
Returns lines after `hint`, until empty line
"""
def get_section(lines, hint):
  section = list()
  
  i = 0
  
  while i < len(lines):
    if lines[i].startswith(hint):
      i += 1
      break
    else:
      i += 1
  
  while i < len(lines):
    if len(lines[i].strip()) > 0:
      section.append(lines[i])
      i += 1
    else:
      break
  
  return section

def get_attributes_table(lines):
  hint = 'Vendor Specific SMART Attributes with Thresholds:'
  
  section = get_section(lines, hint)
  
  stream = io.StringIO('\n'.join(section))
  
  table = pd.read_fwf(stream)
  
  if 'ATTRIBUTE_NAME' not in table \
    or 'ID#' not in table \
    or 'RAW_VALUE' not in table:
    raise SyntaxError('Unrecognized format for attributes table')
  
  return table

def process(lines):
  attributes_table = get_attributes_table(lines)
  
  print(attributes_table)
  
  check_id_nums = [5, 187, 188, 197, 198]
  
  print('Looking for attributes ' + str(check_id_nums))
  
  filtered_attributes = attributes_table.loc[attributes_table['ID#'].isin(check_id_nums)]
  
  if len(filtered_attributes) != len(check_id_nums):
    missing_id_nums = set(check_id_nums) - set(filtered_attributes['ID#'].unique())
    print('Warning, some attributes missing (' + str(missing_id_nums) + ')')
  
  num_errors = int(filtered_attributes['RAW_VALUE'].astype(int).sum()) # need to convert from pandas numpy.int64 to native python int
  
  print('Error count = ' + str(num_errors))
  
  return num_errors

def main():
  if not sys.stdin.isatty():
    sys.exit(process(sys.stdin.readlines()))
  else:
    raise EOFError('No data from stdin')

if __name__ == '__main__':
  main()