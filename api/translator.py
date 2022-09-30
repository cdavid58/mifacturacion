class Translator:
	def codificar(self,sms):
		string = sms
		binary_converted = ','.join(format(ord(c), 'b') for c in string)
		return binary_converted

	def decodificar(self,mensaje):
	    numeros = mensaje.split(",")
	    decodificado = ""
	    for numero_binario in numeros:
	        numero_decimal = int(numero_binario, 2)
	        letra = chr(numero_decimal)
	        decodificado += letra
	    return decodificado

t= Translator()

print(t.decodificar('1100001,1100110,1101000,1100001,110001,110000,111001,110101'))