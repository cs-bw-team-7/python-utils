import time
import requests

# authorization = "Token 11fbd1ea6bdcc021756643bbeef39d4d5400821e"
authorization = "Token ac6e9fac44b48a6974eb8add0a3715184057be52"

headers = {
  'Authorization': authorization,
  'Content-Type': 'application/json',
}

def get_proof():
  response = {}
  while 'proof' not in response:
    endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/'
    response = requests.get(url = endpoint, headers = headers)
    response = response.json()

    if 'proof' not in response:
      print('error getting proof', response)
    
    time.sleep(response['cooldown'])
  return (response['proof'], response['difficulty'])

def read_proof():
  with open('current_proof.txt') as file:
    line = file.readline()
    line = line.replace('(', '').replace(')', '').split(',')
    file_proof = line[0]
    new_proof = float(line[1])
  return file_proof

# proof, difficulty
def write_proof(proof):
  with open('current_proof.txt', 'w+') as file:
    file.write(f"({proof[0]}, {proof[1]})")

if __name__ == "__main__":
  current_proof = get_proof()
  write_proof(current_proof)
  while True:
    file_proof = read_proof()
    print(file_proof, str(current_proof[0]))
    if str(file_proof) == str(current_proof[0]):
      print('sleep')
      time.sleep(3)
    current_proof = get_proof()
    if current_proof != file_proof:
      write_proof(current_proof)
