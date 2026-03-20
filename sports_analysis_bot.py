time_a =input("Digite o primeiro time: ")
time_b =input("Digite o segundo time: ")
gols_a = float(input("Digite a media de gols do time A: "))
gols_b = float(input("Digite a media de gols do time B: "))
escanteios_a = float(input("Digite a media de escanteios do time A: "))
escanteios_b = float(input("Digite a media de escanteios do time B: "))
linha_gols = float(input("Digite a odd gols do jogo: "))
linha_escanteios = float(input("Digite a linha escanteios: "))
jogo = {"time_a": time_a,
        "time_b": time_b,
        "gols_a": gols_a,
        "gols_b": gols_b,
        "escanteios_a": escanteios_a,
        "escanteios_b": escanteios_b,
        "linha_gols": linha_gols,
        "linha_escanteios": linha_escanteios}
media_gols = gols_a + gols_b
media_escanteios = escanteios_a + escanteios_b
diferenca = media_gols - linha_gols
diferenca_2 = media_escanteios - linha_escanteios
# LOGICA GOLS
if diferenca > 1:
    resultado_gols = "Over"
    confianca_gols = "Alta"
elif diferenca > 0.5:
    resultado_gols = "Over"
    confianca_gols = "Média"
elif diferenca < -1:
    resultado_gols = "Under"
    confianca_gols = "Alta"
elif diferenca < -0.5:
    resultado_gols = "Under"
    confianca_gols = "Média"
else:
    resultado_gols = "Evitar"
    confianca_gols = "Baixa"
# LOGICA ESCANTEIOS
if diferenca_2 > 1:
    resultado_escanteios = "Over"
    confianca_escanteios = "Alta"
elif diferenca_2 > 0.5:
    resultado_escanteios = "Over"
    confianca_escanteios = "Média"
elif diferenca_2 < -1:
    resultado_escanteios = "Under"
    confianca_escanteios = "Alta"
elif diferenca_2 < -0.5:
    resultado_escanteios = "Under"
    confianca_escanteios = "Média"
else:
    resultado_escanteios = "Evitar"
    confianca_escanteios = "Baixa"

print("\n--- ANÁLISE DO JOGO ---")
print(f"{time_a} vs {time_b}")

print("\nGOLS:")
print(f"Sugestão: {resultado_gols}")
print(f"Confiança: {confianca_gols}")

print("\nESCANTEIOS:")
print(f"Sugestão: {resultado_escanteios}")
print(f"Confiança: {confianca_escanteios}")

#teste