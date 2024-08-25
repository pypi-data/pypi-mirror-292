##
# EPITECH PROJECT, 2022
# Desktop_pet (Workspace)
# File description:
# colourise_output.py
##

"""
The file containing the code in charge of outputting
coloured text into the terminal.
This class follows the batch colour coding rules (from 0 to F for foreground and background)
"""

from typing import TextIO, Union
import os
import sys
import platform
try:
    import colorama as COC
except ImportError as e:
    msg = "Fatal Error (Colourise Output):"
    msg += "Failed to load Colorama, core dependency for Colourise Output."
    msg += " Aborting.\nImport error msg:"
    raise RuntimeError(msg) from e

ALL = "*"
BOLD = "bold"
DIM = "dim"
ITALIC = "italic"
UNDERLINE = "underline"
BLINK = "blink"
INVERT = "invert"
CONCEALED = "concealed"
STRIKE = "strike"


class ColouriseOutput:
    """
    The class in charge of adding colour to text 
    This class follows the batch colour coding rules (from 0 to F for foreground and background)
    """
    # ---- Custom font formaters ----
    ALL = "*"
    BOLD = "bold"
    DIM = "dim"
    ITALIC = "italic"
    UNDERLINE = "underline"
    BLINK = "blink"
    INVERT = "invert"
    CONCEALED = "concealed"
    STRIKE = "strike"

    def __init__(self, output_channel: TextIO = sys.stdout, error: int = 1, success: int = 0) -> None:
        self.__version__ = "1.0.0"
        self.author = "Henry Letellier"
        self.colour_pallet = {}
        self.unix_colour_pallet = {}
        self.colourise_output = True
        self.wich_system = platform.system()
        self.output = output_channel
        self.error = error
        self.success = success

    def process_attributes(self, attributes: Union[tuple[str], str]) -> list:
        """
        __summary__
            Convert the inputted tuple to a list containing the options

        __parameters__
            attributes: Union[tuple[str], str]
                Either: a tuple containing the attributes to be processed
                Or: the specific attribute to be processed
            The tuple options are:
                * for all the attributes: '*' (will apply all the attributes, thus, any other attributes specified will be ignored)
                * for bold: 'bold' or '1'
                * for dim: 'dim' or '2'
                * for italic: 'italic' or '3'
                * for underline: 'underline' or '4'
                * for blink: 'blink' or '5' or '6'
                * for invert: 'invert' or '7'
                * for concealed: 'concealed' or '8'
                * for strike: 'strike' or '9'
        __returns__
            string
        """
        finall_attributes = ""
        if '*' in attributes:
            return "\033[1m\033[2m\033[3m\033[4m\033[5m\033[7m\033[8m\033[9m"
        if isinstance(attributes, str) is True:
            attributes = (attributes,)
        if isinstance(attributes, tuple) is False:
            return finall_attributes
        added = {
            BOLD: False,
            DIM: False,
            ITALIC: False,
            UNDERLINE: False,
            BLINK: False,
            INVERT: False,
            CONCEALED: False,
            STRIKE: False
        }
        for i in attributes:
            item = i.lower()
            if item in (BOLD, "1"):
                if added[BOLD] is True:
                    continue
                finall_attributes += "\033[1m"  # bold
                added[BOLD] = True
            elif item in (DIM, "2"):
                if added[DIM] is True:
                    continue
                finall_attributes += "\033[2m"  # dim
                added[DIM] = True
            elif item in (ITALIC, "3"):
                if added[ITALIC] is True:
                    continue
                finall_attributes += "\033[3m"  # italic
                added[ITALIC] = True
            elif item in (UNDERLINE, "4"):
                if added[UNDERLINE] is True:
                    continue
                finall_attributes += "\033[4m"  # underline
                added[UNDERLINE] = True
            elif item in (BLINK, "5", "6"):
                if added[BLINK] is True:
                    continue
                finall_attributes += "\033[5m"  # blink
                added[BLINK] = True
            elif item in (INVERT, "7"):
                if added[INVERT] is True:
                    continue
                finall_attributes += "\033[7m"  # invert
                added[INVERT] = True
            elif item in (CONCEALED, "8"):
                if added[CONCEALED] is True:
                    continue
                finall_attributes += "\033[8m"  # concealed (hidden)
                added[CONCEALED] = True
            elif item in (STRIKE, "9"):
                if added[STRIKE] is True:
                    continue
                finall_attributes += "\033[9m"  # strike (cross through)
                added[STRIKE] = True
            else:
                pass
        return finall_attributes

    def display(self, colour: str, attributes: tuple = (), text: str = "") -> None:
        """__summay__

        Depending on the system, change the command used to output colour.
        Convert the inputted tuple to a list containing the options

    __parameters__

            test: str
                The text to be displayed
            attributes: tuple[str]
                The tuple containing the attributes to be processed
            The tuple options are:
                * for all the attributes: '*' (will apply all the attributes, thus, any other attributes specified will be ignored)
                * for bold: 'bold' or '1'
                * for dim: 'dim' or '2'
                * for italic: 'italic' or '3'
                * for underline: 'underline' or '4'
                * for blink: 'blink' or '5' or '6'
                * for invert: 'invert' or '7'
                * for concealed: 'concealed' or '8'
                * for strike: 'strike' or '9'
            colour: str
                * '00': Dark Black on Black
                * '01': Dark Blue on  Black
                * '02': Dark Green on Black
                * '03': Dark Cyan on Black
                * '04': Dark Red on Black
                * '05': Dark Magenta on Black
                * '06': Dark Yelllow on Black
                * '07': Dark White on Black
                * '08': Dark Grey on Black
                * '09': Dark Blue on Black
                * '0A': Bright Green on Black
                * '0B': Bright Cyan on Black
                * '0C': Bright Red on Black
                * '0D': Bright Magenta on Black
                * '0E': Bright Yellow on Black
                * '0F': Bright White on Black
                * '0r': Default Colour on Black
                * '10': Dark Black on Blue
                * '11': Dark Blue on Blue
                * '12': Dark Green on Blue
                * '13': Dark Cyan on Blue
                * '14': Dark Red on Blue
                * '15': Dark Magenta on Blue
                * '16': Dark Yelllow on Blue
                * '17': Dark White on Blue
                * '18': Dark Grey on Blue
                * '19': Dark Blue on Blue
                * '1A': Bright Green on Blue
                * '1B': Bright Cyan on Blue
                * '1C': Bright Red on Blue
                * '1D': Bright Magenta on Blue
                * '1E': Bright Yellow on Blue
                * '1F': Bright White on Blue
                * '1r': Default Colour on Blue
                * '20': Dark Black on Green
                * '21': Dark Blue on Green
                * '22': Dark Green on Green
                * '23': Dark Cyan on Green
                * '24': Dark Red on Green
                * '25': Dark Magenta on Green
                * '26': Dark Yelllow on Green
                * '27': Dark White on Green
                * '28': Dark Grey on Green
                * '29': Dark Blue on Green
                * '2A': Bright Green on Green
                * '2B': Bright Cyan on Green
                * '2C': Bright Red on Green
                * '2D': Bright Magenta on Green
                * '2E': Bright Yellow on Green
                * '2F': Bright White on Green
                * '2r': Default Colour on Green
                * '30': Dark Black on Cyan
                * '31': Dark Blue on Cyan
                * '32': Dark Green on Cyan
                * '33': Dark Cyan on Cyan
                * '34': Dark Red on Cyan
                * '35': Dark Magenta on Cyan
                * '36': Dark Yelllow on Cyan
                * '37': Dark White on Cyan
                * '38': Dark Grey on Cyan
                * '39': Dark Blue on Cyan
                * '3A': Bright Green on Cyan
                * '3B': Bright Cyan on Cyan
                * '3C': Bright Red on Cyan
                * '3D': Bright Magenta on Cyan
                * '3E': Bright Yellow on Cyan
                * '3F': Bright White on Cyan
                * '3r': Default Colour on Cyan
                * '40': Dark Black on Red
                * '41': Dark Blue on Red
                * '42': Dark Green on Red
                * '43': Dark Cyan on Red
                * '44': Dark Red on Red
                * '45': Dark Magenta on Red
                * '46': Dark Yelllow on Red
                * '47': Dark White on Red
                * '48': Dark Grey on Red
                * '49': Dark Blue on Red
                * '4A': Bright Green on Red
                * '4B': Bright Cyan on Red
                * '4C': Bright Red on Red
                * '4D': Bright Magenta on Red
                * '4E': Bright Yellow on Red
                * '4F': Bright White on Red
                * '4r': Default Colour on Red
                * '50': Dark Black on Magenta
                * '51': Dark Blue on Magenta
                * '52': Dark Green on Magenta
                * '53': Dark Cyan on Magenta
                * '54': Dark Red on Magenta
                * '55': Dark Magenta on Magenta
                * '56': Dark Yelllow on Magenta
                * '57': Dark White on Magenta
                * '58': Dark Grey on Magenta
                * '59': Dark Blue on Magenta
                * '5A': Bright Green on Magenta
                * '5B': Bright Cyan on Magenta
                * '5C': Bright Red on Magenta
                * '5D': Bright Magenta on Magenta
                * '5E': Bright Yellow on Magenta
                * '5F': Bright White on Magenta
                * '5r': Default Colour on Magenta
                * '60': Dark Black on Yellow
                * '61': Dark Blue on Yellow
                * '62': Dark Green on Yellow
                * '63': Dark Cyan on Yellow
                * '64': Dark Red on Yellow
                * '65': Dark Magenta on Yellow
                * '66': Dark Yelllow on Yellow
                * '67': Dark White on Yellow
                * '68': Dark Grey on Yellow
                * '69': Dark Blue on Yellow
                * '6A': Bright Green on Yellow
                * '6B': Bright Cyan on Yellow
                * '6C': Bright Red on Yellow
                * '6D': Bright Magenta on Yellow
                * '6E': Bright Yellow on Yellow
                * '6F': Bright White on Yellow
                * '6r': Default Colour on Yellow
                * '70': Dark Black on White
                * '71': Dark Blue on White
                * '72': Dark Green on White
                * '73': Dark Cyan on White
                * '74': Dark Red on White
                * '75': Dark Magenta on White
                * '76': Dark Yelllow on White
                * '77': Dark White on White
                * '78': Dark Grey on White
                * '79': Dark Blue on White
                * '7A': Bright Green on White
                * '7B': Bright Cyan on White
                * '7C': Bright Red on White
                * '7D': Bright Magenta on White
                * '7E': Bright Yellow on White
                * '7F': Bright White on White
                * '7r': Default Colour on White
                * '80': Dark Black on Grey
                * '81': Dark Blue on Grey
                * '82': Dark Green on Grey
                * '83': Dark Cyan on Grey
                * '84': Dark Red on Grey
                * '85': Dark Magenta on Grey
                * '86': Dark Yelllow on Grey
                * '87': Dark White on Grey
                * '88': Dark Grey on Grey
                * '89': Dark Blue on Grey
                * '8A': Bright Green on Grey
                * '8B': Bright Cyan on Grey
                * '8C': Bright Red on Grey
                * '8D': Bright Magenta on Grey
                * '8E': Bright Yellow on Grey
                * '8F': Bright White on Grey
                * '8r': Default Colour on Grey
                * '90': Dark Black on Blue
                * '91': Dark Blue on Blue
                * '92': Dark Green on Blue
                * '93': Dark Cyan on Blue
                * '94': Dark Red on Blue
                * '95': Dark Magenta on Blue
                * '96': Dark Yelllow on Blue
                * '97': Dark White on Blue
                * '98': Dark Grey on Blue
                * '99': Dark Blue on Blue
                * '9A': Bright Green on Blue
                * '9B': Bright Cyan on Blue
                * '9C': Bright Red on Blue
                * '9D': Bright Magenta on Blue
                * '9E': Bright Yellow on Blue
                * '9F': Bright White on Blue
                * '9r': Default Colour on Blue
                * 'A0': Dark Black on Green
                * 'A1': Dark Blue on Green
                * 'A2': Dark Green on Green
                * 'A3': Dark Cyan on Green
                * 'A4': Dark Red on Green
                * 'A5': Dark Magenta on Green
                * 'A6': Dark Yelllow on Green
                * 'A7': Dark White on Green
                * 'A8': Dark Grey on Green
                * 'A9': Dark Blue on Green
                * 'AA': Bright Green on Green
                * 'AB': Bright Cyan on Green
                * 'AC': Bright Red on Green
                * 'AD': Bright Magenta on Green
                * 'AE': Bright Yellow on Green
                * 'AF': Bright White on Green
                * 'Ar': Default Colour on Green
                * 'B0': Dark Black on Cyan
                * 'B1': Dark Blue on Cyan
                * 'B2': Dark Green on Cyan
                * 'B3': Dark Cyan on Cyan
                * 'B4': Dark Red on Cyan
                * 'B5': Dark Magenta on Cyan
                * 'B6': Dark Yelllow on Cyan
                * 'B7': Dark White on Cyan
                * 'B8': Dark Grey on Cyan
                * 'B9': Dark Blue on Cyan
                * 'BA': Bright Green on Cyan
                * 'BB': Bright Cyan on Cyan
                * 'BC': Bright Red on Cyan
                * 'BD': Bright Magenta on Cyan
                * 'BE': Bright Yellow on Cyan
                * 'BF': Bright White on Cyan
                * 'Br': Default Colour on Cyan
                * 'C0': Dark Black on Red
                * 'C1': Dark Blue on Red
                * 'C2': Dark Green on Red
                * 'C3': Dark Cyan on Red
                * 'C4': Dark Red on Red
                * 'C5': Dark Magenta on Red
                * 'C6': Dark Yelllow on Red
                * 'C7': Dark White on Red
                * 'C8': Dark Grey on Red
                * 'C9': Dark Blue on Red
                * 'CA': Bright Green on Red
                * 'CB': Bright Cyan on Red
                * 'CC': Bright Red on Red
                * 'CD': Bright Magenta on Red
                * 'CE': Bright Yellow on Red
                * 'CF': Bright White on Red
                * 'Cr': Default Colour on Red
                * 'D0': Dark Black on Pink
                * 'D1': Dark Blue on Pink
                * 'D2': Dark Green on Pink
                * 'D3': Dark Cyan on Pink
                * 'D4': Dark Red on Pink
                * 'D5': Dark Magenta on Pink
                * 'D6': Dark Yelllow on Pink
                * 'D7': Dark White on Pink
                * 'D8': Dark Grey on Pink
                * 'D9': Dark Blue on Pink
                * 'DA': Bright Green on Pink
                * 'DB': Bright Cyan on Pink
                * 'DC': Bright Red on Pink
                * 'DD': Bright Magenta on Pink
                * 'DE': Bright Yellow on Pink
                * 'DF': Bright White on Pink
                * 'Dr': Default Colour on Pink
                * 'E0': Dark Black on Bright Yellow
                * 'E1': Dark Blue on Bright Yellow
                * 'E2': Dark Green on Bright Yellow
                * 'E3': Dark Cyan on Bright Yellow
                * 'E4': Dark Red on Bright Yellow
                * 'E5': Dark Magenta on Bright Yellow
                * 'E6': Dark Yelllow on Bright Yellow
                * 'E7': Dark White on Bright Yellow
                * 'E8': Dark Grey on Bright Yellow
                * 'E9': Dark Blue on Bright Yellow
                * 'EA': Bright Green on Bright Yellow
                * 'EB': Bright Cyan on Bright Yellow
                * 'EC': Bright Red on Bright Yellow
                * 'ED': Bright Magenta on Bright Yellow
                * 'EE': Bright Yellow on Bright Yellow
                * 'EF': Bright White on Bright Yellow
                * 'Er': Default Colour on Bright Yellow
                * 'F0': Dark Black on Bright White
                * 'F1': Dark Blue on Bright White
                * 'F2': Dark Green on Bright White
                * 'F3': Dark Cyan on Bright White
                * 'F4': Dark Red on Bright White
                * 'F5': Dark Magenta on Bright White
                * 'F6': Dark Yelllow on Bright White
                * 'F7': Dark White on Bright White
                * 'F8': Dark Grey on Bright White
                * 'F9': Dark Blue on Bright White
                * 'FA': Bright Green on Bright White
                * 'FB': Bright Cyan on Bright White
                * 'FC': Bright Red on Bright White
                * 'FD': Bright Magenta on Bright White
                * 'FE': Bright Yellow on Bright White
                * 'FF': Bright White on Bright White
                * 'Fr': Default Colour on Bright White
                * 'r0': Dark Black on Default Background
                * 'r1': Dark Blue on Default Background
                * 'r2': Dark Green on Default Background
                * 'r3': Dark Cyan on Default Background
                * 'r4': Dark Red on Default Background
                * 'r5': Dark Magenta on Default Background
                * 'r6': Dark Yelllow on Default Background
                * 'r7': Dark White on Default Background
                * 'r8': Dark Grey on Default Background
                * 'r9': Dark Blue on Default Background
                * 'rA': Bright Green on Default Background
                * 'rB': Bright Cyan on Default Background
                * 'rC': Bright Red on Default Background
                * 'rD': Bright Magenta on Default Background
                * 'rE': Bright Yellow on Default Background
                * 'rF': Bright White on Default Background
                * 'rr': Default Colour on Default Background
        __returns__
            Nothing
        """
        processed_attributes = self.process_attributes(attributes)
        if self.colourise_output is True:
            try:
                tmp_msg = f"{processed_attributes}"
                tmp_msg += f"{self.unix_colour_pallet[colour]}{text}"
                print(
                    tmp_msg,
                    end="",
                    file=self.output
                )
            except IOError:
                if self.wich_system == "Windows":
                    os.system(f"{self.colour_pallet[colour]}")
                    if len(text) > 0:
                        print(f"{text}", end="", file=self.output)
                else:
                    tmp_msg = f"echo -e \"{self.colour_pallet[colour]}"
                    tmp_msg += f"{processed_attributes}{text}\""
                    os.system(tmp_msg)

    def load_for_windows(self) -> None:
        """ Prepare the Windows colour pallet """
        for i in "0123456789ABCDEFr":
            for j in "0123456789ABCDEFr":
                if i == 'r':
                    if j == 'r':
                        self.colour_pallet[f"{i}{j}"] = "color 0A"
                    else:
                        self.colour_pallet[f"{i}{j}"] = f"color 0{j}"
                elif j == 'r':
                    self.colour_pallet[f"{i}{j}"] = f"color {i}A"
                else:
                    self.colour_pallet[f"{i}{j}"] = f"color {i}{j}"

    def load_for_non_windows(self) -> None:
        """ Prepare the non Windows colour pallet """
        color_list = [
            "0 = 30", "1 = 34", "2 = 32", "3 = 36", "4 = 31", "5 = 35", "6 = 33", "7 = 37",
            "8 = 90", "9 = 94", "a = 92", "b = 96", "c = 91", "d = 95", "e = 93", "f = 97", "0"
        ]
        color_list = [
            "30", "34", "32", "36", "31", "35", "33", "37",
            "90", "94", "92", "96", "91", "95", "93", "97", "0"
        ]
        i = j = 0
        for foreground in "0123456789ABCDEFr":
            j = 0
            for background in "0123456789ABCDEFr":
                self.colour_pallet[
                    f"{background}{foreground}"
                ] = f"\\e[{int(color_list[j])+10}m\\e[{color_list[i]}m"
                self.unix_colour_pallet[
                    f"{background}{foreground}"
                ] = f"\033[{int(color_list[j])+10}m\033[{color_list[i]}m"
                j += 1
            i += 1

    def init_pallet(self) -> int:
        """ Prepare and load an intersystem pallet based on the Windows colour format """
        try:
            COC.reinit()
            self.load_for_non_windows()
            if self.wich_system == "Windows":
                self.load_for_windows()
            return self.success
        except IOError:
            return self.error

    def unload_ressources(self) -> int:
        """ Free the ressources that can be freed """
        try:
            COC.deinit()
            return self.success
        except IOError:
            return self.error

    def test_desing(self) -> None:
        """_summary_
        Test the different design attributes
        """
        self.display(
            "0A",
            UNDERLINE,
            "Diplaying all available attributes\n"
        )
        counter = 0
        attribute_list = [
            ALL, BOLD, DIM, ITALIC,
            UNDERLINE, BLINK, INVERT,
            CONCEALED, STRIKE,
            (BOLD, DIM),
            (BOLD, ITALIC),
            (BOLD, UNDERLINE),
            (BOLD, BLINK),
            (BOLD, INVERT),
            (BOLD, CONCEALED),
            (BOLD, STRIKE),
            (ITALIC, DIM),
            (ITALIC, BLINK),
            (ITALIC, STRIKE),
            (ITALIC, INVERT),
            (ITALIC, UNDERLINE),
            (ITALIC, CONCEALED),
            (UNDERLINE, DIM),
            (UNDERLINE, BLINK),
            (UNDERLINE, STRIKE),
            (UNDERLINE, INVERT),
            (UNDERLINE, CONCEALED),
            (BOLD, ITALIC, UNDERLINE)
        ]
        for attributes in attribute_list:
            counter += 1
            self.display("rr", (), "")
            self.display("0A", (), "Current attribute: '")
            self.display("0A", ITALIC, f"{attributes}")
            self.display("rr", (), "")
            self.display("0A", (), "' -> '")
            self.display("0A", attributes, "Sample Text")
            self.display("rr", (), "")
            self.display("0A", (), "'")
            self.display("rr", (), "\n")
        self.display(
            "rr",
            (),
            f"{counter} Attributes displayed.\n"
        )

    def test_colours(self) -> None:
        """ Display all the available colours and their code """
        self.display(
            "0A",
            UNDERLINE,
            "Displaying all available colours:"
        )
        counter = 0
        for background in "0123456789ABCDEFr":
            for foreground in "0123456789ABCDEFr":
                counter += 1
                self.display("rr", (), "\n")
                self.display(
                    f"{background}{foreground}",
                    (),
                    f"Current colour: '{background}{foreground}'"
                )
        self.display(
            "rr", (), f"\n{counter} Colours displayed.\n"
        )


if __name__ == '__main__':
    CI = ColouriseOutput()
    CI.init_pallet()
    CI.test_desing()
    print("\n")
    CI.test_colours()
    CI.display("0A", (), "Hello World !\n")
    CI.display("rr", "")
    CI.unload_ressources()
    print(f"Created by {CI.author}")
