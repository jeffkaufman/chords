import sys
from collections import namedtuple

NOTES=["I",
       "bI",
       "II",
       "bIII",
       "III",
       "IV",
       "bV",
       "V",
       "bVI",
       "VI",
       "bVII",
       "VII"]

ParsedTune = namedtuple(
  'ParsedTune', ['raw', 'key', 'chords'])
ParsedChord = namedtuple(
  'ParsedChord', ['raw', 'num', 'is_minor'])

def parse_chord(s):
  raw = s
  raw_root, s = s[0], s[1:]
  # midi numbers
  num_root = {'C': 24,
              'D': 26,
              'E': 28,
              'F': 29,
              'G': 31,
              'A': 33,
              'B': 35}[raw_root]
  while s.startswith("#") or s.startswith("b"):
    modifier, s = s[0], s[1:]
    num_root += (1 if modifier == "#" else -1)

  if s == "m":
    is_minor = True
  elif s == "":
    is_minor = False
  else:
    raise Exception("Can't parse '%s'; left with '%s'" % (raw, s))

  return ParsedChord(raw=raw, num=num_root, is_minor=is_minor)

def parse_tune(line):
  raw_chords = line.strip().split()
  chords = [parse_chord(raw_chord)
            for raw_chord in line.strip().split()]
  return ParsedTune(raw=line,
                    key=raw_chords[0],
                    chords=chords)

def interpret_chord(root, chord):
  delta_num = (chord.num - root.num + 12) % 12
  delta_text = NOTES[delta_num]
  if chord.is_minor:
    delta_text = delta_text.lower()
  return delta_text

def load(fnames):
  tunes = []
  for fname in fnames:
    with open(fname) as inf:
      for line in inf:
        line = line.strip()
        if line:
          tunes.append(parse_tune(line))
  return tunes

def reinterpret(tune, root):
  return [interpret_chord(root, chord)
          for chord in tune.chords]

def evaluate(tunes,
             options="",
             graph=False,
             relative_minor=True,
             mixolydian=True,
             thirds=True):
  if type(options) == type(""):
    options = options.split()

  if not thirds:
    options = [option.lower() for option in options]

  counts = []  # note index -> [major count, minor count]
  for note in NOTES:
    counts.append([0, 0])

  playable = 0

  for tune in tunes:
    root = tune.chords[0]

    if relative_minor and root.is_minor: # minor, think of as vi
      root = ParsedChord(raw="_", num=tune.chords[0].num + 3, is_minor=False)
    elif mixolydian and \
         "bVII" in reinterpret(tune, root): # mixolydian, think of as V
      root = ParsedChord(raw="_", num=tune.chords[0].num + 5, is_minor=False)

    interpreted = reinterpret(tune, root)
    if options:
      if not thirds:
        interpreted = [chord.lower() for chord in interpreted]
      if all(chord in options for chord in interpreted):
        #print ("%20s   %20s" % (tune.raw, " ".join(interpreted)))
        playable += 1
    else:
      for i, note in enumerate(NOTES):
        if note in interpreted:
          counts[i][0] += 1
        if note.lower() in interpreted:
          counts[i][1] += 1

  if options:
    #print("%.2f" % (playable / len(tunes)))
    return playable / len(tunes)
  else:
    if thirds:
      for i, note in enumerate(NOTES):
        for j, full_note in enumerate([note, note.lower()]):
          if graph:
            print("%4d  %4s: %s" % (counts[i][j], full_note, "*" * counts[i][j]))
          else:
            print("%s\t%s" % (full_note, counts[i][j]))
    else:
      for i, note in enumerate(NOTES):
        count = counts[i][0] + counts[i][1]
        if graph:
          print("%4d  %4s: %s" % (count, note, "*" * count))
        else:
          print("%s\t%s" % (note, count))

def consider(tunes, options_list, table=True):
  if table:
    print("<table border=1, cellpadding=5>")
    print("<tr><th>Chords<td>Thirds<td>Open")

  for options in options_list:
    if table:
      print ("<tr><td>%s<td>%.0f%%<td>%.0f%%" % (
        options,
        evaluate(tunes, options, thirds=True) * 100,
        evaluate(tunes, options, thirds=False) * 100))
    else:
      print("%.2f\t%.2f\t%s" % (
        evaluate(tunes, options, thirds=True),
        evaluate(tunes, options, thirds=False),
        options))

  if table:
    print ("</table>")

if __name__ == "__main__":
  tunes = load(sys.argv[1:])
  #evaluate(tunes)
  consider(tunes, [
    "I IV V",
    "I IV V vi",
    "I IV V vi",
    "I iii IV V vi",
    "I ii IV V vi",
    "I ii iii IV V vi",
  ])
