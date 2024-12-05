# Simpele rekenmachine

def calculator():
    print("Welkom bij de simpele rekenmachine!")
    print("Kies een bewerking:")
    print("1. Optellen")
    print("2. Aftrekken")
    print("3. Vermenigvuldigen")
    print("4. Delen")

    # Vraag de gebruiker om een keuze
    keuze = input("Voer je keuze in (1/2/3/4): ")

    # Vraag de gebruiker om twee nummers
    try:
        nummer1 = float(input("Voer het eerste nummer in: "))
        nummer2 = float(input("Voer het tweede nummer in: "))
    except ValueError:
        print("Voer een geldig nummer in.")
        return

    # Voer de bewerking uit
    if keuze == "1":
        print(f"Resultaat: {nummer1} + {nummer2} = {nummer1 + nummer2}")
    elif keuze == "2":
        print(f"Resultaat: {nummer1} - {nummer2} = {nummer1 - nummer2}")
    elif keuze == "3":
        print(f"Resultaat: {nummer1} * {nummer2} = {nummer1 * nummer2}")
    elif keuze == "4":
        if nummer2 != 0:
            print(f"Resultaat: {nummer1} / {nummer2} = {nummer1 / nummer2}")
        else:
            print("Fout: Delen door nul is niet toegestaan!")
    else:
        print("Ongeldige keuze. Kies een nummer tussen 1 en 4.")

# Start het programma
if __name__ == "__main__":
    calculator()
