import json
import time
import requests

authorization = "Token 11fbd1ea6bdcc021756643bbeef39d4d5400821e"

headers = {
  'Authorization': authorization,
  'Content-Type': 'application/json',
}

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


def getNeighbors(room, path):
  '''
    returns a list of neighbors
    neighbors: [
      { 'coords': '(59, 59)', 'direction': 'n', 'path': ['e', 'n'] },
      { 'coords': '(59, 59)', 'direction': 'n', 'path': ['e', 'n'] }
    ]
  '''
  neighbors = []
  coordinates = room['coordinates']  # coord dictionary
  for direction in room['exits']:
    neighbor = { 'direction': direction, 'path': [*path, direction] }
    neighbor_coords = {**coordinates}

    if direction == 'n':
      neighbor_coords['y'] += 1
    if direction == 'e':
      neighbor_coords['x'] += 1
    if direction == 's':
      neighbor_coords['y'] -= 1
    if direction == 'w':
      neighbor_coords['x'] -= 1
    
    neighbor['coords'] = getCoordString(neighbor_coords)
    neighbors.append(neighbor)
  return neighbors


def getCoordString(coords):
  return f'({coords["x"]},{coords["y"]})'


def getCoordDict(string):
  coordArray = string.replace('(', '').replace(')', '').split(',')
  return {
    'x': int(coordArray[0]),
    'y': int(coordArray[1])
  }


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
  time.sleep(data['cooldown'] + 1)
  return data


def take(item):
  endpoint = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/take'
  body = {
    'name': item
  }
  response = requests.post(url = endpoint, headers = headers, data = json.dumps(body))
  response = response.json()
  if 'data' in response:
    data = response['data']
    time.sleep(data['cooldown'] + 1)
    print('Taken Item', response)
  else:
    time.sleep(15);


def moveToNext(previous, next_room):
  reverse_directions = { 'n': 's', 'e': 'w', 's': 'n', 'w': 'e' }
  reverse_path = previous['path'][::-1]

  # previous is a room object with path, next is a neighbor
  neighborCoords = [neighbor['coords'] for neighbor in getNeighbors(previous, previous['path'])]

  # while it's not a neighbor, backtrack on previous.path
  while next_room['coords'] not in neighborCoords and len(reverse_path) > 0:
    # travel backwards along reversed path
    current_room = traverse(reverse_directions[reverse_path[0]])
    reverse_path = reverse_path[1:]
    current_path = reverse_path[::-1]
    # for each room travelled get neighbors
    neighborCoords = [neighbor['coords'] for neighbor in getNeighbors(current_room, current_path)]

  target_room = traverse(next_room['direction'])
  print(f'\n==== Target Room {target_room["room_id"]} ====\n')
  return target_room


def main():
  # setup initial tracked, visited, stack
  stack = Stack()
  visited = {}
  tracked = set()

  # init
  endpoint = "https://t7-api.herokuapp.com/init/"
  response = requests.post(url = endpoint, headers = headers)
  response = response.json()
  room = response['data']
  
  # sleep(cooldown)
  time.sleep(room['cooldown'] + 1)

  coordString = getCoordString(room['coordinates'])
  tracked.add(coordString)
  # add starting room to visited with an empty path
  visited[coordString] = {**room, "path": []}

  # add initial room data
  neighbors = getNeighbors(room, [])

  # neighbor = { 'coords': '(59, 60)', direction: 'e', path: ['e'] }

  for neighbor in neighbors:
    if neighbor['coords'] not in tracked:
      stack.push(neighbor)  # neighbor format will become next
      tracked.add(neighbor['coords'])
  
  previous_room = visited[coordString]

  # while stack > 0:
  while stack.size() > 0:
    # next = stack.pop
    next_room = stack.pop()  # { coords: '(59, 60)', direction: 'e', path: ['e']}

    # if in visited, skip
    if next_room['coords'] in visited:
      continue

    # curr = moveToNext(prev, next)
    current_room = moveToNext(previous_room, next_room)  # previous_room is a room object, next_room is not
    print(f'\n==== Current Room {current_room["room_id"]} ====\n')
    if current_room["room_id"] == 467:
      exit()
    # current room should now be a room object
    # visited push curr, path will be next_room path because we're now at the next room
    visited[getCoordString(current_room['coordinates'])] = {**current_room, "path": next_room['path']}

    # for item in curr items
    for item in current_room['items']:
      # take(item)
      if "shiny" in item:
        take(item)

    neighbors = getNeighbors(current_room, next_room['path'])
    # for exits in curr
    for neighbor in neighbors:
      # if not tracked
      if neighbor['coords'] not in tracked:
        # stack push room
        stack.push(neighbor)
        # tracked add room coordString
        tracked.add(neighbor['coords'])
    # prev == curr with path
    previous_room = visited[getCoordString(current_room['coordinates'])]
  pass

if __name__ == '__main__':
  main()