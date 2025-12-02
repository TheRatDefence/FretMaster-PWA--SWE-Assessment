from config import PREFER_SHARPS

# Map of note names to their position in the chromatic scale (0-11)
note_map = {
    'C': 0, 'B#': 0,
    'C#': 1, 'Db': 1,
    'D': 2,
    'D#': 3, 'Eb': 3,
    'E': 4, 'Fb': 4,
    'E#': 5, 'F': 5,
    'F#': 6, 'Gb': 6,
    'G': 7,
    'G#': 8, 'Ab': 8,
    'A': 9,
    'A#': 10, 'Bb': 10,
    'B': 11, 'Cb': 11
}

def note_to_midi(note: str) -> int:
    """
    Convert a note name with octave (e.g., 'C4', 'A#5', 'Db3') to MIDI number.

    :param note: The note name with octave (e.g., 'C4', 'A#5', 'Db3')
    :return: The MIDI note number (0-127)
    """

    # Split into octave and note name and check input
    try:
        octave    = int(note[-1])   # Last character should be the octave
        note_name = str(note[:-1])
    except ValueError as e:
        raise ValueError(f"Invalid note syntax: {e}")


    # Get the pitch class (0-11)
    if note_name not in note_map:
        raise ValueError(f"Invalid note name: {note_name}")

    pitch_class = note_map[note_name]

    # MIDI formula: MIDI = (octave + 1) * 12 + pitch_class
    midi_number = (octave + 1) * 12 + pitch_class

    return midi_number

def midi_to_note(midi_number: int, prefer_sharps: bool = PREFER_SHARPS) -> str:
    """
    Convert a midi number to a note name and pitch.

    :param midi_number: The MIDI note number (0-127)
    :param prefer_sharps: If True, use sharps (C#), if False, use flats (Db)
    :return: The note name with octave (e.g., 'C4', 'A#5', 'Db3')
    """

    if not 0 <= midi_number <= 127:
        raise ValueError(f"MIDI number {midi_number} outside valid range (0-127)")


    # Note names for each pitch class (0-11)
    note_names_sharp = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    note_names_flat  = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

    note_names = note_names_sharp if prefer_sharps else note_names_flat

    # Reverse the MIDI formula: MIDI = (octave + 1) * 12 + pitch_class
    octave = (midi_number // 12) - 1
    pitch_class = midi_number % 12

    note_name = note_names[pitch_class]

    return f"{note_name}{octave}"


# Maybe add support for alternate tunings
guitar_string_map = {
    0: note_to_midi('E2'),
    1: note_to_midi('A2'),
    2: note_to_midi('D3'),
    3: note_to_midi('G3'),
    4: note_to_midi('B3'),
    5: note_to_midi('E4'),
}



def midi_to_string_fret(string_num: int, target_midi_number: int) -> tuple[int, int]:
    """
    Converts a single midi note to a string and fret.

    :param string_num: The string number (0 - 5)
    :param target_midi_number: The target note as midi number
    :return: Tuple[String Number, Fret Number]
    """

    if not 0 <= string_num <= 5:
        raise ValueError(f'String number: {string_num} outside 0 - 5 range')

    open_string_midi = guitar_string_map[string_num]
    fret_number = target_midi_number - open_string_midi

    return string_num, fret_number

def note_to_guitar_positions(target_note: str) -> list[tuple[int, int]]:
    """
    Returns a list of string name and fret positions for the target note

    :param target_note: Target note as note name and octave (Eg. 'C4')
    :return: List[tuple[string number, fret number]]
    """

    midi_note_number = note_to_midi(target_note)
    number_of_strings = len(guitar_string_map)

    positions: list[tuple[int, int]] = ([])
    for string_number in range(number_of_strings):
        string_fret = midi_to_string_fret(string_number, midi_note_number)
        positions.append(string_fret)

    return positions

if __name__ == '__main__':
    print(note_to_guitar_positions('E4'))