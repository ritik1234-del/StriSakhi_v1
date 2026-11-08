"""Build the two law documents StriSakhi will search.

  data/library/BNS_women_safety.json      offences (Bharatiya Nyaya Sanhita, 2023)
  data/library/BNSS_BSA_procedure.json    police/court steps (BNSS 2023) and evidence rules (BSA 2023)

HOW IT WORKS
  1. parse_acts.py cuts the official gazette PDFs into sections (exact words).
  2. This file lists WHICH sections matter for women, and adds our own helper
     labels. Helper labels are NOT law - the "text" field is the only law.
  3. We save everything as JSON, with the page number in the gazette PDF.

Run:  python src/build_law_library.py
"""
import json
from datetime import date
from pathlib import Path

from parse_acts import parse_act

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "library"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LAW_NAMES = {
    "BNS": "Bharatiya Nyaya Sanhita, 2023",
    "BNSS": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "BSA": "Bharatiya Sakshya Adhiniyam, 2023",
}
GAZETTE_URL = {
    "BNS": "https://egazette.gov.in/WriteReadData/2023/250883.pdf",
    "BNSS": "https://egazette.gov.in/WriteReadData/2023/250884.pdf",
    "BSA": "https://egazette.gov.in/WriteReadData/2023/250882.pdf",
}

# Each row: section number -> (plain label in English, short Hindi name or "", topic tag)
# Labels were written by us after reading the section text. They only help searching.
BNS = {
    34: ("Nothing is an offence if done in private defence", "", "self-defence"),
    35: ("Right of private defence of body and property", "आत्मरक्षा का अधिकार", "self-defence"),
    37: ("Acts against which there is no right of private defence", "", "self-defence"),
    38: ("When private defence of the body may extend to causing death", "आत्मरक्षा में मृत्यु तक", "self-defence"),
    63: ("Rape - definition", "बलात्कार की परिभाषा", "sexual offences"),
    64: ("Punishment for rape", "बलात्कार की सज़ा", "sexual offences"),
    65: ("Punishment for rape in certain cases (younger victims)", "", "sexual offences"),
    66: ("Rape causing death or persistent vegetative state", "", "sexual offences"),
    67: ("Sexual intercourse by husband upon wife during separation", "", "sexual offences"),
    68: ("Sexual intercourse by a person in authority", "", "sexual offences"),
    69: ("Sexual intercourse by deceitful means (including false promise of marriage)", "धोखे से यौन संबंध / शादी का झूठा वादा", "sexual offences"),
    70: ("Gang rape", "सामूहिक बलात्कार", "sexual offences"),
    71: ("Punishment for repeat offenders", "", "sexual offences"),
    72: ("Disclosing the identity of a victim of certain offences", "पीड़िता की पहचान उजागर करना", "privacy"),
    73: ("Printing or publishing court proceedings without permission", "", "privacy"),
    74: ("Assault or criminal force to a woman to outrage her modesty", "महिला की लज्जा भंग करने के इरादे से हमला", "harassment"),
    75: ("Sexual harassment", "यौन उत्पीड़न", "harassment"),
    76: ("Assault or criminal force to a woman with intent to disrobe her", "वस्त्र उतारने के इरादे से हमला", "harassment"),
    77: ("Voyeurism", "चोरी-छिपे देखना / तस्वीर या वीडियो बनाना", "harassment"),
    78: ("Stalking", "पीछा करना (स्टॉकिंग)", "harassment"),
    79: ("Word, gesture or act intended to insult the modesty of a woman", "महिला का अपमान करने वाले शब्द या इशारे", "harassment"),
    80: ("Dowry death", "दहेज हत्या", "dowry and marriage"),
    81: ("Cohabitation by a man deceitfully inducing belief of lawful marriage", "", "dowry and marriage"),
    82: ("Marrying again during the lifetime of husband or wife (bigamy)", "दूसरी शादी (द्विविवाह)", "dowry and marriage"),
    83: ("Fraudulent marriage ceremony without a lawful marriage", "", "dowry and marriage"),
    84: ("Enticing or taking away a married woman with criminal intent", "", "dowry and marriage"),
    85: ("Cruelty by husband or his relatives", "पति या ससुराल वालों की क्रूरता", "dowry and marriage"),
    86: ("Cruelty defined (includes harassment to force an unlawful demand for property)", "क्रूरता की परिभाषा", "dowry and marriage"),
    87: ("Kidnapping or abducting a woman to compel her to marry", "शादी के लिए अपहरण", "kidnapping"),
    88: ("Causing miscarriage", "गर्भपात कराना", "pregnancy"),
    89: ("Causing miscarriage without the woman's consent", "बिना सहमति गर्भपात", "pregnancy"),
    90: ("Death caused by an act done to cause miscarriage", "", "pregnancy"),
    91: ("Act done to prevent a child being born alive or to cause its death after birth", "", "pregnancy"),
    92: ("Causing death of a quick unborn child by an act amounting to culpable homicide", "", "pregnancy"),
    93: ("Exposure and abandonment of a child under twelve by parent or carer", "", "children"),
    94: ("Concealment of birth by secretly disposing of a dead body", "", "children"),
    95: ("Hiring or engaging a child to commit an offence", "", "children"),
    96: ("Procuration of a child", "", "children"),
    97: ("Kidnapping or abducting a child under ten to steal from its person", "", "children"),
    98: ("Selling a child for prostitution", "", "children"),
    99: ("Buying a child for prostitution", "", "children"),
    107: ("Abetment of suicide of a child or person of unsound mind", "", "suicide"),
    108: ("Abetment of suicide", "आत्महत्या के लिए उकसाना", "suicide"),
    115: ("Voluntarily causing hurt", "जानबूझकर चोट पहुँचाना", "hurt and violence"),
    116: ("Grievous hurt - definition", "गंभीर चोट", "hurt and violence"),
    117: ("Voluntarily causing grievous hurt", "", "hurt and violence"),
    118: ("Hurt or grievous hurt by dangerous weapons or means", "", "hurt and violence"),
    123: ("Causing hurt by poison or stupefying drug to commit an offence", "", "hurt and violence"),
    124: ("Acid attack - grievous hurt by acid, and throwing or attempting to throw acid", "एसिड हमला", "hurt and violence"),
    126: ("Wrongful restraint", "रास्ता रोकना", "restraint"),
    127: ("Wrongful confinement", "बंधक बनाकर रखना", "restraint"),
    129: ("Criminal force", "", "hurt and violence"),
    130: ("Assault", "", "hurt and violence"),
    131: ("Punishment for assault or criminal force", "मारपीट की सज़ा", "hurt and violence"),
    133: ("Assault or criminal force with intent to dishonour a person", "", "hurt and violence"),
    137: ("Kidnapping", "अपहरण", "kidnapping"),
    138: ("Abduction", "", "kidnapping"),
    141: ("Importation of a girl or boy from a foreign country", "", "trafficking"),
    143: ("Trafficking of person", "मानव तस्करी", "trafficking"),
    144: ("Exploitation of a trafficked person", "", "trafficking"),
    200: ("Non-treatment of victim by a hospital", "पीड़िता का इलाज न करना", "victim rights"),
    351: ("Criminal intimidation (threats)", "धमकी देना", "threats"),
    352: ("Intentional insult with intent to provoke breach of peace", "", "threats"),
}

BNSS = {
    36: ("Procedure of arrest and duties of the officer making an arrest", "", "arrest"),
    43: ("How arrest is made (includes rules for arresting women)", "गिरफ़्तारी कैसे होती है", "arrest"),
    144: ("Order for maintenance of wives, children and parents", "पत्नी, बच्चों और माता-पिता का भरण-पोषण", "maintenance"),
    145: ("Procedure for maintenance orders", "", "maintenance"),
    146: ("Alteration in maintenance allowance", "", "maintenance"),
    147: ("Enforcement of maintenance order", "", "maintenance"),
    173: ("Information in cognizable cases - FIR, Zero FIR, e-FIR", "एफ़आईआर दर्ज कराना / ज़ीरो एफ़आईआर", "complaint and FIR"),
    175: ("Police officer's power to investigate a cognizable case", "", "complaint and FIR"),
    176: ("Procedure for investigation", "", "complaint and FIR"),
    179: ("Police power to require attendance of witnesses (limits for women)", "थाने बुलाने की सीमा", "complaint and FIR"),
    180: ("Examination of witnesses by police", "", "complaint and FIR"),
    183: ("Recording of confessions and statements before a Magistrate", "मजिस्ट्रेट के सामने बयान", "complaint and FIR"),
    184: ("Medical examination of the victim of rape", "बलात्कार पीड़िता की मेडिकल जाँच", "medical and victim support"),
    193: ("Police report on completion of investigation (time limit for rape cases)", "जाँच पूरी होने की रिपोर्ट", "complaint and FIR"),
    194: ("Police to enquire and report on suicide, etc.", "", "suicide"),
    196: ("Inquiry by Magistrate into cause of death", "", "suicide"),
    366: ("Court to be open - closed-door trial for rape cases", "बलात्कार के मामलों की बंद कमरे में सुनवाई", "court"),
    396: ("Victim compensation scheme", "पीड़ित को मुआवज़ा", "medical and victim support"),
    397: ("Treatment of victims - free treatment in hospitals", "पीड़िता का मुफ़्त इलाज", "medical and victim support"),
    398: ("Witness protection scheme", "गवाह सुरक्षा", "court"),
}

BSA = {
    48: ("Evidence about the character of the victim in sexual offence cases", "", "evidence"),
    117: ("Presumption as to abetment of suicide by a married woman", "विवाहित महिला की आत्महत्या में उकसावे का अनुमान", "evidence"),
    118: ("Presumption as to dowry death", "दहेज हत्या का अनुमान", "evidence"),
    120: ("Presumption as to absence of consent in certain rape cases", "सहमति न होने का अनुमान", "evidence"),
}

# Old-law hints: ONLY pairs that two or more sources agree on. Marked "to verify".
OLD_LAW_HINT = {
    ("BNS", 63): "IPC 375", ("BNS", 64): "IPC 376", ("BNS", 74): "IPC 354",
    ("BNS", 79): "IPC 509", ("BNS", 80): "IPC 304B", ("BNS", 85): "IPC 498A",
    ("BNS", 351): "IPC 506",
}


def build(code, wanted, filename, source_list):
    """Cut the wanted sections out of an Act and return their records."""
    sections = {s["section"]: s for s in parse_act(code)}
    records = []
    for number, (label, label_hi, topic) in wanted.items():
        s = sections[number]
        records.append({
            "id": f"{code}-{number}",
            "law": LAW_NAMES[code],
            "law_short": code,
            "section": str(number),
            "label_en": label,
            "label_hi": label_hi,
            "topic": topic,
            "chapter": s["chapter"],
            "gazette_pdf_page": s["page"],
            "old_law_hint": OLD_LAW_HINT.get((code, number), ""),
            "text": s["text"],
        })
    return records


def save(filename, title, description, records, sources):
    doc = {
        "title": title,
        "description": description,
        "built_on": date.today().isoformat(),
        "sources": sources,
        "warning": ("The 'text' field is copied word-for-word from the official gazette. "
                    "Fields label_en, label_hi, topic and old_law_hint are helper notes "
                    "added by us; they are not law. old_law_hint is TO VERIFY. "
                    "This is legal information, not legal advice."),
        "sections": records,
    }
    path = OUT_DIR / filename
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {path.name}: {len(records)} sections")


def main():
    bns = build("BNS", BNS, "", None)
    save("BNS_women_safety.json",
         "Bharatiya Nyaya Sanhita, 2023 - sections that matter for women's safety",
         "Offences (in force from 1 July 2024; replaced the Indian Penal Code, 1860).",
         bns, [{"law": LAW_NAMES["BNS"], "official_pdf": GAZETTE_URL["BNS"]}])

    procedure = build("BNSS", BNSS, "", None) + build("BSA", BSA, "", None)
    save("BNSS_BSA_procedure.json",
         "BNSS 2023 and BSA 2023 - how to complain, how cases run, and evidence rules",
         "BNSS replaced the Code of Criminal Procedure, 1973. BSA replaced the Indian Evidence Act, 1872. "
         "Both in force from 1 July 2024.",
         procedure,
         [{"law": LAW_NAMES["BNSS"], "official_pdf": GAZETTE_URL["BNSS"]},
          {"law": LAW_NAMES["BSA"], "official_pdf": GAZETTE_URL["BSA"]}])


if __name__ == "__main__":
    main()
