
class Chair:
    def __init__(self,color,material,height,weight):
        self.color = color
        self.material = material
        self.height = height
        self.weight = weight

    def __str__(self):
        return(f'стул ({chair.color},{chair.material},{chair.height},{chair.weight})')



    def sit (self):
        print('сел на стул')
    def move (self):
        print('передвинул')
    def broke (self):
        print('сломал стул')


chair = Chair('Brown','Wood','100','10')

print(chair.__str__())
chair.sit()
chair.move()
chair.broke()