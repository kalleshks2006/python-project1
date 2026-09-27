from heapq import heappush, heappop
from collections import deque

# ECU test states: (Temperature, Voltage, RPM)
tests = [
    (25, 12.0, 1000),
    (40, 12.5, 1500),
    (60, 13.0, 2000),
    (80, 13.5, 3000),
    (100, 14.0, 4000)
]

goal = (80, 13.5, 3000)

def fault(t):
    temp, volt, rpm = t
    return temp > 90 or volt < 11 or volt > 14.5 or rpm > 5000

def bfs():
    q = deque([tests[0]])
    visited = set()
    while q:
        x = q.popleft()
        if x in visited: continue
        visited.add(x)
        if x == goal: return x
        for y in tests:
            if y not in visited:
                q.append(y)

def greedy():
    q = [(0, tests[0])]
    visited = set()
    while q:
        _, x = heappop(q)
        if x in visited: continue
        visited.add(x)
        if x == goal: return x
        for y in tests:
            if y not in visited:
                h = sum(abs(y[i] - goal[i]) for i in range(3))
                heappush(q, (h, y))

def astar():
    q = [(0, tests[0])]
    visited = set()
    while q:
        cost, x = heappop(q)
        if x in visited: continue
        visited.add(x)
        if x == goal: return x
        for y in tests:
            if y not in visited:
                g = cost + 1
                h = sum(abs(y[i] - goal[i]) for i in range(3))
                heappush(q, (g + h, y))

print("AI-Based ECU Validation")
print("-" * 30)

for t in tests:
    print(t, "-> FAULT" if fault(t) else "OK")

print("\nBFS   :", bfs())
print("Greedy:", greedy())
print("A*    :", astar())