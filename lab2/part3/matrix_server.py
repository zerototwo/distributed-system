from xmlrpc.server import SimpleXMLRPCServer

def multiplyMatrices(A, B):
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    if cols_A != rows_B:  # check dimensions
        return f"Error: cannot multiply, A is {rows_A}x{cols_A}, B is {rows_B}x{cols_B}"
    result = [[0]*cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    return result

server = SimpleXMLRPCServer(("localhost", 8001))
print("Matrix RPC Server running on port 8001...")
server.register_function(multiplyMatrices, "multiplyMatrices")
server.serve_forever()