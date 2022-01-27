from smb.SMBConnection import SMBConnection
from pathlib import Path
from datetime import date
import shutil
import os


class ShareFileService():

    def __init__(self, host, root_directory, login=None, password=None, local_name=None, remote_name=None):
        """
            Description paramters for SMBConnection lib


            Create a new SMBConnection instance.

            *username* and *password* are the user credentials required to authenticate the underlying SMB connection with the remote server.
            *password* can be a string or a callable returning a string.
            File operations can only be proceeded after the connection has been authenticated successfully.

            Note that you need to call *connect* method to actually establish the SMB connection to the remote server and perform authentication.

            The default TCP port for most SMB/CIFS servers using NetBIOS over TCP/IP is 139.
            Some newer server installations might also support Direct hosting of SMB over TCP/IP; for these servers, the default TCP port is 445.

            :param string my_name: The local NetBIOS machine name that will identify where this connection is originating from.
                                   You can freely choose a name as long as it contains a maximum of 15 alphanumeric characters and does not contain spaces and any of ``\\/:*?";|+``
            :param string remote_name: The NetBIOS machine name of the remote server.
                                       On windows, you can find out the machine name by right-clicking on the "My Computer" and selecting "Properties".
                                       This parameter must be the same as what has been configured on the remote server, or else the connection will be rejected.
            :param string domain: The network domain. On windows, it is known as the workgroup. Usually, it is safe to leave this parameter as an empty string.
            :param boolean use_ntlm_v2: Indicates whether pysmb should be NTLMv1 or NTLMv2 authentication algorithm for authentication.
                                        The choice of NTLMv1 and NTLMv2 is configured on the remote server, and there is no mechanism to auto-detect which algorithm has been configured.
                                        Hence, we can only "guess" or try both algorithms.
                                        On Sambda, Windows Vista and Windows 7, NTLMv2 is enabled by default. On Windows XP, we can use NTLMv1 before NTLMv2.
            :param int sign_options: Determines whether SMB messages will be signed. Default is *SIGN_WHEN_REQUIRED*.
                                     If *SIGN_WHEN_REQUIRED* (value=2), SMB messages will only be signed when remote server requires signing.
                                     If *SIGN_WHEN_SUPPORTED* (value=1), SMB messages will be signed when remote server supports signing but not requires signing.
                                     If *SIGN_NEVER* (value=0), SMB messages will never be signed regardless of remote server's configurations; access errors will occur if the remote server requires signing.
            :param boolean is_direct_tcp: Controls whether the NetBIOS over TCP/IP (is_direct_tcp=False) or the newer Direct hosting of SMB over TCP/IP (is_direct_tcp=True) will be used for the communication.
                                          The default parameter is False which will use NetBIOS over TCP/IP for wider compatibility (TCP port: 139).
        """

        # Verificar as pastas compartilhadas ou criar, link abaixo mostra como fazer
        # https://www.vivaolinux.com.br/dica/Compartilhamento-simples-e-rapido-de-diretorio-para-outros-computadores

        self.host = host
        self.login = login
        self.password = password
        self.local_name = local_name
        self.remote_name = remote_name
        self.use_authentication = False
        self.root_directory = root_directory

        if login and password:
            self.use_authentication = True
            self.connection = SMBConnection(username=self.login, password=self.password, my_name=local_name, remote_name=remote_name)  # It's net bios  name
            self.connection.connect(ip=self.host.replace("\\\\",""))  # The IP of file server

    def __send_file(self, local_file, remote_directory, filename):
        """ send file with authentication """
        remote_file = os.path.join(remote_directory, filename)
        with open(local_file, "rb") as file:
            self.connection.storeFile(service_name=self.root_directory,  path=remote_file, file_obj=file)
            return True
        return False

    def __copy_file(self, local_file, remote_file):
        """ send file without authentication """
        try:
            shutil.copyfile(local_file, remote_file)
            return True
        except:
            return False

    def share_file(self, local_file, remote_directory, filename):
        full_remote_directory = os.path.join(self.host, self.root_directory, remote_directory)
        print("COPIANDO ARQUIVO:", local_file)
        if self.__verify_directory(full_remote_directory):
            remote_file = os.path.join(full_remote_directory, filename)
            print("PARA:", remote_file)
            if self.use_authentication:
                result = self.__send_file(local_file, remote_directory, filename)
            else:
                result = self.__copy_file(local_file, remote_file)

            if result:
                return True
            else:
                print("Erro! Não foi possivel criar arquivo na pasta do file server")
                return False
        else:
            print("Erro! Não foi possivel criar diretorio no file server")
            return False

    def __verify_directory(self, remote_directory):
        try:
            Path(remote_directory).mkdir(parents=True, exist_ok=True)
            return True

        except Exception as error:
            return False

    def close_connection(self):
        self.connection.close()
        print("Fechando conexão")





##
## EXAMPLE CONFIGURATIONS
##
        
FILE_SERVER = "\\\\192.168.0.26"
FILE_SERVER_ROOT_DIR = "public"
FILE_SERVER_LOGIN = "teste"
FILE_SERVER_PASSWORD = "teste"
FILE_SERVER_LOCAL_NAME = "Diego"  # nome do meu usario na maquina local
FILE_SERVER_REMOTE_NAME = "teste" # nome do usuario no maquina destino
FILE_SERVER_XMLS_DIR = "factor\\cedentes\\[cedente]\\notas_fiscais\\[ano]\\[mes]\\[dia]"
FILE_SERVER_CSVS_DIR = "factor\\cedentes\\[cedente]\\negociacoes\\[ano]\\[mes]\\[dia]"

##
## TEST CONFIGURATIONS
##

#FILE_SERVER = "\\\\crefisa.com.br"
#FILE_SERVER_ROOT_DIR = "root"
#FILE_SERVER_LOGIN = "crefisa\usr_dsc_des"
#FILE_SERVER_PASSWORD = "crefisa\usr_dsc_des"            # nome do meu usario na maquina local
#FILE_SERVER_LOCAL_NAME = "[netbios_name_local]"         # nome do usuario no maquina destino
#FILE_SERVER_REMOTE_NAME = "[netbios_name_remote]"
#FILE_SERVER_XMLS_DIR = "INTERFACE_DES\\DSC_RDL\\NF"
#FILE_SERVER_CSVS_DIR = "GEDDSC_DES\\[ano]\\[mes]\\[dia]"




todays_date = date.today()
year = str(todays_date.year)
month = str(todays_date.month)
day = str(todays_date.day)

if len(month) == 1:
    month = "0"+month
if len(day) == 1:
    day = "0"+day
    
cedente = "12859855750"
filename = "32210406067119000753550010000124561329097173-nfe.xml"
#local_file = os.path.join('media', 'cedentes', cedente, "notas_fiscais", filename)
#local_file = os.path.join("C:\\Users\\Diego\\Desktop\\teste_ftp\\arquivos_testes", filename)
local_file = os.path.join("C:\\Users\\Diego\\Desktop\\teste_ftp\\arquivos_testes", filename)



#remote_directory = os.path.join("factor", "cedentes", cedente, "notas_fiscais", str(year), str(month), str(day))
#remote_directory = os.path.join("GEDDSC_DSC", "cedentes", cedente, "notas_fiscais", str(year), str(month), str(day))
remote_directory = str(FILE_SERVER_XMLS_DIR)
remote_directory = remote_directory.replace("[cedente]", cedente)
remote_directory = remote_directory.replace("[ano]", year)
remote_directory = remote_directory.replace("[mes]", month)
remote_directory = remote_directory.replace("[dia]", day)

file_server = ShareFileService(FILE_SERVER, FILE_SERVER_ROOT_DIR, login=FILE_SERVER_LOGIN, password=FILE_SERVER_PASSWORD, local_name=FILE_SERVER_LOCAL_NAME, remote_name=FILE_SERVER_REMOTE_NAME)
file_server.share_file(local_file=local_file, remote_directory=remote_directory, filename=filename)


























