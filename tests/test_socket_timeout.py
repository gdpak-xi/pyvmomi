import env
import ssl
from pyVim.connect import SmartConnect
from pyVmomi import vim, vmodl, SoapStubAdapter

PropertyCollector = vmodl.query.PropertyCollector
WaitOptions = PropertyCollector.WaitOptions

def _poll(conn, version):
  wait_opts = WaitOptions(maxWaitSeconds=10)
  pc = conn.RetrieveContent().propertyCollector
  result = pc.WaitForUpdatesEx(version, wait_opts)

def host_conn(socket_timeout):
  username, password = "root", "nutanix/4u"
  conn = SmartConnect(host="192.168.5.1",
                      user=username,
                      pwd=password,
                      socketTimeout=socket_timeout)
  _poll(conn, '')

def vcenter_conn(socket_timeout):
  ip_address = "10.1.135.161"
  version = "vim.version.version9"
  cert_file = "/home/nutanix/certs/vcextn.cert"
  cert_key_file = "/home/nutanix/certs/vcextn.key"
  extension_key = "com.nutanix.00055972-bf86-bdfd-0000-00000000444d"
  stub = SoapStubAdapter(host=ip_address, port=80,
                         poolSize=1, connectionPoolTimeout=900,
                         version=version,
                         sslProxyPath="/sdkTunnel",
                         certFile=cert_file,
                         certKeyFile=cert_key_file,
                         socketTimeout=socket_timeout)
  si = vim.ServiceInstance("ServiceInstance", stub)
  session_mgr = si.content.sessionManager
  session_mgr.LoginExtensionByCertificate(extension_key)
  conn = si
  _poll(conn, '')

test_timeout_list = [5, 15, 5, 15]
test_exc_list = [True, False, True, False]
conn_method_list = [host_conn, host_conn, vcenter_conn, vcenter_conn]

index = 1
for timeout, exc, conn_type in zip(test_timeout_list, test_exc_list, conn_method_list):
  print("Test %d:" % index)
  try:
    conn_type(timeout)
    if exc:
      print("\tFAIL")
    else:
      print("\tPASS")
  except ssl.SSLError:
    if exc:
      print("\tPASS:- Socket timeout successful")
    else:
      print("\tFAIL:- Socket timeout.")
  index += 1
