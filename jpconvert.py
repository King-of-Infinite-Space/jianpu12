#%%
from mingus.containers import Note as MNote
from mingus.core.notes import note_to_int, int_to_note

def duration_to_letter(duration):
    duration_dict = {4: '', 8: 'q', 16: 's', 32: 'd', 64: 'h'}
    return duration_dict[duration]

def twelve_to_seven(num12):
    number_dict = {
        1: '1', 2: '#1', 3: '2', 4: '#2', 5: '3', 6: '4',
        7: '#4', 8: '5', 9: '#5', 10: '6', 11: '#6', 12: '7',
    }
    return number_dict[num12]

class Note(MNote):
    def __init__(self, note_str, baseNote=MNote(48)):
        self.baseNote = baseNote
        # assuming note_str is in jianpu12 notation, eg 11'.//
        self.slash = note_str.count('/')
        self.duration = 4 * 2**self.slash
        self.extension = '.' if '.' in note_str else ''
        octave = self.baseNote.octave + note_str.count("'") - note_str.count(",")
        note_12 = int(note_str.strip(",'./|"))
        if note_12 > 12:
            raise ValueError("Note number must be between 0 and 12")
        note_int = (note_12 - 1) + octave * 12 + note_to_int(self.baseNote.name)
        # integer notation, C0 = 0
        super().__init__(note_int)

    @property
    def mixedNum(self):
        return str(int(self)%12+1)+'^'+str(self.octave)

    # the following properties are base dependent
    @property
    def dot(self):
        interval = int(self) - (self.baseNote.octave * 12 + note_to_int(self.baseNote.name))
        rel_octave = interval // 12
        dot = "'"*rel_octave if rel_octave > 0 else ","*(-rel_octave)
        return dot

    @property
    def number12(self):
        return (int(self) - note_to_int(self.baseNote.name))%12 + 1

    @property
    def number(self):
        return twelve_to_seven(self.number12)

    def to_ly(self):
        raise NotImplementedError("Not implemented yet")

    def to_jp12(self):
        return str(self.number12) + self.dot + self.extension +'/'*self.slash

    def to_jp7(self):
        return str(self.number7) + self.dot + self.extension +'/'*self.slash

    def to_jianpuly(self):
        return duration_to_letter(self.duration)+self.number+self.dot+self.extension

def set_note(note, noteStr):
    if noteStr[-1] in '1234567890':
        note.set_note(noteStr[:-1], int(noteStr[-1]))
    else:
        note.set_note(noteStr, 4)

def convert_to_jianpuly(lines):
    def convert_line(line):
        symbols = line.rstrip().split(' ')
        for i, s in enumerate(symbols):
            if s == '|':
                symbols[i] = '' # remove bar line
            elif s in ['-','','(',')','~']:
                pass
            elif s.startswith('0'):
                duration = 4*2**s.count('/')
                symbols[i] = duration_to_letter(duration) + '0' + '.'*s.count('.')
            else:
                symbols[i] = Note(s,baseNote).to_jianpuly()
        return ' '.join(symbols)+'\n'
    
    baseNote = MNote()
    linesStart = False
    for j, line in enumerate(lines):
        if not linesStart and line == '\n': # first empty line after preamble
            linesStart = True
        elif line.startswith('NextScore'):
            linesStart = False
        elif line.startswith('1='):
            set_note(baseNote, line.rstrip()[2:])
        elif line.startswith('%') or ':' in line:
            pass
        else:
            if linesStart:
                lines[j] = convert_line(line)
    return lines

def changeKeySignature(lines, keySig):
    def process_line(line, oldBase, newBase):
        symbols = line.rstrip().split(' ')
        for i, s in enumerate(symbols):
            if s in ['-','','(',')','~','|']:
                pass
            elif s.startswith('0'):
                pass
            else:
                note = Note(s,oldBase)
                note.baseNote = newBase
                symbols[i] = note.to_jp12()
        return ' '.join(symbols)+'\n'

    oldBase = MNote()
    newBase = MNote()
    linesStart = False
    for j, line in enumerate(lines):
        if not linesStart and line == '\n': # first empty line after preamble
            linesStart = True
        elif line.startswith('NextScore'):
            linesStart = False
        elif line.startswith('1='):
            set_note(oldBase, line.rstrip()[2:])
            if keySig[0] in '0123456789-':
                newBase.from_int(int(oldBase) + int(keySig))
            else:
                set_note(newBase, keySig)
            lines[j] = f'1={newBase.name}{newBase.octave}\n'
        elif line.startswith('%') or ':' in line:
            pass
        else:
            if linesStart:
                lines[j] = process_line(line, oldBase, newBase)
    return lines

def main(args):
    if args.shift:
        args.keySig = str(-args.shift)
    if args.keySig:
        if args.keySig[0] in '0123456789-':
            print(f'Moving key signature by {args.keySig} (shifting numbers by {-int(args.keySig)})')
        else:
            print('Changing key signature to %s' % args.keySig)
        outfile = args.infile if args.outfile is None else args.outfile
        with open(args.infile, 'r') as f:
            lines = f.readlines()
        lines = changeKeySignature(lines, args.keySig)
        with open(outfile, 'w') as f:
            f.writelines(lines)
        print('Changed key signature to %s in file %s' % (args.keySig, outfile))
    else:
        outfile_jply = args.infile.replace('.jp12', '.jply') if args.outfile is None else args.outfile
        print(f'Converting {args.infile} to jianpu-ly format')
        with open(args.infile, 'r') as f:
            lines = f.readlines()
        lines = convert_to_jianpuly(lines)
        with open(outfile_jply, 'w') as f:
            f.writelines(lines)
        print(f'Converted {args.infile} to {outfile_jply}')
        if args.compile:
            print(f'Compiling {outfile_jply} with jianpu-ly and lilypond')
            outfile_ly = outfile_jply.replace('.jply', '.ly')
            import subprocess, sys
            print(f'Converting {outfile_jply} to {outfile_ly}')
            subprocess.run(f'python ./jianpu-ly/jianpu-ly.py {outfile_jply} > {outfile_ly}', shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT, check=True)
            print(f'Converted {outfile_jply} to {outfile_ly}')
            print(f'Compiling {outfile_ly} with lilypond')
            subprocess.run(['lilypond', outfile_ly], stdout=sys.stdout, stderr=subprocess.STDOUT, check=True)
        if args.delete:
            import os
            os.remove(outfile_ly)
            print(f'Deleted {outfile_ly}')

#%%
if __name__ == '__main__':
    import argparse
    desc = '''If no options are provided, 
        convert jianpu12 format to jianpu-ly format
        '''
    parser = argparse.ArgumentParser(epilog=desc)
    parser.add_argument('infile', type=str, help='jianpu12 file to convert')
    parser.add_argument('outfile', type=str, nargs='?', default=None, help='output file')
    parser.add_argument('-c', '--compile', action='store_true', help='compile the converted file with lilypond')
    parser.add_argument('-d', '--delete', action='store_true', help='delete intermediate .ly file after compilation')
    parser.add_argument('-k', '--keySig', type=str, help='change key sig of jp12 to given key or by given interval')
    parser.add_argument('-s', '--shift', type=int, help='shift the numbers of jp12 by given number')
    args = parser.parse_args()
    main(args)