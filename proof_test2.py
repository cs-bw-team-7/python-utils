import sys
import hashlib
import json
import time
import requests
import os

# authorization = "Token 11fbd1ea6bdcc021756643bbeef39d4d5400821e"
authorization = "Token ac6e9fac44b48a6974eb8add0a3715184057be52"

headers = {
  'Authorization': authorization,
  'Content-Type': 'application/json',
}

def proof(last_proof, difficulty):
  # proof = (time.time() % 1)
  proof = 42424344929699
  while valid(last_proof, proof, difficulty) is False:
    # proof += 0.00000000000000000000000000001
    proof += 0.33
  
  return proof


def valid(last_proof, proof, difficulty):
  guess = f'{last_proof}{proof}'.encode()
  guess_hash = hashlib.sha256(guess).hexdigest()

  return guess_hash[:difficulty] == ('0' * difficulty)

def get_proof():
  response = {}
  while 'proof' not in response:
    endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/'
    response = requests.get(url = endpoint, headers = headers)
    response = response.json()

    if 'proof' not in response:
      print('error getting proof', response)
    
    print('sleeping', response['cooldown'] + 5)
    time.sleep(response['cooldown'] + 5)
  return (response['proof'], response['difficulty'])

def submit_proof(proof):
  endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/'
  body = {
    "proof": f'{proof}',
  }
  print('submit')
  response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
  print('res')
  print(response)
  response = response.json()
  print(response)

  time.sleep(response['cooldown'])

  if 'messages' not in response:
    print(response)
    return False

  if 'New Block Forged' in response['messages']:
    return True
  else:
    return False

def mine(proofData = False):
  # get last proof
  last_proof = proofData[0]
  difficulty = proofData[1]
  
  print(f'Working on {last_proof} ({difficulty})')
  new_proof = proof(last_proof, difficulty)
  return new_proof

# with open('output.txt') as program:
#     instruction = program.readline()
#     room_id = int(instruction.split(' ')[-1])

if __name__ == '__main__':

  current_proof = get_proof()
  while True:
    # Mine current proof
    new_proof = mine(current_proof)
    # Once mined, check current proof again
    update_proof = get_proof()
    # if it's the same write proof to file
    if current_proof[0] == update_proof[0]:
      with open('proof.txt', 'w+') as file:
        file.write(f"({current_proof[0]}, {new_proof})")

      # wait for new proof
      print('waiting for new proof')
      while True:
        time.sleep(8)
        update_proof = get_proof()
        print(f'{current_proof[0] != update_proof[0]} {current_proof[0]}, {update_proof[0]} {type(current_proof[0])}, {type(update_proof[0])}')
        if current_proof[0] != update_proof[0]:
          break

    current_proof = update_proof
  
  # with open('proof.txt') as file:
  #   line = file.readline()
  #   line = line.replace('(', '').replace(')', '').split(',')
  #   last_proof = line[0]
  #   new_proof = float(line[1])
  
  # print(last_proof, new_proof)
    # instruction = program.readline()
    # room_id = int(instruction.split(' ')[-1])