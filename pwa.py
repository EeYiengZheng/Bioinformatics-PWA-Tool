"""
cs 123a bioinformatics

ee yieng zheng, raymond hong
"""

from enum import Enum


class Type(Enum):
    NUCLEOTIDE = 1
    PROTEIN = 2


class PWA(object):
    """
    Pairwise Alignment of FASTA sequences using
    the Needleman Wunsch algorithm

    supports nucleotide or peptide comparison
    """

    def __init__(self, alignment_type: Type, fasta: str):
        """
        Assuming all inputs are valid FASTA-string
        and using linux \n EOL
        :param alignment_type: the Type (Enum) of alignment
        :param seq1: FASTA sequences
        """
        self.alignment_type = alignment_type
        self.fasta_string = fasta.replace(" ", "")
        self.fasta_list = self.__to_list(fasta)
        self.traced_path = None
        self.aligned_sequences = None
        self.__matrix = [[" ", " "],
                       [" "]]

        if len(self.fasta_list) < 2:
            raise ValueError("Need at least 2 FASTA sequences")

    def do_alignment(self, match=1, mismatch=-1, gap=-2):
        """
        performs pairwise alignment of two sequences and the traced path string at self.traced_path
        :param match: positive score for matching bit
        :param mismatch: negative score for mismatching bit
        :param gap: negative score for gap-penalty
        :return: void
        """
        if self.alignment_type == Type.NUCLEOTIDE:
            self.traced_path = self.__align_nuc(match, mismatch, gap)
            self.aligned_sequences = self.__insert_indel()

        elif self.alignment_type == Type.PROTEIN:
            self.traced_path = self.__align_pro(match, mismatch, gap)
        else:
            raise AttributeError("non-supported alignment Type. Supports: ", [t for t in Type])

    def get_best_score(self):
        end = self.__matrix[-1][-1]
        return end[0]

    def print_aligned_seq(self):
        if self.aligned_sequences:
            print(self.aligned_sequences[0])
            print(self.aligned_sequences[1])

    def print_pretty(self, separator=' '):
        print("rows: ", len(self.__matrix), "\ncolumns: ", len(self.__matrix[0]), "\n")
        for row in self.__matrix:
            if isinstance(row[0], str):
                print(separator.join(str(c) for c in row))

    def __align_nuc(self, match, mismatch, gap):
        # copy the first 2 sequences to the matrix table
        seq1 = self.__strip_fasta_comment(self.fasta_list[0])
        seq2 = [list(c) for c in list(self.__strip_fasta_comment(self.fasta_list[1]))]
        self.__matrix[0].extend(list(seq1))
        self.__matrix.extend(seq2)

        # initialize gap penalty
        self.__matrix[1].append((0, 'd')) # 0 at row 2 column 2
        for i in range(1, len(seq1)+1):
            self.__matrix[1].append((i * gap, 'w'))
        for i in range(len(seq2)):
            self.__matrix[i+2].append(((i + 1) * gap, 'n'))

        # the algorithm part
        for row in range(len(seq2)):
            for col in range(len(seq1)):
                # diagonal (northwest)
                diag = self.__matrix[row+1][col+1]
                d = (diag[0] + (match if (self.__matrix[0][col+2] == self.__matrix[row+2][0]) else mismatch), 'd')

                # north and west
                north = self.__matrix[row+1][col+2]
                n = (north[0] + gap, 'n')

                west = (self.__matrix[row+2])[col+1]
                w = (west[0] + gap, 'w')

                # comparison
                m = d[0]
                if n[0] > m:
                    m = n[0]
                if w[0] > m:
                    m = w[0]

                best = filter(lambda tup: tup[0] == m, [d, n, w])
                arrow = ""
                for a in best:
                    arrow += a[1]

                self.__matrix[row+2].append((m, arrow))
        # trace back
        row = len(self.__matrix) - 1
        col = len(self.__matrix[0]) - 1
        path = self.__trace_back(row, col)
        return path

    def __align_pro(self, match, mismatch, gap):

        return ''

    def __trace_back(self, row, col):
        if row == 1 and col == 1:
            return ''
        score, path = self.__matrix[row][col]
        p = path[0]
        if p is 'd':
            t = self.__trace_back(row-1, col-1)
        elif p is 'n':
            t = self.__trace_back(row-1, col)
        elif p is 'w':
            t = self.__trace_back(row, col-1)
        else:
            raise RuntimeError("No path found. CHECK YOUR PWA ALGORITHM!!")

        return t + p

    def __insert_indel(self):
        """
        generate aligned sequences with indel insertion.
        by default uses the object's generated path
        :param path: a path different from the one generated by the algorithm
        :return: a list of aligned sequences by descending FASTA text
        """
        seq1 = ""
        seq2 = ""

        i = len(self.__matrix[0]) - 1
        j = len(self.__matrix) - 1
        for p in list(self.traced_path[::-1]):
            top = self.__matrix[0][i]
            bot = self.__matrix[j][0]
            if p is 'd':
                seq1 = top + seq1
                seq2 = bot + seq2
                i -= 1
                j -= 1
            elif p is 'n':
                seq1 = '-' + seq1
                seq2 = bot + seq2
                j -= 1
            elif p is 'w':
                seq1 = top + seq1
                seq2 = '-' + seq2
                i -= 1
            else:
                raise RuntimeError("traced path string contains invalid character. CHECK YOUR PWA ALGORITHM!!")

        return [seq1, seq2]

    def __to_list(self, seq: str):
        fastas = list()
        buffer = ""
        for line in seq.replace('\\n', '\n').splitlines():
            if line.startswith('>'):
                buffer = line
            else:
                fastas.append(buffer + "\n" + line)
        return fastas

    def __get_fasta_comment(self, seq: str):
        """
        find and return the FASTA comment from a single FASTA sequence
        :param seq: sequence
        :return: FASTA comment with a leading > and without the sequence
        """
        if seq.startswith('>'):
            return seq[:seq.find("\n")]
        else:
            return '>'

    def __strip_fasta_comment(self, seq: str):
        """
        remove the leading FASTA comment from a single FASTA sequence string
        :param seq: input sequence
        :return: sequence with FASTA comment removed
        """
        return seq.lstrip(self.__get_fasta_comment(seq)).strip()


if __name__ == '__main__':
    sequences = input("FASTA:\n")
    pwa = PWA(Type.NUCLEOTIDE, sequences)
    pwa.do_alignment()

    # pwa.print_pretty()
    # pwa.print_aligned_seq()

    """ 
    # check score 
    
    print("score: ", pwa.get_best_score())
    
    score = 0
    for i in range(len(pwa.aligned_sequences[0])):
        top = pwa.aligned_sequences[0][i]
        bot = pwa.aligned_sequences[1][i]
        if top is '-' or bot is '-':
            score += -2
        elif top is bot:
            score += 1
        elif top is not bot:
            score += -1
    print(score)
    """
