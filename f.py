import argparse
import re
from typing import List
from rapidfuzz import fuzz, process
from unidecode import unidecode

class LaboArticleMatcher:
    def __init__(self, deno_labo_path, deno_sap_path, output_path):
        self.deno_labo_path = deno_labo_path
        self.deno_sap_path = deno_sap_path
        self.output_path = output_path
        self.lines_zmmartstam_denom = []
        self.lines_zmmartstam_matnr = []
        self.lines_result = []

    def load_sap_data(self):
        with open(self.deno_sap_path, encoding="utf8") as f_denomination_sap:
            for line_zmmartstam in f_denomination_sap:
                line_zmmartstam = line_zmmartstam.strip().split("\t")
                self.lines_zmmartstam_denom.append(line_zmmartstam[1])
                self.lines_zmmartstam_matnr.append(line_zmmartstam[0])

    def preprocess_text(self, text):
        text = text.upper()
        text = unidecode(text)
        text = re.sub('[^0-9A-Z]*', '', text)
        return text

    def calculate_levenshtein_distance(self, query, choices):
        return process.extractOne(query, choices, scorer=fuzz.ratio)[1]

    def process_labo_data(self):
        with open(self.deno_labo_path, encoding="utf8") as f_denomination_labo:
            for line_feuil1 in f_denomination_labo:
                line_feuil1 = line_feuil1.strip().split("\t")

                if len(line_feuil1) < 3:
                    id_prod, labo = line_feuil1[0], line_feuil1[1]
                    self.lines_result.append(f"{id_prod}\t{labo}\t\t\t\t1,00\n")
                    continue

                query = self.preprocess_text(line_feuil1[2])
                levenshtein_val = self.calculate_levenshtein_distance(query, self.lines_zmmartstam_denom)
                ind_min = self.lines_zmmartstam_denom.index(
                    process.extractOne(query, self.lines_zmmartstam_denom, scorer=fuzz.ratio)[0])

                self.lines_result.append(
                    f"{line_feuil1[0]}\t{line_feuil1[1]}\t{line_feuil1[2]}\t"
                    f"{self.lines_zmmartstam_matnr[ind_min]}\t{self.lines_zmmartstam_denom[ind_min]}\t{levenshtein_val:.2f}\n")

    def write_output(self):
        with open(self.output_path, "w", encoding="utf8") as f_result:
            f_result.writelines(self.lines_result)

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fullpath_denomination_labo",
                        help="chemin complet du fichier de dénomination des articles de labos", type=str)
    parser.add_argument("--fullpath_denomination_sap",
                        help="chemin complet du fichier de dénomination des articles dans sap", type=str)
    parser.add_argument("--fullpath_output",
                        help="chemin complet du fichier de sortie donnant la distance de levenshtein pour chaque ligne d'article de labo",
                        type=str)
    return parser.parse_args()

def main():
    args = get_arguments()
    matcher = LaboArticleMatcher(args.fullpath_denomination_labo, args.fullpath_denomination_sap, args.fullpath_output)
    matcher.load_sap_data()
    matcher.process_labo_data()
    matcher.write_output()

if __name__ == "__main__":
    main()
