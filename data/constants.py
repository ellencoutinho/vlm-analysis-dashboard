import glob

json_files = glob.glob("runs/*.json")

question_type_map = {
    "U": "Compreensão Básica",
    "A": "Atribuição",
    "F": "Previsão de Eventos",
    "R": "Raciocínio Reversivo",
    "C": "Inferência Contrafactual",
    "I": "Introspecção"
}