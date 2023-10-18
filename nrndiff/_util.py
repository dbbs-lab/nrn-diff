class Memo(set):
    def visit(self, children):
        for (left, right) in children:
            if left not in self and right not in self:
                yield left, right
            self.add(left)
            self.add(right)
