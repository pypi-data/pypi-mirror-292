"""
  add more util functions to help parse data
"""

from ast import literal_eval

def parse_dict(txt : str) -> dict:
  try:
    _crop = txt[txt.index("{"):txt.index("}") + 1]
  except:
    raise ValueError("Input is cut off or length error :{}".format(txt))
  else:
    return literal_eval(_crop)

def parse_tuple(txt : str) -> tuple:
  try:
    _crop = txt[txt.index("("):txt.index(")") + 1]
  except:
    raise ValueError("Input is cut off or length error  :{}".format(txt))
  else:
    return literal_eval(_crop)

def parse_list(txt : str) -> list:
  try:
    _crop = txt[txt.index("["):txt.index("]") + 1]
  except:
    raise ValueError("Input is cut off or length error  :{}".format(txt))
  else:
    return literal_eval(_crop)


def pick_parser(type : str) -> callable:
    if type == "dict":
      return parse_dict

    if type ==  "tuple":
      return parse_tuple

    if type == "list":
      return parse_tuple

    raise TypeError("Type not found {}".format(type))


if __name__ == "__main__":
  print("----")
  #asumme the line of data is a single type 1{} or [] or ()
  parser = pick_parser('tuple')


  txt = r"({'name': '.\\output-video\\private\\cery\\clips\\video00.mp4', 'gaus_white_percentage': 111.63432355967078, 'canny_white_percentage': 11.370916923868311, 'points': 228.9541055812757, 'focus': '3,4'}, -1.8821869999999876)"
  import re

  d = parser(txt=txt)
  print(d, type(d))
  """
    1.) before using literal_eval we can regex the positions of {} to crop the dict to find exact
        -assuming it a single dictionary per line table entry it should work

    2.) we can use a recursive algo to find the section which has a dict type but it does not tell us exactly

  """
  # print(matches)

  # converted =  literal_eval(txt)
  # print(converted, type(converted), len(converted))




