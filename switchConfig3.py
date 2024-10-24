import telnetlib
import getpass
import time
import csv
import pdb

class SwitchTelnet:
    def __init__(self, host, username, password, enable_password):
        self.host = host
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.connection = None
    
    def connect(self):
        try:
            print(f"Estabelecendo conexão Telnet com o switch {self.host}...")
            #pdb.set_trace()
            # Estabelece a conexão Telnet
            self.connection = telnetlib.Telnet(self.host)
            print("Conexão estabelecida. Autenticando...")
            
            # Autenticando usuário
            self.connection.read_until(b"User:")
            self.connection.write(self.username.encode('ascii') + b"\n")
            
            if self.password:
                self.connection.read_until(b"Password:")
                self.connection.write(self.password.encode('ascii') + b"\n")
            
            # Espera o prompt após o login
            time.sleep(1)

            print("Autenticado com sucesso. Entrando no modo privilegiado...")
            #pdb.set_trace()
            self.connection.write(b"en\n")
            print(enable_password)
            time.sleep(2)
            if self.enable_password:
                self.connection.read_until(b"Password:")
                self.connection.write(self.enable_password.encode('ascii') + b"\n")
            
            # Espera o prompt no modo privilegiado
            time.sleep(1)
            print(f"Modo privilegiado ativado no switch {self.host}.")
        
        except Exception as e:
            print(f"Erro ao conectar ou autenticar no switch: {e}")
            return False
        
        return True

    def get_running_config(self):
        try:
            print("Enviando comando para extrair a configuração 'running-config'...")
            # Envia o comando para evitar pausas na saída (comando terminal length 0)
            self.connection.write(b"terminal length 0\n")
            time.sleep(1)

            # Envia o comando show running-config
            self.connection.write(b"show running-config\n")
            
            # Espera a resposta e lê o resultado
            print("Aguardando resposta do switch...")
            time.sleep(10)
            output = self.connection.read_very_eager().decode('ascii')
            print("Configuração extraída com sucesso!")
            return output
        
        except Exception as e:
            print(f"Erro ao coletar a configuração: {e}")
            return None

    def close(self):
        if self.connection:
            print(f"Encerrando conexão com o switch {self.host}...")
            self.connection.write(b"exit\n")
            self.connection.close()
            print(f"Conexão com o switch {self.host} encerrada.")

def process_switches_from_file(file_path):
    try:
        # Abre o arquivo CSV com a lista de switches e suas credenciais
        #pdb.set_trace()
        with open(file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                host = row['ip']
                username = row['username']
                password = row['password']
                enable_password = row['enable_password']
                
                print(f"\nProcessando switch: {host}...")
                # Instancia a classe SwitchTelnet
                switch = SwitchTelnet(host, username, password, enable_password)
                
                # Tenta conectar ao switch
                if switch.connect():
                    config = switch.get_running_config()

                    if config:
                        # Salva a configuração em um arquivo local
                        print(f"Salvando a configuração 'running-config' do switch {host} em config_{host}.txt...")
                        with open(f"config_{host}.txt", "w") as config_file:
                            config_file.write(config)
                        print(f"Configuração 'running-config' do switch {host} salva com sucesso!\n")
                    
                    # Encerra a conexão
                    switch.close()
                else:
                    print(f"Falha ao conectar ao switch {host}.\n")
    
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado.")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    # Solicita o caminho do arquivo CSV contendo a lista de switches
    file_path = input("Digite o caminho do arquivo CSV com os IPs e credenciais dos switches: ")
    
    # Processa os switches a partir do arquivo
    process_switches_from_file(file_path)