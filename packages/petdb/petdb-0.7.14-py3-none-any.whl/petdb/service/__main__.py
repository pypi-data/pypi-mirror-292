
import os
import sys
import hashlib

from petcmd import Commander

from petdb.service.api import DEFAULT_PORT
from petdb.service.server import run

commander = Commander()

SERVICE_NAME = "petdb.database.{port}.service"
SERVICE_PATH = os.path.join("/etc/systemd/system", SERVICE_NAME)

template = f"""
[Unit]
Description=PetDB Service

[Service]
User={os.environ.get("USER", "root")}
Environment="LD_LIBRARY_PATH=/usr/local/lib"
Environment="PYTHONUNBUFFERED=1"
WorkingDirectory=/var/lib/petdb
ExecStart={sys.executable} -u -m petdb.service run "{{password_hash}}" -P {{port}}
Restart=always

[Install]
WantedBy=multi-user.target
""".strip()

def check_current_configuration(service_path: str) -> bool:
	try:
		with open(service_path, "r") as f:
			executable = f.read().split("ExecStart=")[1].split(" ")[0]
		if executable != sys.executable:
			print(f"PetDB service have already been configured with another python executable: {executable}")
			if input(f"Want to replace it with the current one: {sys.executable} (y/n)? ").lower() != "y":
				return False
	except Exception:
		pass
	return True

@commander.command("init", "reinit")
def init_service(password: str, port: int = DEFAULT_PORT):
	service_name = SERVICE_NAME.format(port=port)
	service_path = SERVICE_PATH.format(port=port)
	if os.path.exists(service_path):
		if not check_current_configuration(service_path):
			return
		os.system(f"sudo systemctl stop {service_name}")
		os.system(f"sudo systemctl disable {service_name}")
		os.remove(service_path)
		os.system(f"sudo systemctl daemon-reload")
	with open(service_path, "w") as f:
		f.write(template.format(password_hash=hashlib.sha256(password.encode("utf-8")).hexdigest(), port=port))
	os.system(f"sudo systemctl daemon-reload")
	os.system(f"sudo systemctl enable {service_name}")
	os.system(f"sudo systemctl start {service_name}")

@commander.command("run")
def run_service(password_hash: str, port: int):
	run(password_hash=password_hash, port=port)

if __name__ == "__main__":
	commander.process()
