import random

def scramble_word(palavra):
   return "".join(random.sample(palavra, len(palavra)))

palavras = ["python", "desenvolvedor", "programação", "desafio"]
palavra = random.choice(palavras)
embaralhado = scramble_word(palavra)

print("Palavra embaralhada:", embaralhada)

tentativas = 3
enquanto tentativas > 0:
   palpite = input("Adivinhe a palavra: ").lower()
   se palpite == palavra:
       print("Correto! ????")
       quebrar
   senão:
       tentativas -= 1
       print(f"Errado! {tentativas} tentativas restantes.")

se tentativas == 0:
   print(f"Fim de jogo! A palavra correta era {palavra}.")