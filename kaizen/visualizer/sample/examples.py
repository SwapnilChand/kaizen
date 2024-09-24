class A:
    def method_a(self):
        return "Method A"

class B:
    def method_b(self, a: A):
        return a.method_a()

class C:
    def method_c(self, b: B):
        return b.method_b(A())