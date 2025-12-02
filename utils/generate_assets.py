from config import DIAGRAM_PATH
from utils.pitch_logic import note_to_guitar_positions
from fretboardgtr.fretboard import FretBoard
from pathlib import Path

def create_diagram(target_note: str, fret_range: tuple[int, int] = (0, 12)) -> Path:
    """
    Creates a fretboard diagram SVG for all positions of a target note.

    :param target_note: The note to diagram (e.g., 'C4', 'A#5')
    :param fret_range: Tuple of (min_fret, max_fret) to display
    :return: Path to the saved SVG file
    """
    # Create diagram
    fb = FretBoard() # Customise styling later

    note_name_only = target_note[:-1] # Extracts just the note name, need to make customisable in config

    # Add the notes to the diagram
    lower_bound, upper_bound = fret_range
    for string_num, fret in note_to_guitar_positions(target_note):
        if lower_bound <= fret <= upper_bound:
            fb.add_note(string_no=string_num + 1, note=note_name_only)

    # Make the directory if it doesn't exist
    DIAGRAM_PATH.mkdir(parents=True, exist_ok=True)

    # Save the diagram
    save_name = DIAGRAM_PATH / f'{target_note}.svg'
    fb.export(str(save_name), format='svg')

    return save_name


if __name__ == '__main__':
    print(create_diagram('C4'))