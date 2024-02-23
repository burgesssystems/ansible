# Installation Requirements

1. Python 3.11.

2. Virtual env created under $HOME/ansible_inventory for Python 3.11:

```
cd $HOME
python3.11 -m venv ansible_inventory
```
3. The following python modules installed:
```
source $HOME/ansible_inventory/bin/activate
pip3 install requests
pip3 install pandas
pip3 install flatten_json
pip3 install Pyarrow
```
4. Download and copy the following files in the repository to your Ansible server:
```
getinventory.py
get_pb_dyn_inventory.sh
```
Both the above files need to be copied to /usr/local/bin on your Ansible controller.

Run the Example Playbook

1. Download the file print_facts.yml and copy to your Ansible controller.

2. Run the playbook - either pass in a hostname or if you have setup Host Groups in CheckMK you can pass in a host group:

/usr/bin/ansible-playbook -i /usr/local/bin/get_pb_dyn_inventory.sh -e target=LMST print_facts.yml
