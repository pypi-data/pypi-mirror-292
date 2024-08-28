# -*- coding: utf-8 -*-

import argparse
import os
import sys
import warnings

import openpyxl
from verbecc import Conjugator


def remove_suj(conj):
    modes = list(conj.keys())
    for each_mode in modes:
        verb_times = list(conj[each_mode].keys())
        for each_verb_time in verb_times:
            conj[each_mode][each_verb_time]
            conj[each_mode][each_verb_time] = [
                s.replace('yo ', '') for s in conj[each_mode][each_verb_time]
            ]
            conj[each_mode][each_verb_time] = [
                s.replace('tú ', '') for s in conj[each_mode][each_verb_time]
            ]
            conj[each_mode][each_verb_time] = [
                s.replace('él ', '') for s in conj[each_mode][each_verb_time]
            ]
            conj[each_mode][each_verb_time] = [
                s.replace('nosotros ', '')
                for s in conj[each_mode][each_verb_time]
            ]
            conj[each_mode][each_verb_time] = [
                s.replace('vosotros ', '')
                for s in conj[each_mode][each_verb_time]
            ]
            conj[each_mode][each_verb_time] = [
                s.replace('ellos ', '')
                for s in conj[each_mode][each_verb_time]
            ]

    return conj


def get_verb_time(conj, verb):
    modes = list(conj.keys())
    modes_match = []
    verb_times_match = []
    pers_match = []
    for each_mode in modes:
        verb_times = list(conj[each_mode].keys())
        for each_verb_time in verb_times:
            for i in range(len(conj[each_mode][each_verb_time])):
                if (
                    each_mode == 'gerundio' or each_mode == 'infinitivo'
                ) and i > 0:
                    break
                if conj[each_mode][each_verb_time][i] == verb:
                    pers_match.append(i + 1)
                    verb_times_match.append(each_verb_time)
                    modes_match.append(each_mode)

    return modes_match, verb_times_match, pers_match


def getKcell(mode):
    if mode == 'subjuntivo':
        return 1
    elif mode == 'imperativo':
        return 2
    else:
        return 0


def getLcell(mode, verb_time):
    if verb_time == 'presente':
        return 0
    elif 'pretérito' in verb_time:
        if 'imperfecto' in verb_time:
            return 2
        else:
            return 1
    elif 'futuro' in verb_time:
        return 3
    elif mode == 'condicional':
        return 5


def getMcell(verb_time):
    if verb_time == 'gerundio':
        return 1
    else:
        return 0


def getNcell(verb_time):
    if (
        'perfecto' in verb_time
        and 'imperfecto' not in verb_time
        and 'simple' not in verb_time
    ):
        return 1
    else:
        return 0


def main(args):
    warnings.filterwarnings('ignore')
    # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'

    color = openpyxl.styles.colors.Color(rgb='bce4e5')
    fill = openpyxl.styles.fills.PatternFill(
        patternType='solid', fgColor=color
    )

    workbook = openpyxl.load_workbook(filename=args.file_name)

    # sheet_verbs = workbook['VERBOS']

    # cell_number = '2'
    # cell_letter = 'A'
    # P0 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P0.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    # cell_letter = 'B'
    # P1 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P1.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    # cell_letter = 'C'
    # P2 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P2.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    # cell_letter = 'D'
    # P3 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P3.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    # cell_letter = 'E'
    # P4 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P4.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    # cell_letter = 'F'
    # P5 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P5.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    # cell_letter = 'G'
    # P6 = []
    # verb = sheet_verbs[cell_letter + cell_number].value
    # while type(verb) != type(None):
    #     P6.append(verb)
    #     cell_number = chr(ord(cell_number)+1)
    #     verb = sheet_verbs[cell_letter + cell_number].value

    cell_letter = args.init_cell[0]
    cell_number = args.init_cell[1:]
    sheet = workbook['LINGÜÍSTICAS']
    cg = Conjugator(lang='es')

    verb = sheet[cell_letter + cell_number].value
    infinitive = sheet[chr(ord(cell_letter) + 1) + cell_number].value
    empty_cell = sheet[chr(ord(cell_letter) + 2) + cell_number].value

    while verb and not empty_cell:
        if infinitive:
            try:
                conjugation = cg.conjugate(str(infinitive))
                conj = conjugation['moods']
                conj = remove_suj(conj)

                modes_match, verb_times_match, pers_match = get_verb_time(
                    conj, verb
                )
                infinitive = conj['infinitivo']['infinitivo'][0]

                Gcell = None
                for each in pers_match:
                    if type(Gcell) == type(None):
                        Gcell = each
                    elif Gcell != each:
                        Gcell = str(Gcell) + '/' + str(each)

                Kcell = None
                for each in modes_match:
                    if type(Kcell) == type(None):
                        Kcell = getKcell(each)
                    elif Kcell != getKcell(each):
                        Kcell = str(Kcell) + '/' + str(getKcell(each))

                Lcell = None
                for each_verb_time, each_mode in zip(
                    verb_times_match, modes_match
                ):
                    if type(Lcell) == type(None):
                        Lcell = getLcell(each_mode, each_verb_time)
                    elif Lcell != getLcell(each_mode, each_verb_time):
                        Lcell = (
                            str(Lcell)
                            + '/'
                            + str(getLcell(each_mode, each_verb_time))
                        )

                Mcell = None
                for each in verb_times_match:
                    if type(Mcell) == type(None):
                        Mcell = getMcell(each)
                    elif Mcell != getMcell(each):
                        Mcell = str(Mcell) + '/' + str(getMcell(each))

                Ncell = None
                for each in verb_times_match:
                    if type(Ncell) == type(None):
                        Ncell = getNcell(each)
                    elif Ncell != getNcell(each):
                        Ncell = str(Ncell) + '/' + str(getNcell(each))

                if len(modes_match) > 1:
                    Ocell = 1
                else:
                    Ocell = 0

                #         if infinitive in P0:
                #             Pcell = 0
                #         elif infinitive in P1:
                #             Pcell = 1
                #         elif infinitive in P2:
                #             Pcell = 2
                #         elif infinitive in P3:
                #             Pcell = 3
                #         elif infinitive in P4:
                #             Pcell = 4
                #         elif infinitive in P5:
                #             Pcell = 5
                #         elif infinitive in P6:
                #             Pcell = 6
                #         else:
                #             Pcell = -1

                sheet[chr(ord(cell_letter) + 3) + cell_number].value = str(
                    Gcell
                )
                sheet[chr(ord(cell_letter) + 7) + cell_number].value = str(
                    Kcell
                )
                sheet[chr(ord(cell_letter) + 8) + cell_number].value = str(
                    Lcell
                )
                sheet[chr(ord(cell_letter) + 9) + cell_number].value = str(
                    Mcell
                )
                sheet[chr(ord(cell_letter) + 10) + cell_number].value = str(
                    Ncell
                )
                sheet[chr(ord(cell_letter) + 11) + cell_number].value = str(
                    Ocell
                )
                #         sheet[chr(ord(cell_letter)+12) + cell_number].value = str(Pcell)

                if args.color:
                    sheet[chr(ord(cell_letter) + 3) + cell_number].fill = fill
                    sheet[chr(ord(cell_letter) + 7) + cell_number].fill = fill
                    sheet[chr(ord(cell_letter) + 8) + cell_number].fill = fill
                    sheet[chr(ord(cell_letter) + 9) + cell_number].fill = fill
                    sheet[chr(ord(cell_letter) + 10) + cell_number].fill = fill
                    sheet[chr(ord(cell_letter) + 11) + cell_number].fill = fill
                    sheet[chr(ord(cell_letter) + 12) + cell_number].fill = fill

                print(' ')
                print(verb)
                print(infinitive)

            except:
                pass

        cell_number = str(int(cell_number) + 1)
        verb = sheet[cell_letter + cell_number].value
        infinitive = sheet[chr(ord(cell_letter) + 1) + cell_number].value

    workbook.save(filename=args.file_name)


if __name__ == '__main__':
    # Running the script as python ... is deprecated
    parser = argparse.ArgumentParser(
        description='Automated codification program'
    )
    parser.add_argument(
        '-color', action='store_true', help='color automated cells'
    )
    parser.add_argument(
        '-file_name',
        default='PRESEEA_1995_Nivel_bajo.xlsx',
        help='Excel file name',
    )
    parser.add_argument(
        '-init_cell', default='D2', help='Initial cell with verb'
    )
    args = parser.parse_args()
    main(args)
