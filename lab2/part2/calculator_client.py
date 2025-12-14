import Pyro4

# Define remote functions
def add(x, y): return x + y
def subtract(x, y): return x - y
def multiply(x, y): return x * y
def divide(x, y): return "Error: Division by zero" if y == 0 else x / y

# Start Pyro server and register functions
daemon = Pyro4.Daemon()
uri_add = daemon.register(add)
uri_sub = daemon.register(subtract)
uri_mul = daemon.register(multiply)
uri_div = daemon.register(divide)

print("URIs:\n add:", uri_add, "\n sub:", uri_sub, "\n mul:", uri_mul, "\n div:", uri_div)
daemon.requestLoop()