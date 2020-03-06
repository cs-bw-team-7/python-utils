import sys
import hashlib
import json
import time
import requests
import os
from ls8.cpu import *

authorization = "Token 11fbd1ea6bdcc021756643bbeef39d4d5400821e"

headers = {
  'Authorization': authorization,
  'Content-Type': 'application/json',
}

def proof(last_proof, difficulty):
  proof = 2837.908123
  while valid(last_proof, proof, difficulty) is False:
    proof += 2
  
  return proof


def valid(last_proof, proof, difficulty):
  guess = f'{last_proof}{proof}'.encode()
  guess_hash = hashlib.sha256(guess).hexdigest()

  return guess_hash[:difficulty] == ('0' * difficulty)

def get_proof():
  endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/last_proof/'
  response = requests.get(url = endpoint, headers = headers)
  response = response.json()

  if 'proof' not in response:
    print('error getting proof', response)
  
  time.sleep(response['cooldown'])
  return (response['proof'], response['difficulty'])

def submit_proof(proof):
  endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/mine/'
  body = {
    "proof": proof,
  }
  response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
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

def mine():
  # get last proof
  while True:
    proofData = get_proof()  # (last_proof, difficulty)
    last_proof = proofData[0]
    difficulty = proofData[1]
    print(f'Working on {last_proof} ({difficulty})')
    new_proof = proof(last_proof, difficulty)
    print('submitting: ', new_proof)
    submitted = submit_proof(new_proof)
    if submitted:
      print(new_proof)
      break

def ls8():
  endpoint = "https://lambda-treasure-hunt.herokuapp.com/api/adv/examine/"
  body = {
    "name": "WELL"
  }

  response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
  response = response.json()

  time.sleep(response['cooldown'])

  # get raw program string
  # strip first line
  program = '\n'.join(response['description'].split('\n')[2:])
  cpu = CPU()
  cpu.load(program)
  cpu.run()


def traverse(direction):
  print(f'\n==== Moving {direction} ====\n')
  response = {}
  while 'data' not in response:
    endpoint = 'https://t7-api.herokuapp.com/move/'
    body = {
      'direction': direction
    }

    response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
    response = response.json()

    if 'data' not in response:
      print('error: ', response)
      time.sleep(10)
  
  data = response['data']
  print('sleeping', data['cooldown'])
  print(data['messages'])
  print(data['room_id'])
  time.sleep(data['cooldown'] + 1)
  return data

def dash(direction, number, current):
  print(f'\n==== Dashing {direction} ====\n')
  endpoint = 'https://t7-api.herokuapp.com/roomids/'
  # get number of rooms in direction
  # e.g. 3 east

  coords = []

  for i in range(number):
    if direction == "n":
      current['y'] += 1
    if direction == "e":
      current['x'] += 1
    if direction == "s":
      current['y'] -= 1
    if direction == "w":
      current['x'] -= 1

    coords.append(f'({current["x"]},{current["y"]})')

  body = {
    "coords": coords
  }

  response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
  response = response.json()

  if 'ids' not in response:
    print('error', response)
  
  rooms = response['ids']

  response = {}
  while 'data' not in response:
    # endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/dash/'
    endpoint = 'https://t7-api.herokuapp.com/dash/'
    body = {
      "direction": direction,
      "num_rooms": f'{number}',
      "next_room_ids": ','.join([str(rid) for rid in rooms])
    }

    response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
    response = response.json()
    # data = response['data']
    
    if 'data' not in response:
      print('error: ', response)
      time.sleep(10)
  
  data = response['data']
  print('sleeping', data['cooldown'])
  print(data['messages'])
  time.sleep(data['cooldown'] + 1)
  return data


def get_coin_room():
  # read output.txt
  # split by space
  # return just the last in the array as int
  with open('output.txt') as program:
    instruction = program.readline()
    room_id = int(instruction.split(' ')[-1])

  endpoint = 'https://t7-api.herokuapp.com/room'
  body = {
    "id": room_id
  }
  response = requests.get(url = endpoint, headers = headers, data = json.dumps(body))
  response = response.json()

  if 'coordinates' not in response:
    print('error getting coordinates', response)

  return response['coordinates']

def main(dest):
  # dest = '(55,66)'
  endpoint = 'https://t7-api.herokuapp.com/getPath/'
  body = {
    "destination": dest,
  }
  response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
  response = response.json()

  if 'path' in response:
    path = response['path']
    # path = ['n']
    current = response['coordinates']
    print('\n===============\n')
    print(f'From {current}')
    print(path)
    print('\n===============\n')

    i = 0
    while (i + 1) < len(path):
      dashNum = 0
      while path[i + 1] == path[i]:
        dashNum += 1
        i += 1

        if (i + 1) >= len(path):
          break;
      
      if dashNum > 0:
        number = dashNum + 1
        current = dash(path[i], number, current)['coordinates']
        # print('dashing ', path[i])
        i += 1

        if (i + 1) >= len(path):
          break
      else:
        current = traverse(path[i])['coordinates']
        # print('moving ', path[i]);
        i += 1
        if (i + 1) >= len(path):
          # print('moving ', path[i])
          # traverse(path[i])
          break
    if i < len(path):
      # print('moving ', path[i])
      traverse(path[i])
  else:
    print('error', response)

if __name__ == '__main__':
  # main('(50,58)')  # move to the well
  # main('(63,61)')  # move to the well
  # while True:
  #   stdout_ = sys.stdout #Keep track of the previous value.
  #   sys.stdout = open('output.txt', 'w') # Something here that provides a write method.
  #   ls8()
  #   sys.stdout = stdout_ # restore the previous stdout

  #   next_room = get_coin_room()  # get next coin room
  #   main(next_room)  # move to coin room
    mine()  # mine a coin
    # main('(63,61)')  # move back to the well
