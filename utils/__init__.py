r"""
Runs once to create all visual assets and corresponding data.

| Component             | Task & Details                                            | Output                                                        |
|-----------------------|-----------------------------------------------------------|---------------------------------------------------------------|
| Pitch Logic           | Implement the core algorithm:                             | List of validated coordinates (e.g., `[(6, 8), (5, 3), ...]`) |
|                       |   $\mathbf{F = N_{\text{target}} - N_{\text{open, S}}}$   | for each target note.                                         |
|                       | to find all (string_num, fret) positions for a pitch      |                                                               |
|                       | (e.g., MIDI Notes 40 to 88).                              |                                                               |
|-----------------------|-----------------------------------------------------------|---------------------------------------------------------------|
| Fretboard SVG         | Use the **`fretboard`** library to draw the guitar neck   |                                                               |
|                       | and place markers (dots with fret numbers) at all         |                                                               |
|                       | calculated positions. Save each diagram as a unique       |                                                               |
|                       | SVG file (e.g., `static/diagrams/C4_all_pos.svg`).        | High-fidelity SVG files.  |                                   |
|-----------------------|-----------------------------------------------------------|---------------------------------------------------------------|
| Notation Image        | **Integrate VexFlow:** Since the `fretboard` library only |                                                               |
|                       | handles the guitar neck, you'll use VexFlow               |                                                               |
|                       | (a JavaScript library)** to render the staff notation     |                                                               |
|                       | (Treble Clef, note head, stem) on the front-end           |                                                               |
|                       | (see Phase III). *Alternatively,* you can generate and    |                                                               |
|                       | save a static set of notation PNGs/SVGs for all notes, but|                                                               |
|                       | client-side rendering is more flexible.                   | (For now, a placeholder or a plan to use VexFlow in the HTML  |
                                                                                    | template).                                                    |
|-----------------------|-----------------------------------------------------------|---------------------------------------------------------------|

"""

