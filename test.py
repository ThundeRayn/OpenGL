import copy
#test
base=[1,2,3]
print("self.base=")
print(*base, sep = ", ")
vertices=copy.copy(base)
print("self.vertices=")
print(*vertices, sep = ", ")
print("after setting self.vertices, self.base=")
print(*base, sep = ", ")


face0=[5,2,3]
face1=[1,2,6]
face2=[1,4,3]

weight0=[1,0,0]
weight1=[0,0,1]
weight2=[1,0,1]


faces = [face0,face1,face2]

for x in range(0,3):
    print("------------>> x =" +str(x))
    print("before x, self.vertices=" + str(vertices))
    for i in range(0,len(vertices)):
        print("--> i ="+str(i))
        if i%float(3)==0.0 or i%float(3)==1.0 or i%float(3)==2.0:
                    vertices[i] = vertices[i] + weight2[x]*(faces[x][i]-base[i])
                    print("self.vertices now =" + str(vertices))

print("after for looping,base:")
print(*base, sep = ", ")
print("after for looping,vertices:")
print(*vertices, sep = ", ")
