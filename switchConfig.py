import telnetlib
import getpass
import time

class SwitchTelnet:
    def __init__(self, host, username, password, enable_password):
        self.host = host
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.connection = None
    
    def connect(self):
        try:
            # Estabelece a conexão Telnet
            self.connection = telnetlib.Telnet(self.host)
            self.connection.read_until(b"Username: ")
            self.connection.write(self.username.encode('ascii') + b"\n")
            
            if self.password:
                self.connection.read_until(b"Password: ")
                self.connection.write(self.password.encode('ascii') + b"\n")

            # Espera o prompt após o login
            time.sleep(1)
            self.connection.write(b"enable\n")
            self.connection.read_until(b"Password: ")
            self.connection.write(self.enable_password.encode('ascii') + b"\n")
            
            # Espera o prompt no modo privilegiado
            time.sleep(1)
            print(f"Conectado ao switch {self.host}")
        
        except Exception as e:
            print(f"Erro ao conectar: {e}")
    
    def get_running_config(self):
        try:
            # Envia o comando para extrair a configuração running-config
            self.connection.write(b"terminal length 0\n")  # Para evitar pausas na saída
            time.sleep(1)
            self.connection.write(b"show running-config\n")
            
            # Espera a resposta e lê o resultado
            time.sleep(3)
            output = self.connection.read_very_eager().decode('ascii')
            return output
        
        except Exception as e:
            print(f"Erro ao coletar configuração: {e}")
    
    def close(self):
        if self.connection:
            self.connection.write(b"exit\n")
            self.connection.close()
            print(f"Conexão com o switch {self.host} encerrada")

if __name__ == "__main__":
    # Exemplo de uso
    host = input("Digite o IP do switch: ")
    username = input("Digite o usuário: ")
    password = getpass.getpass("Digite a senha: ")
    enable_password = getpass.getpass("Digite a senha enable: ")

    switch = SwitchTelnet(host, username, password, enable_password)
    
    switch.connect()
    config = switch.get_running_config()
    
    if config:
        # Salva a configuração em um arquivo local
        with open(f"config_{host}.txt", "w") as config_file:
            config_file.write(config)
        print(f"Configuração running-config salva em config_{host}.txt")
    
    switch.close()
