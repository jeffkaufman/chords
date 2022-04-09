from collections import namedtuple

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

def interpret_chord(root, chord):
  delta_num = (chord.num - root.num + 12) % 12
  delta_text = NOTES[delta_num]
  if chord.is_minor:
    delta_text = delta_text.lower()
  return delta_text

data = []

def process(fname):
  with open(fname) as inf:
    for line in inf:
      data.append(parse_tune(line.strip()))

process("f-and-w.txt")
process("t.txt")
      
counts = []
for note in NOTES:
  counts.append([0, 0])

def reinterpret(tune, root):
  return [interpret_chord(root, chord)
          for chord in tune.chords]
  
for tune in data:
  root = tune.chords[0]

  if True:  # reinterpret
    if root.is_minor: # minor, think of as vi
      root = ParsedChord(raw="_", num=tune.chords[0].num + 3, is_minor=False)
    elif "bVII" in reinterpret(tune, root): # mixolydian, think of as V
      root = ParsedChord(raw="_", num=tune.chords[0].num + 5, is_minor=False)

  interpreted = reinterpret(tune, root)

  for i, note in enumerate(NOTES):
    if note in interpreted:
      counts[i][0] += 1
    if note.lower() in interpreted:
      counts[i][1] += 1

if True:  # consider include thirds, distinguishing minor/major
  for i, note in enumerate(NOTES):
    for j, full_note in enumerate([note, note.lower()]):
      print("%4d  %4s: %s" % (counts[i][j], full_note, "*" * counts[i][j]))
else:
  for i, note in enumerate(NOTES):
    count = counts[i][0] + counts[i][1]
    print("%4d  %4s: %s" % (count, note, "*" * count))
