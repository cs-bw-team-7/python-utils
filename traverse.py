import json
import time
import requests

class Queue():
    def __init__(self):
        self.queue = []
    def enqueue(self, value):
        self.queue.append(value)
    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None
    def size(self):
        return len(self.queue)


class Stack():
    def __init__(self):
        self.stack = []
    
    def push(self, value):
        self.stack.append(value)
    
    def pop(self):
        if self.size() > 0:
            return self.stack.pop()
        else:
            return None
    
    def size(self):
        return len(self.stack)
    
    def __str__(self):
      string = ''
      for item in self.stack:
        string += f'|\t{item}\n'
      return string

# endpoint = "https://t7-api.herokuapp.com/init/"
# response = requests.get(url = endpoint);

# data = response.json()
# print(data)

authorization = "Token 11fbd1ea6bdcc021756643bbeef39d4d5400821e"

headers = {
  'Authorization': authorization,
  'Content-Type': 'application/json',
}


def getCoordString(coords):
  return f'({coords["x"]},{coords["y"]})'


def getCoordDict(string):
  coordArray = string.replace('(', '').replace(')', '').split(',')
  return {
    'x': int(coordArray[0]),
    'y': int(coordArray[1])
  }


def traverse(direction):
  response = {}
  print(f'\n====== Traversing: {direction} ======\n')
  while 'data' not in response:
    endpoint = 'https://t7-api.herokuapp.com/move/'
    body = {
      'direction': direction
    }

    response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
    response = response.json()

    if 'data' not in response:
      print('error: ', response)
      time.sleep(5)
  
  data = response['data']
  time.sleep(data['cooldown'] + 1)
  return data

# prevPath, prevRoom, goal: coordString
def backtrack(path, room, goal):
  reverseDirs = { "n": "s", "e": "w", "s": "n", "w": "e" }
  reversePath = path[::-1]
  goalDict = getCoordDict(goal)

  for reverse in reversePath:
    reverseDirection = reverseDirs[reverse]
    roomCoords = room['coordinates']

    xDiff = goalDict['x'] - roomCoords['x']
    yDiff = goalDict['y'] - roomCoords['y']

    # Check if goal is a neighboring room, XOR to exclude diagonals
    neighbor = abs(xDiff) == 1 ^ abs(yDiff) == 1

    if xDiff == -1:
      direction = "w"
    elif xDiff == 1:
      direction = "e"
    
    if yDiff == -1:
      direction = "s"
    elif yDiff == 1:
      direction = "n"

    # if goal is next to current room + exit that direction, return
    if neighbor and direction in room['exits']:
      # We are at a connected room
      print('\n===== Connected =====\n')
      print(f'BackTracked to: {room["room_id"]}')
      print('\n===== Connected =====\n')
      return room

    # walk path in reverse until goal coords are connected
    print(f'\n===== Backtracking: {reverseDirection} =====\n')
    room = traverse(reverseDirection)
    # need to check valid exit to coords before breaking

  print(f'\n===== BackTracked to: {room["room_id"]} =====\n')
  # We have effectively moved to a connected room
  return room


def getNeighbors(coordinates):
  '''
    Will return a list of neighbor coords e.g. ['(59, 60)', '(60, 61)']
  '''
  neighbors = []

  # North
  nextCoords = {**coordinates}
  nextCoords['y'] += 1
  neighbors.append(getCoordString(nextCoords))

  # East
  nextCoords = {**coordinates}
  nextCoords['x'] += 1
  neighbors.append(getCoordString(nextCoords))

  # South
  nextCoords = {**coordinates}
  nextCoords['y'] -= 1
  neighbors.append(getCoordString(nextCoords))

  # West
  nextCoords = {**coordinates}
  nextCoords['x'] -= 1
  neighbors.append(getCoordString(nextCoords))

  return neighbors


def main():
  # init
  endpoint = "https://t7-api.herokuapp.com/init/"
  response = requests.post(url = endpoint, headers = headers)
  response = response.json()
  room = response['data']
  
  # sleep(cooldown)
  time.sleep(room['cooldown'] + 1)

  tracked = {}
  coordinates = room['coordinates']
  tracked[getCoordString(coordinates)] = True
  visited = {}
  visited[getCoordString(coordinates)] = {**room, "path": []}
  stack = Stack()

  # for each room in this room, push dir on stack (coordinates, direction, path)
  for direction in room['exits']:
    roomData = []
    nextCoords = {**room['coordinates']}

    if direction == 'n':
      nextCoords['y'] += 1
    if direction == 'e':
      nextCoords['x'] += 1
    if direction == 's':
      nextCoords['y'] -= 1
    if direction == 'w':
      nextCoords['x'] -= 1
    
    nextCoordString = getCoordString(nextCoords)
    roomData.append(nextCoordString)
    roomData.append(direction)
    roomData.append([direction])
    stack.push(roomData)
    tracked[nextCoordString] = True
  
  currRoom = room

  # while stack is not empty
  while stack.size() > 0:
    # pop direction off of stack
    prevRoom = stack.pop()  # [coordStr, direction, path]
    prevCoordString = prevRoom[0]
    prevPath = prevRoom[2]
    prevDirection = prevRoom[1]

    # We've visited this room, skip adding to stack to prevent infinite loops
    if prevCoordString in visited:
      continue

    if prevCoordString not in getNeighbors(currRoom['coordinates']):
      currPath = visited[getCoordString(currRoom['coordinates'])]['path']
      # backtrack to neighbor
      currRoom = backtrack(currPath, currRoom, prevCoordString)

    # backtrack here
    # currRoom = backtrack(prevPath, currRoom, prevCoordString)

    # traverse direction to next room
    currRoom = traverse(prevDirection)
    print('\n===== Current Room =====\n')
    print(currRoom['room_id'])
    print('\n===== Current Room =====\n')

    # '{"name":"treasure"}' https://lambda-treasure-hunt.herokuapp.com/api/adv/take/

    for item in currRoom['items']:
      endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/take'
      body = {
        'name': item
      }
      response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
      response = response.json()
      print('item response:', response)
      # data = response['data']

    # Add to visited
    visited[getCoordString(currRoom['coordinates'])] = {**currRoom, "path": prevPath}

    print('\n===== Exits =====\n')
    print(currRoom['exits'])
    print('\n===== Exits =====\n')

    # for each exit in this room
    for direction in currRoom['exits']:
      roomData = []
      nextCoords = {**currRoom['coordinates']}

      if direction == 'n':
        nextCoords['y'] += 1
      if direction == 'e':
        nextCoords['x'] += 1
      if direction == 's':
        nextCoords['y'] -= 1
      if direction == 'w':
        nextCoords['x'] -= 1 

      nextCoordString = getCoordString(nextCoords)
      roomData.append(nextCoordString)
      roomData.append(direction)
      roomData.append([*prevPath, direction])
      
      # print('\n===== Tracked =====\n')
      # print(nextCoordString)
      # print(tracked)
      # print('\n===== Tracked =====\n')

      # if not tracked
      if nextCoordString not in tracked:
        stack.push(roomData)
        tracked[nextCoordString] = True

    print(stack)

if __name__ == "__main__":
  main()